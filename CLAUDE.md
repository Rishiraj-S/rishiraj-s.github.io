# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Previewing the Site

No build system. Open files directly in a browser, or serve locally:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

Project/tool pages use relative paths (`../../assets/`) — they must be served from a server root, not opened as `file://` paths, to avoid broken asset links.

## Architecture

Static site deployed via GitHub Pages. No framework, no build step, no package manager.

**Design:** "matchday hub" theme modelled on a football game's main menu (EAFC-style tiles, Q/E tabs, gold focus frame, button-prompt bar). Hand-written CSS/JS, no CSS framework or vendor libraries. Font: Saira (Google Fonts, variable `wdth` axis for condensed display type).

**Page structure:**

- `index.html` — menu hub with hash-routed panels: `#home` (tile grid), `#projects` (filterable), `#tools`, `#career` (bio, transfer history + certifications, academy), `#contact` (formsubmit.co form). Without JS all panels render stacked.
- `projects/<slug>/index.html` — project case-study pages (clean URLs `/projects/<slug>/`); "match report" layout (gallery strip, article, facts sidebar), reference shared assets via `../../assets/` and own screenshots via `images/`
- `tools/<slug>/index.html` — standalone interactive apps with their own inline CSS/JS, not using the shared template: `voronoi-pitch-mapper`, `event-tagger`, `3d-tracking-viewer` (loads `data/` and `football-pitch.png` from its own folder), `3d-goal-simulation` (unlisted)
- `thank-you.html` — contact form redirect target
- `assets/` — site-wide files only: css, js, `img/profile/` (photos of the owner), `img/clubs/` (employer badges), favicons
- `_sources/` — full-res originals (`photos/`, `logos/`) that site images are exported from; GitHub Pages' Jekyll build skips `_` folders, so they are versioned but not published. Export web copies as WebP with metadata stripped, never link `_sources/` from a page
- Naming: lowercase kebab-case everywhere (GitHub Pages is case-sensitive)

**Styling and behaviour:**

- Design tokens (colours, font, radii) at the top of [assets/css/main.css](assets/css/main.css); gold `--gold` is reserved for focus, ratings and primary actions
- [assets/js/main.js](assets/js/main.js): panel routing, Q/E tab switching, arrow-key focus between `.tile`s, project filters (`data-tags`), Esc follows the `[data-back]` link on sub-pages
- Home hub layout is CSS `grid-template-areas` (`.a-feat`, `.a-card`, ...), with tablet/mobile variants in the media queries

**Adding a new project page:**

1. Copy an existing `projects/<slug>/` folder as a template
2. Add a `.tile` to `#project-grid` in `index.html` linking to `projects/<slug>/`, with `data-tags` (`sports`, `genai`, `research`)
3. Put screenshots in `projects/<slug>/images/`
