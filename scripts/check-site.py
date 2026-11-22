#!/usr/bin/env python3
"""Site checks for this static GitHub Pages portfolio. Standard library only.

    python3 scripts/check-site.py              # check the site, exit 1 on any error
    python3 scripts/check-site.py --self-test  # prove each check catches what it should
    python3 scripts/check-site.py --external   # outside links still resolve (network; weekly in CI)

Checks what GitHub Pages publishes (Jekyll skips paths starting with "." or "_"):
  links    every local src/href/srcset/url() and quoted asset path in inline JS
           resolves, with exact case (Pages is case-sensitive)
  anchors  "#id" and "page.html#id" targets exist (tabs <-> panel ids)
  private  no page links into unpublished paths such as _sources/
  html     each page has <html lang>, <title>, a viewport meta, unique ids,
           and an alt attribute on every <img>
  naming   lowercase kebab-case file names (data files under tools/*/data/ exempt)
  metadata no EXIF in published JPEG/PNG/WebP images (location, camera data)
  size     files over 100 MB fail (GitHub rejects them), over 50 MB warn
  js       `node --check` on assets/js/*.js when node is installed
  seo      indexable pages (not redirects, not noindex) have a meta description and an
           og:image; absolute links to this site (og:image, og:url, canonical) point at
           real files; sitemap.xml lists exactly the indexable pages
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_SCHEMES = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//|#|\$\{|\{\{)", re.I)
ASSET_STRING = re.compile(r"""["']([^"'\s<>()]+/[^"'\s<>()]+\.(?:png|jpe?g|webp|gif|svg|json|jsonl|csv|parquet|css|js|ico|mp4|webm))["']""")
CSS_URL = re.compile(r"""url\(\s*["']?([^"')]+)["']?\s*\)""")
KEBAB = re.compile(r"^[a-z0-9][a-z0-9.-]*$")
NAMING_EXEMPT = ("README.md", "CLAUDE.md")
MB = 1024 * 1024
SITE = "https://rishiraj-s.github.io/"


