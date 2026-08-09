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
| [GenAI Market Intelligence Dashboard](projects/genai_dashboard.html) | GenAI / LLM | Python, LLaMA-3.3-70B, FAISS, Streamlit |
| [OCR-to-LLM Microservice](projects/news_summarizer.html) | GenAI / NLP | Rails 8, AWS Textract, Anthropic Claude |
| [Player Scouting Dashboard](projects/player_scouting_dashboard.html) | Sports Analytics | Python, Streamlit, Radar Charts |
| [Football Event Tagger](projects/event_tagger.html) | Sports Analytics | HTML, JavaScript, MediaRecorder API |
| [3D Tracking Data Visualizer](projects/3d.html) | Sports Analytics | JavaScript, Three.js, D3-Delaunay |
| [Voronoi Pitch Mapping Tool](projects/voronoi_tool.html) | Sports Analytics | JavaScript, OpenCV.js, D3-Delaunay |
| [Bayer Leverkusen Bundesliga Analysis](projects/bayer_leverkusen.html) | Sports Analytics | Python, StatsBomb, mplsoccer |
| [Leicester City PL Title Analysis](projects/leicester_city.html) | Sports Analytics | Python, pandas, matplotlib |
| [Aitana Bonmatí World Cup Analysis](projects/aitana_bonmati.html) | Sports Analytics | Python, StatsBomb |
| [MDS Minor Thesis — Breast Cancer ML](projects/monash-minor-thesis.html) | Machine Learning | Python, scikit-learn |
| [Spotify Data Visualisation](projects/data-viz-project.html) | Data Viz | R, ggplot2 |

---

## Tech Stack

- **Languages**: Python, SQL, R, JavaScript
- **ML / AI**: scikit-learn, LLaMA, Claude (Anthropic), FAISS (RAG)
- **Data Engineering**: Selenium, BeautifulSoup, SerpAPI, SAP BODS, Apache Hadoop
- **Visualisation**: Streamlit, Power BI, mplsoccer, matplotlib, Three.js, D3
- **Cloud**: AWS (Textract, S3), Microsoft Azure
- **Web**: HTML5, CSS3, Bootstrap 5, JavaScript

---

## Repository Structure

```
rishiraj-s.github.io/
├── index.html                  # Main single-page portfolio
├── thank-you.html              # Contact form redirect
├── projects/                   # Individual project pages and tools
│   ├── aitana_bonmati.html
│   ├── bayer_leverkusen.html
│   ├── data-viz-project.html
│   ├── event_tagger.html
│   ├── genai_dashboard.html
│   ├── leicester_city.html
│   ├── monash-minor-thesis.html
│   ├── news_summarizer.html
│   ├── player_scouting_dashboard.html
│   ├── voronoi_tool.html
│   ├── 3d.html
│   └── data/                   # Tracking data used by 3d.html
└── assets/
    ├── css/main.css            # Custom styles (CSS variables for theming)
    ├── js/main.js              # Custom scripts
    ├── img/                    # Images and portfolio media
    │   ├── portfolio/          # Project screenshots by category
    │   │   ├── class_projects/
    │   │   ├── dell/
    │   │   ├── genai/
    │   │   ├── monash_data_viz_project/
    │   │   ├── monash_minor_thesis/
    │   │   ├── scouting_dashboard/
    │   │   └── sports/
    │   └── football-pitch.png  # Default pitch image for 3D visualizer
    └── vendor/                 # Bundled third-party libraries
        ├── bootstrap/
        ├── bootstrap-icons/
        ├── aos/
        ├── swiper/
        ├── glightbox/
        ├── isotope-layout/
        ├── typed.js/
        └── waypoints/
```

---

## Local Development

No build system — open files directly or serve locally:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

> Project pages use relative paths (`../assets/`) and must be served from a server root, not opened as `file://` paths.

---

## Contact

- **Email**: rishiraj1998.rs@gmail.com
- **LinkedIn**: [linkedin.com/in/rishirajsinharay](https://www.linkedin.com/in/rishirajsinharay/)
- **GitHub**: [github.com/Rishiraj-S](https://github.com/Rishiraj-S)
- **Medium**: [medium.com/@rishiraj1998.rs](https://medium.com/@rishiraj1998.rs)
