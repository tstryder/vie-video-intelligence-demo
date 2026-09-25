# Video Intelligence Engine (VIE) - Multimodal Video Analytics

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![DuckDB](https://img.shields.io/badge/duckdb-1.0+-yellow.svg)](https://duckdb.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.39+-red.svg)](https://vie-video-intelligence-demo.streamlit.app/)
[![Status](https://img.shields.io/badge/Mode-100%25%20Offline%20%2F%20Zero--API-success.svg)]()

[English](README.md) | Português

> Uma demonstração interativa do **Video Intelligence Engine (VIE)**: um pipeline de dados end-to-end que transforma vídeos curtos em Creative Intelligence multimodal estruturada e consultável.

Este repositório fornece uma demonstração autônoma e **100% offline** da camada analítica, do schema dimensional e do dashboard interativo do VIE utilizando **DuckDB** e **Streamlit**.

🔗 **[Acessar Demo Online](https://vie-video-intelligence-demo.streamlit.app/)** | 📦 **[Código do Motor Principal](https://github.com/TStryder/vie-video-intelligence-engine)**

---

## Visão Geral da Arquitetura

```text
               DATASET PÚBLICO DE VÍDEOS CURTOS (N=10)
                                 │
     ┌───────────────────────────┴───────────────────────────┐
     ▼                                                       ▼
data/features.parquet                               data/performance.parquet
(55 colunas: fatos físicos,                         (Snapshots longitudinais:
 observações da IA, interpretações                    views, likes, comentários, engajamento)
 semânticas)
     │                                                       │
     └───────────────────────────┬───────────────────────────┘
                                 │
                                 ▼
                     MOTOR DUCKDB EM MEMÓRIA
                   (src/analytics.py: views SQL,
                    UNNEST multi-label, window joins)
                                 │
                                 ▼
                   DASHBOARD INTERATIVO STREAMLIT
                             (app.py)
        ├── Aba 1: Panorama & Métricas Descritivas
        ├── Aba 2: Creative Inspector & Galeria de Keyframes
        └── Aba 3: Insights de Performance & Tendências Longitudinais
```

---

## Dataset & Escopo Técnico

O dataset da demonstração é composto por **10 vídeos curtos reais** processados pelo pipeline VIE V3 completo:

* **Fatos Físicos (`measurements`)**: Métricas determinísticas calculadas via Python (FFprobe, PySceneDetect, Whisper) - cortes por segundo, palavras por minuto, proporção de fala e duração.
* **Observações Multimodais (`observations`)**: Características visuais (presença de webcam, tela dividida, legendas centrais, rostos, produtos) e presença de áudio.
* **Interpretações Cognitivas (`interpretations`)**: Mecanismos de gancho primário, estruturas narrativas, recursos retóricos e chamadas para ação com citações de evidências temporais.
* **Keyframes**: Quadros JPEG extraídos e associados às transições de cena e aos itens de evidência citados.
* **Resultados Observados (`performance`)**: Snapshots longitudinais de performance pública coletados via `yt-dlp`.

---

## Aviso Metodológico

> [!NOTE]
>
> 1. **Amostra Observacional Demonstrativa**: O dataset incluído é uma amostra pequena e não probabilística ($N = 10$), coletada a partir de YouTube Shorts publicamente acessíveis. Seu objetivo exclusivo é demonstrar viabilidade computacional, modelagem de dados e workflows analíticos.
> 2. **Sem Inferências Causais**: As correlações e os padrões de performance apresentados no dashboard representam estatísticas descritivas observacionais. Esta demonstração não estabelece relações causais sobre os algoritmos de recomendação das plataformas.
> 3. **Conteúdo de Terceiros**: Streams de vídeo originais em alta resolução e arquivos de áudio completos não são redistribuídos. Toda marca, título e identificação pública dos criadores pertence aos respectivos detentores dos direitos autorais.

---

## Quickstart

### 1. Clonar & Instalar Dependências

```bash
git clone https://github.com/tstryder/vie-video-intelligence-demo.git
cd vie-video-intelligence-demo

python -m venv .venv
# No Windows:
.venv\Scripts\activate
# No Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Iniciar o Dashboard Streamlit

```bash
streamlit run app.py
```

A aplicação será iniciada localmente em `http://localhost:8501`.

### 3. Executar a Suíte de Testes

```bash
pytest tests/ -v
```

---

## Visão Geral do Dashboard

* **Aba 1: 📊 Panorama & Métricas**: Visão geral das principais métricas (médias de WPM, cadência de cortes, proporção de fala, volume total de visualizações) e visão tabular integrada.
* **Aba 2: 🔍 Creative Inspector & Keyframes**: Inspeção detalhada por vídeo, apresentando parâmetros técnicos, observações sensoriais, evidências temporais citadas com timestamps e galeria visual de keyframes.
* **Aba 3: 📈 Insights de Performance & Análise Cruzada**: Análise cruzada dos mecanismos de gancho, correlações de ritmo e evolução longitudinal das visualizações ao longo do tempo.

---

## Motor Principal

Esta demonstração é alimentada pelo pipeline de extração desenvolvido no motor principal:

👉 [TStryder/vie-video-intelligence-engine](https://github.com/TStryder/vie-video-intelligence-engine)
