# Rishiraj Sinharay — Portfolio Website

Personal portfolio of **Rishiraj Sinharay**, Research Engineer at the Barcelona Supercomputing Center, working across data engineering, machine learning and sports analytics.

Live site: [rishiraj-s.github.io](https://rishiraj-s.github.io)

---

## About

A static site deployed via GitHub Pages, designed like a football game's main menu: Q/E tabs, tiles you move between with the arrow keys, a yellow focus frame and a controller-prompt bar. The colours come from FC Barcelona's 2025–26 home kit, kept minimal.

Tabs: **Home** (photo, about, career, a slideshow of sports project highlights), **Projects** (filterable by Sports, GenAI and Research), **Tools**, **Career** (transfer history and academy), **Trophies** (certifications and a photo gallery) and **Contact**.

---

## Projects

| Project | Area | Stack |
|---|---|---|
| [CuléVision: game analysis tool for FC Barcelona](projects/culevision/) (master's thesis) | Sports, 2026 | Python, Plotly Dash, XGBoost, SHAP, mplsoccer, Selenium Wire, Docker, Google Cloud Run |
| [Real Madrid player load forecasting (ACWR)](projects/real-madrid-internship/) | Sports, 2026 | Python, XGBoost, scikit-learn, pandas, Streamlit |
| [Player Scouting Dashboard](projects/player-scouting-dashboard/) | Sports, 2025 | Python, pandas, Plotly, Streamlit |
| [Aitana Bonmatí at the 2023 World Cup](projects/aitana-bonmati/) | Sports, 2025 | Python, StatsBomb, mplsoccer |
| [Leicester City's 5000-to-1 title](projects/leicester-city/) | Sports, 2025 | Python, StatsBomb, mplsoccer |
| [Bayer Leverkusen's unbeaten Bundesliga season](projects/bayer-leverkusen/) | Sports, 2025 | Python, StatsBomb, mplsoccer |
| [GenAI Market Intelligence Dashboard](projects/genai-dashboard/) | GenAI, 2025 | Python, LLaMA-3.3-70B, FAISS, Streamlit |
| [News Summarisation and Hindi Text-to-Speech](projects/news-summarizer/) | GenAI, 2025 | Python, Hugging Face, Streamlit |
| [Predictive biomarkers for FGFR therapy (MDS minor thesis)](projects/monash-minor-thesis/) | Research, 2023 | Python, scikit-learn |
| [Spotify Streaming Data Analysis](projects/spotify-data-viz/) | Research, 2022 | R, ggplot2 |

## Tools

| Tool | What it does | Stack |
|---|---|---|
| [3D tracking viewer](tools/3d-tracking-viewer/) | Replays tracking data on a 3D pitch with Voronoi regions | JavaScript, Three.js, D3-Delaunay |
| [Event tagger](tools/event-tagger/) | Tag match events on video, export to Excel or a highlight cut | HTML, JavaScript, MediaRecorder API |
| [Voronoi pitch mapper](tools/voronoi-pitch-mapper/) | Map players from a broadcast frame onto a pitch | JavaScript, OpenCV.js, D3-Delaunay |

---

## Repository Structure

```
rishiraj-s.github.io/
├── index.html                  # Menu hub: Home, Projects, Tools, Career, Trophies, Contact
├── thank-you.html              # Contact form redirect target
├── projects/                   # Case-study pages, one folder per project
│   └── <slug>/
│       ├── index.html          # Served at /projects/<slug>/
│       └── images/             # WebP screenshots and the card cover, this project only
├── tools/                      # Standalone interactive apps (own inline CSS/JS) + cover.webp
│   ├── 3d-tracking-viewer/     # + data/ (tracking JSON/JSONL) + football-pitch.png
│   ├── 3d-goal-simulation/     # Unlisted; + data/ (source parquet)
│   ├── event-tagger/
│   └── voronoi-pitch-mapper/
├── scripts/check-site.py       # Site checks (also run in CI)
├── _sources/                   # Full-size originals; versioned, not published (Jekyll skips _ folders)
│   ├── photos/                 # Profile and gallery photos
│   ├── logos/                  # Employer logos
│   ├── projects/               # Original project screenshots and posters
│   └── tools/                  # Original tool covers
└── assets/                     # Site-wide only
    ├── css/main.css            # Styles; design tokens (kit colours, font, radii) at the top
    ├── js/main.js              # Tab routing, keyboard navigation, filters, slideshows
    └── img/
        ├── favicon.ico, favicon.png
        ├── profile/            # Photos of me used on the site
        ├── clubs/              # Employer badges, 128px square WebP
        └── gallery/            # Trophies photo wall
```

Published images are WebP, at most 1,600px on the long edge, with metadata stripped. The full-size originals live in `_sources/`, mirroring the published path, and are never linked from a page.
Naming: lowercase kebab-case for all folders and files.

---

## Local Development

No build system. Open files directly or serve locally:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

> Pages use relative paths (`../../assets/`) and must be served from a server root, not opened as `file://` paths.

---

## Checks

`python3 scripts/check-site.py` checks everything GitHub Pages publishes: local links and assets resolve (case-sensitive), tab/anchor targets exist, pages have a title, language and viewport, every image has alt text, file names are kebab-case, published images carry no EXIF metadata, no file nears GitHub's size limits, and the site JavaScript parses. It runs on every push and pull request via GitHub Actions. `--self-test` proves each check still catches the fault it is for.

---

## Contact

Use the contact form on the [site](https://rishiraj-s.github.io/#contact), or find me on:

- **LinkedIn**: [linkedin.com/in/rishirajsinharay](https://www.linkedin.com/in/rishirajsinharay/)
- **GitHub**: [github.com/Rishiraj-S](https://github.com/Rishiraj-S)
- **Medium**: [medium.com/@rishiraj1998.rs](https://medium.com/@rishiraj1998.rs)
