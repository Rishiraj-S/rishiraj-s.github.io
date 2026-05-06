# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Previewing the Site

No build system. Open files directly in a browser, or serve locally:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

Project pages use relative paths (`../assets/`) — they must be served from a server root, not opened as `file://` paths, to avoid broken asset links.

## Architecture

Static site deployed via GitHub Pages. No framework, no build step, no package manager.

**Template base:** BootstrapMade iPortfolio — vendor libraries are bundled under `assets/vendor/` (Bootstrap 5, AOS, Swiper, GLightbox, Typed.js, PureCounter, Isotope, Waypoints). Do not install or update these via npm; edit the bundled files in place if needed.

**Page structure:**

- `index.html` — single-page portfolio with anchor-linked sections: `#hero`, `#about`, `#resume`, `#extracurriculars`, `#portfolio`, `#certifications`, `#contact`
- `projects/*.html` — individual project detail pages; use `body class="portfolio-details-page"` and reference assets via `../assets/`
- `thank-you.html` — contact form redirect target
- `projects/voronoi_tool.html` — standalone interactive tool with its own inline CSS/JS, not using the shared template

**Styling:**

- Global CSS variables (colors, fonts) defined at the top of [assets/css/main.css](assets/css/main.css) — change accent color (`--accent-color: #0e8fc9`) here to retheme
- Dark sidebar uses `.dark-background` class; light content sections use `.light-background`

**Adding a new project page:**

1. Copy an existing `projects/*.html` as a template
2. Add a card to the `#portfolio` section in `index.html` with matching filter tags
3. Place screenshots under `assets/img/portfolio/<project-name>/`