class Page(HTMLParser):
    """Collects what the checks need from one HTML file."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs, self.ids, self.dup_ids, self.missing_alt = [], set(), set(), []
        self.lang = self.title = self.viewport = False
        self.redirect = self.noindex = False
        self.meta, self.own_urls = {}, []
        self.scripts, self._in_script = [], False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            (self.dup_ids if a["id"] in self.ids else self.ids).add(a["id"])
        if tag == "html" and a.get("lang"):
            self.lang = True
        if tag == "title":
            self.title = True
        if tag == "meta" and a.get("name") == "viewport":
            self.viewport = True
        if tag == "meta" and (a.get("http-equiv") or "").lower() == "refresh":
            self.redirect = True
        if tag == "meta" and (a.get("name") or a.get("property")) and a.get("content") is not None:
            key = a.get("name") or a.get("property")
            self.meta[key] = a["content"]
            if key == "robots" and "noindex" in a["content"]:
                self.noindex = True
            if key in ("og:image", "og:url"):
                self.own_urls.append(a["content"])
        if tag == "link" and a.get("rel") == "canonical" and a.get("href"):
            self.own_urls.append(a["href"])
        if tag == "img" and "alt" not in a:
            self.missing_alt.append(a.get("src", "?"))
        for key in ("src", "href", "poster", "data"):
            if a.get(key):
                self.refs.append(a[key].strip())
        if a.get("srcset"):
            self.refs += [part.split()[0] for part in a["srcset"].split(",") if part.strip()]
        if a.get("style"):
            self.refs += CSS_URL.findall(a["style"])
        self._in_script = tag in ("script", "style")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._in_script = False

    def handle_data(self, data):
        if self._in_script:
            self.scripts.append(data)


def published_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith((".", "_")))
        for f in sorted(filenames):
            if not f.startswith((".", "_")):
                yield os.path.relpath(os.path.join(dirpath, f), root).replace(os.sep, "/")


def exists_exact(root, rel):
    """True only if every path segment matches on disk with exact case."""
    cur = root
    for seg in rel.split("/"):
        if not os.path.isdir(cur) or seg not in os.listdir(cur):
            return False
        cur = os.path.join(cur, seg)
    return True


def resolve(page_rel, ref):
    """Map a reference to (repo-relative path, fragment), or None for external/dynamic refs."""
    if not ref or SKIP_SCHEMES.match(ref) and not ref.startswith("#"):
        return None
    path, _, frag = ref.partition("#")
    path = path.split("?")[0]
    if not path:
        return page_rel, frag
    base = "" if path.startswith("/") else os.path.dirname(page_rel)
    target = os.path.normpath(os.path.join(base, path.lstrip("/"))).replace(os.sep, "/")
    if path.endswith("/") or target == ".":
        target = (target.rstrip("/.") + "/index.html").lstrip("/")
    return target, frag


def has_exif(path):
    with open(path, "rb") as fh:
        head = fh.read(256 * 1024)
    ext = path.lower().rsplit(".", 1)[-1]
    if ext in ("jpg", "jpeg"):
        return b"Exif\x00\x00" in head
    if ext == "png":
        return b"eXIf" in head
    if ext == "webp":
        return b"EXIF" in head[:64 * 1024]
    return False


def check(root):
    errors, warnings = [], []
    files = list(published_files(root))
    pages = {}
    for rel in files:
        if rel.endswith(".html"):
            p = Page()
            with open(os.path.join(root, rel), encoding="utf-8") as fh:
                p.feed(fh.read())
            pages[rel] = p

    for rel, p in pages.items():
        missing = [name for name, ok in (("<html lang>", p.lang), ("<title>", p.title), ("viewport meta", p.viewport)) if not ok]
        if missing:
            errors.append(f"{rel}: missing {', '.join(missing)}")
        for i in sorted(p.dup_ids):
            errors.append(f"{rel}: duplicate id \"{i}\"")
        for src in p.missing_alt:
            errors.append(f"{rel}: <img src=\"{src}\"> has no alt attribute (use alt=\"\" if decorative)")

        refs = p.refs + [m for s in p.scripts for m in ASSET_STRING.findall(s)] + [m for s in p.scripts for m in CSS_URL.findall(s)]
        for ref in refs:
            r = resolve(rel, ref)
            if r is None:
                continue
            target, frag = r
            if target.startswith(("_", ".")) or "/_" in "/" + target or "/." in "/" + target:
                errors.append(f"{rel}: links to unpublished path \"{ref}\"")
            elif not exists_exact(root, target):
                errors.append(f"{rel}: broken reference \"{ref}\" (no {target})")
            elif frag and target.endswith(".html") and target in pages and frag not in pages[target].ids:
                errors.append(f"{rel}: anchor \"{ref}\" has no element with id=\"{frag}\" in {target}")

    def page_url(rel):
        return SITE + ("" if rel == "index.html" else rel[: -len("index.html")] if rel.endswith("/index.html") else rel)

    indexable = {rel for rel, p in pages.items() if not p.redirect and not p.noindex}
    for rel in sorted(indexable):
        p = pages[rel]
        missing = [k for k, label in (("description", "meta description"), ("og:image", "og:image")) if not p.meta.get(k)]
        if missing:
            errors.append(f"{rel}: indexable page missing {', '.join(missing)}")
    for rel, p in pages.items():
        for url in p.own_urls:
            if url.startswith(SITE):
                local = url[len(SITE):]
                local = (local + "index.html") if local.endswith("/") or not local else local
                if not exists_exact(root, local):
                    errors.append(f"{rel}: {url} points to a missing file")

    sitemap = os.path.join(root, "sitemap.xml")
    if os.path.exists(sitemap):
        with open(sitemap, encoding="utf-8") as fh:
            listed = set(re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", fh.read()))
        wanted = {page_url(rel) for rel in indexable}
        for url in sorted(listed - wanted):
            errors.append(f"sitemap.xml lists {url}, which is not an indexable page")
        for url in sorted(wanted - listed):
            errors.append(f"sitemap.xml is missing indexable page {url}")

    for rel in files:
        if rel.endswith(".css"):
            with open(os.path.join(root, rel), encoding="utf-8") as fh:
                for ref in CSS_URL.findall(fh.read()):
                    r = resolve(rel, ref)
                    if r and not exists_exact(root, r[0]):
                        errors.append(f"{rel}: broken url(\"{ref}\")")
        name = rel.rsplit("/", 1)[-1]
        legacy_redirect = rel in pages and pages[rel].redirect   # old URLs from the pre-2026 site keep their names
        if not re.match(r"^tools/[^/]+/data/", rel) and name not in NAMING_EXEMPT and not legacy_redirect and not all(KEBAB.match(s) for s in rel.split("/")):
            errors.append(f"{rel}: not lowercase kebab-case")
        if rel.lower().endswith((".jpg", ".jpeg", ".png", ".webp")) and has_exif(os.path.join(root, rel)):
            errors.append(f"{rel}: image carries EXIF metadata; re-export it stripped")
        size = os.path.getsize(os.path.join(root, rel))
        if size > 100 * MB:
            errors.append(f"{rel}: {size // MB} MB, over GitHub's 100 MB file limit")
        elif size > 50 * MB:
            warnings.append(f"{rel}: {size // MB} MB, over GitHub's 50 MB warning size")

    js = [f for f in files if f.startswith("assets/js/") and f.endswith(".js")]
    node = shutil.which("node")
    if node:
        for f in js:
            res = subprocess.run([node, "--check", os.path.join(root, f)], capture_output=True, text=True)
            if res.returncode:
                errors.append(f"{f}: JavaScript syntax error\n{res.stderr.strip()}")
    elif js:
        warnings.append("node not installed: skipped JavaScript syntax check")
    return errors, warnings, len(pages), len(files)


BLOCKED = {401, 403, 429, 999}   # sites that refuse bots (LinkedIn, Medium): reported, not failed
SKIP_HOSTS = ("fonts.googleapis.com", "fonts.gstatic.com")


def classify(status):
    """ok / blocked / broken for an HTTP status (None = no response at all)."""
    if status is not None and 200 <= status < 400:
        return "ok"
    return "blocked" if status in BLOCKED else "broken"


def fetch_status(url):
    for method in ("HEAD", "GET"):   # some servers reject HEAD
        req = urllib.request.Request(url, method=method, headers={"User-Agent": "Mozilla/5.0 (compatible; portfolio-link-check)"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.status
        except urllib.error.HTTPError as e:
            status = e.code
            if method == "GET" or status not in (403, 405, 501):
                return status
        except Exception:
            if method == "GET":
                return None
    return None


def check_external(root):
    """Every outside http(s) link on the site still resolves."""
    urls = set()
    for rel in published_files(root):
        if rel.endswith(".html"):
            p = Page()
            with open(os.path.join(root, rel), encoding="utf-8") as fh:
                p.feed(fh.read())
            if p.redirect:
                continue
            urls |= {u for u in p.refs if u.startswith(("http://", "https://")) and not u.startswith(SITE)
                     and not any(h in u for h in SKIP_HOSTS)}
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = dict(zip(sorted(urls), pool.map(fetch_status, sorted(urls))))
    errors, warnings = [], []
    for url, status in results.items():
        verdict = classify(status)
        if verdict == "broken":
            errors.append(f"{url}: {status or 'no response'}")
        elif verdict == "blocked":
            warnings.append(f"{url}: {status} (site blocks automated checks; check by hand)")
    return errors, warnings, len(results)


def self_test():
    """Build a tiny site with one planted fault per check and assert each is reported."""
    good_head = ('<html lang="en"><head><title>t</title><meta name="viewport" content="x"><meta name="description" content="d">'
                 '<meta property="og:image" content="https://rishiraj-s.github.io/og.jpg"></head>')
    site = {
        "index.html": good_head + '<body><nav><a href="#ok">ok</a><a href="#nope">x</a></nav><section id="ok"></section>'
                      '<img src="assets/Logo.png" alt=""><img src="assets/missing.png" alt=""><img src="assets/a.jpg">'
                      '<a href="_sources/raw.jpg">raw</a><a href="sub/">sub</a><a href="sub/#gone">gone</a>'
                      '<a href="https://example.com">ext</a><a href="mailto:a@b.c">mail</a></body></html>',
        "sub/index.html": '<html><head></head><body><p id="d"></p><p id="d"></p></body></html>',
        "assets/logo.png": b"\x89PNG\r\n\x1a\n",
        "assets/a.jpg": b"\xff\xd8\xff\xe1\x00\x10Exif\x00\x00",
        "assets/Bad_Name.css": "body{background:url(gone.png)}",
        "assets/js/ok.js": "const a = 1;",
        "assets/js/bad.js": "const = ;",
        "_sources/raw.jpg": b"raw",
        "tools/x/data/Provider_File.json": "{}",
        "og.jpg": b"\xff\xd8\xff",
        "card/index.html": good_head.replace("og.jpg", "nope.jpg") + "<body></body></html>",
        "private/index.html": good_head.replace('<meta name="description" content="d">', '<meta name="robots" content="noindex">')
                              .replace('<meta property="og:image" content="https://rishiraj-s.github.io/og.jpg">', "") + "<body></body></html>",
        "sitemap.xml": "<urlset><url><loc>https://rishiraj-s.github.io/</loc></url><url><loc>https://rishiraj-s.github.io/card/</loc></url>"
                       "<url><loc>https://rishiraj-s.github.io/gone/</loc></url></urlset>",
        "old_page.html": good_head.replace("</head>", '<meta http-equiv="refresh" content="0; url=sub/"></head>') + '<body><a href="sub/">moved</a></body></html>',   # legacy redirect: name exempt
    }
    expected = [
        "anchor \"#nope\"", "broken reference \"assets/Logo.png\"", "broken reference \"assets/missing.png\"",
        "<img src=\"assets/a.jpg\"> has no alt", "unpublished path \"_sources/raw.jpg\"", "anchor \"sub/#gone\"",
        "sub/index.html: missing <html lang>, <title>, viewport meta", "duplicate id \"d\"",
        "assets/a.jpg: image carries EXIF", "assets/Bad_Name.css: not lowercase kebab-case", "broken url(\"gone.png\")",
        "sub/index.html: indexable page missing description, og:image",
        "card/index.html: https://rishiraj-s.github.io/nope.jpg points to a missing file",
        "sitemap.xml lists https://rishiraj-s.github.io/gone/, which is not an indexable page",
        "sitemap.xml is missing indexable page https://rishiraj-s.github.io/sub/",
    ]
    if shutil.which("node"):
        expected.append("assets/js/bad.js: JavaScript syntax error")
    with tempfile.TemporaryDirectory() as tmp:
        for rel, body in site.items():
            path = os.path.join(tmp, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as fh:
                fh.write(body if isinstance(body, bytes) else body.encode())
        errors, _, _, _ = check(tmp)
    report = "\n".join(errors)
    missed = [e for e in expected if e not in report]
    assert not missed, "self-test: these faults were not reported:\n  " + "\n  ".join(missed) + "\n\nreported:\n" + report
    false_hits = [e for e in errors if not any(x in e for x in expected)]
    assert not false_hits, "self-test: unexpected errors (false positives):\n  " + "\n  ".join(false_hits)
    assert [classify(c) for c in (200, 301, 403, 999, 429, 404, 500, None)] == ["ok", "ok", "blocked", "blocked", "blocked", "broken", "broken", "broken"]
    print(f"self-test passed: {len(expected)} planted faults caught, no false positives; link classification ok")


def main():
    if "--self-test" in sys.argv:
        self_test()
        return 0
    if "--external" in sys.argv:
        errors, warnings, n = check_external(ROOT)
        for w in warnings:
            print(f"warning: {w}")
        for e in errors:
            print(f"error: {e}")
        print(f"\n{n} outside links: {len(errors)} broken, {len(warnings)} blocked")
        return 1 if errors else 0
    errors, warnings, n_pages, n_files = check(ROOT)
    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error: {e}")
    print(f"\n{n_pages} pages, {n_files} published files: {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
