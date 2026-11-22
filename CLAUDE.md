# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Previewing the Site

No build system. Open files directly in a browser, or serve locally:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

Project/tool pages use relative paths (`../../assets/`) — they must be served from a server root, not opened as `file://` paths, to avoid broken asset links.

## Checks

Run before every commit; CI (`.github/workflows/checks.yml`) runs the same on every push and PR:

```bash
python3 scripts/check-site.py              # links, anchors, html basics, naming, EXIF, file sizes, JS syntax
python3 scripts/check-site.py --self-test  # proves each check catches a planted fault
```

Standard library only. When adding a new kind of check, add a planted fault for it to `self_test()`.

## Architecture

Static site deployed via GitHub Pages. No framework, no build step, no package manager.

**Design:** "matchday hub" theme modelled on a football game's main menu (EAFC-style tiles, Q/E tabs, gold focus frame, button-prompt bar). Hand-written CSS/JS, no CSS framework or vendor libraries. Font: Saira (Google Fonts, variable `wdth` axis for condensed display type).

**Page structure:**

- `index.html` — menu hub with hash-routed panels: `#home` (tile grid), `#projects` (filterable), `#tools`, `#career` (transfer history, academy), `#trophies` (certifications), `#contact` (formsubmit.co form). Without JS all panels render stacked.
- `projects/<slug>/index.html` — project case-study pages (clean URLs `/projects/<slug>/`); "match report" layout (gallery strip, article, facts sidebar), reference shared assets via `../../assets/` and own screenshots via `images/`
- `tools/<slug>/index.html` — standalone interactive apps with their own inline CSS/JS, not using the shared template: `voronoi-pitch-mapper`, `event-tagger`, `3d-tracking-viewer` (loads `data/` and `football-pitch.png` from its own folder; tracking data is gzipped `.jsonl.gz`, decompressed in the browser while streaming), `3d-goal-simulation` (unlisted). Each ends with an inline-styled fixed '← Portfolio' link back to `index.html#tools` and the site favicon
- `thank-you.html` — contact form redirect target (noindex)
- `404.html` — themed not-found page; GitHub serves it for any missing path at any depth, so its links are root-absolute
- `projects/*.html` (flat files, e.g. `leicester_city.html`) — redirect pages for the pre-2026 URLs; they keep their old non-kebab names on purpose (the checker exempts pages with a meta refresh). `main.js` also maps old section anchors (`#portfolio`, `#resume`, ...) to the new tabs
- `sitemap.xml`, `robots.txt` — list every project and tool page; update both `<lastmod>` and the URL list when pages are added
- `_config.yml` — keeps `README.md`, `CLAUDE.md` and `scripts/` off the published site
- `assets/` — site-wide files only: css, js, `img/profile/` (photos of the owner), `img/clubs/` (employer badges), `img/gallery/` (Trophies photo wall), favicons
- `_sources/` — full-res originals (`photos/`, `logos/`) that site images are exported from; GitHub Pages' Jekyll build skips `_` folders, so they are versioned but not published. Export web copies as WebP with metadata stripped, never link `_sources/` from a page
- Naming: lowercase kebab-case everywhere (GitHub Pages is case-sensitive)

**Styling and behaviour:**

- Design tokens (colours, font, radii) at the top of [assets/css/main.css](assets/css/main.css). Colours are FC Barcelona's 2025–26 home kit (`--blue-void`, `--loyal-blue`, `--game-royal`, `--deep-garnet`, `--noble-red`, `--cardinal-red`, `--mineral-yellow`); use them through the semantic tokens (`--tunnel*`, `--chalk`, `--gold`). `--gold` (mineral yellow) is reserved for focus, ratings and primary actions
- [assets/js/main.js](assets/js/main.js): panel routing, Q/E tab switching, arrow-key focus between `.tile`s, project filters (`data-tags`), Esc follows the `[data-back]` link on sub-pages
- Home hub layout is CSS `grid-template-areas` (`.a-feat`, `.a-card`, ...), with tablet/mobile variants in the media queries

**Adding a new project page:**

1. Copy an existing `projects/<slug>/` folder as a template
2. Add a `.tile` to `#project-grid` in `index.html` linking to `projects/<slug>/`, with `data-tags` (`sports`, `genai`, `research`)
3. Put screenshots in `projects/<slug>/images/` (WebP, metadata stripped, with width/height on every `<img>`)
4. Make `projects/<slug>/og.jpg`: 1200x630 JPEG, the first screenshot fitted whole on `#0a0e29`; update the page's description, canonical and `og:*` tags (absolute `https://rishiraj-s.github.io/...` URLs)
5. Add the page to `sitemap.xml`, then run `python3 scripts/check-site.py`
