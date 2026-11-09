#!/usr/bin/env python3
"""Site checks for this static GitHub Pages portfolio. Standard library only.

    python3 scripts/check-site.py              # check the site, exit 1 on any error
    python3 scripts/check-site.py --self-test  # prove each check catches what it should

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
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_SCHEMES = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//|#|\$\{|\{\{)", re.I)
ASSET_STRING = re.compile(r"""["']([^"'\s<>()]+/[^"'\s<>()]+\.(?:png|jpe?g|webp|gif|svg|json|jsonl|csv|parquet|css|js|ico|mp4|webm))["']""")
CSS_URL = re.compile(r"""url\(\s*["']?([^"')]+)["']?\s*\)""")
KEBAB = re.compile(r"^[a-z0-9][a-z0-9.-]*$")
NAMING_EXEMPT = ("README.md", "CLAUDE.md")
MB = 1024 * 1024


class Page(HTMLParser):
    """Collects what the checks need from one HTML file."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs, self.ids, self.dup_ids, self.missing_alt = [], set(), set(), []
        self.lang = self.title = self.viewport = False
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

    for rel in files:
        if rel.endswith(".css"):
            with open(os.path.join(root, rel), encoding="utf-8") as fh:
                for ref in CSS_URL.findall(fh.read()):
                    r = resolve(rel, ref)
                    if r and not exists_exact(root, r[0]):
                        errors.append(f"{rel}: broken url(\"{ref}\")")
        name = rel.rsplit("/", 1)[-1]
        if not re.match(r"^tools/[^/]+/data/", rel) and name not in NAMING_EXEMPT and not all(KEBAB.match(s) for s in rel.split("/")):
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


def self_test():
    """Build a tiny site with one planted fault per check and assert each is reported."""
    good_head = '<html lang="en"><head><title>t</title><meta name="viewport" content="x"></head>'
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
    }
    expected = [
        "anchor \"#nope\"", "broken reference \"assets/Logo.png\"", "broken reference \"assets/missing.png\"",
        "<img src=\"assets/a.jpg\"> has no alt", "unpublished path \"_sources/raw.jpg\"", "anchor \"sub/#gone\"",
        "sub/index.html: missing <html lang>, <title>, viewport meta", "duplicate id \"d\"",
        "assets/a.jpg: image carries EXIF", "assets/Bad_Name.css: not lowercase kebab-case", "broken url(\"gone.png\")",
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
    print(f"self-test passed: {len(expected)} planted faults caught, no false positives")


def main():
    if "--self-test" in sys.argv:
        self_test()
        return 0
    errors, warnings, n_pages, n_files = check(ROOT)
    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error: {e}")
    print(f"\n{n_pages} pages, {n_files} published files: {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
