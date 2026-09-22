# Video Intelligence Engine (VIE) — Public Demonstration

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![DuckDB](https://img.shields.io/badge/duckdb-1.0+-yellow.svg)](https://duckdb.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.39+-red.svg)](https://vie-video-intelligence-demo.streamlit.app/)
[![Status](https://img.shields.io/badge/Mode-100%25%20Offline%20%2F%20Zero--API-success.svg)]()

English | [Português](README.pt-BR.md)

> An interactive demonstration of the **Video Intelligence Engine (VIE)**: an end-to-end data pipeline converting short-form video into structured, queryable multimodal Creative Intelligence.

This repository provides an autonomous, **100% offline demonstration** of VIE's analytical layer, dimensional schema, and interactive dashboard using **DuckDB** and **Streamlit**.

🔗 **[Access Online Demo](https://vie-video-intelligence-demo.streamlit.app/)** | 📦 **[Core Engine Code](https://github.com/TStryder/vie-video-intelligence-engine)**

---

## Architecture Overview

```text
               PUBLIC SHORT-FORM VIDEO DATASET (N=10)
                                 │
     ┌───────────────────────────┴───────────────────────────┐
     ▼                                                       ▼
data/features.parquet                               data/performance.parquet
(55 columns: Physical facts,                        (Longitudinal time-series snapshots:
 AI observations, semantic interpretations)          views, likes, comments, engagement)
     │                                                       │
     └───────────────────────────┬───────────────────────────┘
                                 │
                                 ▼
                     DUCKDB IN-MEMORY ENGINE
                   (src/analytics.py: SQL views,
                    UNNEST multi-label, window joins)
                                 │
                                 ▼
                   STREAMLIT INTERACTIVE DASHBOARD
                             (app.py)
        ├── Tab 1: Overview & Descriptive Metrics
        ├── Tab 2: Creative Inspector & Keyframe Gallery
        └── Tab 3: Performance Insights & Longitudinal Trends
```

---

## Dataset & Technical Scope

The demonstration dataset comprises **10 real short-form videos** processed through the full VIE V3 pipeline:
- **Physical Facts (`measurements`)**: Deterministic metrics computed via Python (FFprobe, PySceneDetect, Whisper) — cuts per second, words per minute, speech ratio, duration.
- **Multimodal Observations (`observations`)**: Visual features (webcam presence, split screen, center captions, faces, products) and audio presence.
- **Cognitive Interpretations (`interpretations`)**: Primary hook mechanisms, narrative structures, rhetorical devices, and calls to action with temporal evidence citations.
- **Keyframes**: Extracted JPEG frames mapped to scene transitions and cited evidence items.
- **Observed Outcomes (`performance`)**: Longitudinal public performance snapshots collected via `yt-dlp`.

---

## Methodological Disclaimer

> [!NOTE]
> 1. **Observational Demonstration Sample**: The included dataset is a small, non-probabilistic sample ($N = 10$) collected from publicly accessible YouTube Shorts. It serves exclusively to demonstrate computational feasibility, data modeling, and analytical workflows.
> 2. **No Causal Claims**: Correlations and performance patterns shown in the dashboard represent observational descriptive statistics. This demonstration makes no causal claims regarding platform recommendation algorithms.
> 3. **Third-Party Content**: Original high-resolution video streams and full audio files are not redistributed. All creator branding, titles, and public channel handles belong to their respective copyright holders.

---

## Quickstart

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/your-username/vie-video-intelligence-demo.git
cd vie-video-intelligence-demo

python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Launch the Streamlit Dashboard
```bash
streamlit run app.py
```
The application will start locally at `http://localhost:8501`.

### 3. Run the Test Suite
```bash
pytest tests/ -v
```

---

## Dashboard Walkthrough

- **Tab 1: 📊 Panorama da Base & Métricas**: Executive metrics overview (averages of WPM, cut cadence, speech ratio, total view volume) and integrated tabular view.
- **Tab 2: 🔍 Creative Inspector & Keyframes**: In-depth inspection per video showing technical parameters, sensory observations, cited temporal evidence with timestamps, and visual keyframe gallery.
- **Tab 3: 📈 Performance & Insights Cruzados**: Cross-analysis of hook mechanisms, pacing correlation, and longitudinal view evolution over time.

---

🔗 Upstream Engine
This demo is powered by the extraction pipeline developed in the core engine:
👉 [TStryder/vie-video-intelligence-engine](https://github.com/tstryder/vie-video-intelligence)
