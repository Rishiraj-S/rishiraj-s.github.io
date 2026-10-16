# Rishiraj Sinharay — Portfolio Website

Personal portfolio website for **Rishiraj Sinharay**, a Data Scientist and Sports Analytics professional based in Barcelona, Spain.

Live site: [rishiraj-s.github.io](https://rishiraj-s.github.io)

---

## About

This portfolio showcases professional experience, education, and projects across data science, machine learning, generative AI, and sports analytics. Built as a static site deployed via GitHub Pages.

---

## Featured Projects

| Project | Domain | Stack |
|---|---|---|
| [GenAI Market Intelligence Dashboard](projects/genai-dashboard/) | GenAI / LLM | Python, LLaMA-3.3-70B, FAISS, Streamlit |
| [OCR-to-LLM Microservice](projects/news-summarizer/) | GenAI / NLP | Rails 8, AWS Textract, Anthropic Claude |
| [Player Scouting Dashboard](projects/player-scouting-dashboard/) | Sports Analytics | Python, Streamlit, Radar Charts |
| [Football Event Tagger](tools/event-tagger/) | Sports Analytics | HTML, JavaScript, MediaRecorder API |
| [3D Tracking Data Visualizer](tools/3d-tracking-viewer/) | Sports Analytics | JavaScript, Three.js, D3-Delaunay |
| [Voronoi Pitch Mapping Tool](tools/voronoi-pitch-mapper/) | Sports Analytics | JavaScript, OpenCV.js, D3-Delaunay |
| [Bayer Leverkusen Bundesliga Analysis](projects/bayer-leverkusen/) | Sports Analytics | Python, StatsBomb, mplsoccer |
| [Leicester City PL Title Analysis](projects/leicester-city/) | Sports Analytics | Python, pandas, matplotlib |
| [Aitana Bonmatí World Cup Analysis](projects/aitana-bonmati/) | Sports Analytics | Python, StatsBomb |
| [MDS Minor Thesis — Breast Cancer ML](projects/monash-minor-thesis/) | Machine Learning | Python, scikit-learn |
| [Spotify Data Visualisation](projects/spotify-data-viz/) | Data Viz | R, ggplot2 |

---

## Tech Stack

- **Languages**: Python, SQL, R, JavaScript
- **ML / AI**: scikit-learn, LLaMA, Claude (Anthropic), FAISS (RAG)
- **Data Engineering**: Selenium, BeautifulSoup, SerpAPI, SAP BODS, Apache Hadoop
- **Visualisation**: Streamlit, Power BI, mplsoccer, matplotlib, Three.js, D3
- **Cloud**: AWS (Textract, S3), Microsoft Azure
- **Web**: HTML5, CSS3, JavaScript

---

## Repository Structure

```
rishiraj-s.github.io/
├── index.html                  # Single-page portfolio (home)
├── thank-you.html              # Contact form redirect target
├── projects/                   # Case-study pages, one folder per project
│   └── <slug>/
│       ├── index.html          # Served at /projects/<slug>/
│       └── images/             # Screenshots used by this project only
├── tools/                      # Standalone interactive apps (own inline CSS/JS)
│   ├── 3d-tracking-viewer/     # + data/ (tracking JSON/JSONL) + football-pitch.png
│   ├── 3d-goal-simulation/     # Unlisted; + data/ (source parquet)
│   ├── event-tagger/
│   └── voronoi-pitch-mapper/
└── assets/                     # Site-wide only
    ├── css/main.css            # Custom styles (CSS variables for theming)
    ├── js/main.js              # Tab routing, keyboard navigation, filters
    └── img/                    # Profile photo, favicons
```

Each project/tool folder also holds the `cover` image used for its card on the home page.
Naming: lowercase kebab-case for all folders and files.

---

## Local Development

No build system — open files directly or serve locally:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

> Pages use relative paths (`../../assets/`) and must be served from a server root, not opened as `file://` paths.

---

## Contact

- **Email**: rishiraj1998.rs@gmail.com
- **LinkedIn**: [linkedin.com/in/rishirajsinharay](https://www.linkedin.com/in/rishirajsinharay/)
- **GitHub**: [github.com/Rishiraj-S](https://github.com/Rishiraj-S)
- **Medium**: [medium.com/@rishiraj1998.rs](https://medium.com/@rishiraj1998.rs)
