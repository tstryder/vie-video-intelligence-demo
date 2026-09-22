# Video Intelligence Engine (VIE) — Demonstração Pública

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![DuckDB](https://img.shields.io/badge/duckdb-1.0+-yellow.svg)](https://duckdb.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.39+-red.svg)](https://vie-video-intelligence-demo.streamlit.app/)
[![Status](https://img.shields.io/badge/Mode-100%25%20Offline%20%2F%20Zero--API-success.svg)]()

[English](README.md) | Português

> Demonstração interativa do **Video Intelligence Engine (VIE)**: pipeline analítico multimodal que converte vídeos curtos em Creative Intelligence estruturada e consultável via SQL.

Este repositório fornece uma demonstração **100% autônoma e offline** da camada analítica, do schema dimensional e do dashboard interativo do VIE utilizando **DuckDB** e **Streamlit**.

🔗 **[Acessar Demo Online](https://vie-video-intelligence-demo.streamlit.app/)** | 📦 **[Código do Motor Principal](https://github.com/TStryder/vie-video-intelligence-engine)**

---

## Visão Geral da Arquitetura

```text
               DATASET PÚBLICO DE VÍDEOS CURTOS (N=10)
                                 │
     ┌───────────────────────────┴───────────────────────────┐
     ▼                                                       ▼
data/features.parquet                               data/performance.parquet
(55 colunas: Fatos físicos,                         (Snapshots temporais longitudinais:
 observações da IA, interpretações semânticas)       views, likes, comentários, engajamento)
     │                                                       │
     └───────────────────────────┬───────────────────────────┘
                                 │
                                 ▼
                     MOTOR ANALÍTICO DUCKDB
                   (src/analytics.py: views SQL,
                    UNNEST multi-label, temporal joins)
                                 │
                                 ▼
                   DASHBOARD INTERATIVO STREAMLIT
                             (app.py)
        ├── Aba 1: Panorama da Base & Métricas Descritivas
        ├── Aba 2: Creative Inspector & Galeria de Keyframes
        └── Aba 3: Insights de Performance & Séries Temporais
```

---

## Dataset e Escopo Técnico

O dataset da demonstração é composto por **10 vídeos reais** processados integralmente pelo pipeline VIE V3:
- **Fatos Físicos (`measurements`)**: Métricas determinísticas calculadas via Python (FFprobe, PySceneDetect, Whisper) — cortes por segundo, palavras por minuto, cadência de fala, duração.
- **Observações Multimodais (`observations`)**: Elementos visuais (presença de webcam, tela dividida, legendas dinâmicas, detecção facial, produtos) e áudio.
- **Interpretações Cognitivas (`interpretations`)**: Mecanismos de gancho primário, arcos narrativos, recursos retóricos e chamadas para ação com citação de evidências temporais.
- **Keyframes**: Quadros JPEG extraídos nas transições de corte e amarrados aos nós de evidência.
- **Performance Observada (`performance`)**: Snapshots públicos longitudinais de engajamento capturados via `yt-dlp`.

---

## Aviso Metodológico

> [!NOTE]
> 1. **Amostra Observacional Demonstrativa**: O dataset fornecido é uma amostra não-probabilística restrita ($N = 10$) derivada de publicações públicas no YouTube Shorts. Destina-se exclusivamente a demonstrar viabilidade computacional, modelagem dimensional e consultas analíticas.
> 2. **Ausência de Causalidade**: As correlações e padrões de desempenho exibidos refletem observações pontuais descritivas. O projeto não infere relações de causa e efeito sobre os algoritmos das plataformas.
> 3. **Conteúdo de Terceiros**: Mídias originais completas (.mp4/.wav) não são redistribuídas. As marcas, títulos e identificadores dos criadores pertencem aos respectivos detentores de direitos.

---

## Como Executar

### 1. Clonar e Instalar Dependências
```bash
git clone https://github.com/seu-usuario/vie-video-intelligence-demo.git
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
O dashboard será aberto em seu navegador no endereço `http://localhost:8501`.

### 3. Executar os Testes Automatizados
```bash
pytest tests/ -v
```

---

## Estrutura das Abas do Dashboard

- **Aba 1: 📊 Panorama da Base & Métricas**: Métricas médias (WPM, cortes/s, ratio de fala, volume de views) e tabela consolidada de fatos e performance.
- **Aba 2: 🔍 Creative Inspector & Keyframes**: Inspeção detalhada de cada vídeo, exibindo ficha técnica, diagnósticos sensoriais, evidências citadas amarradas a timestamps e galeria visual dos keyframes.
- **Aba 3: 📈 Performance & Insights Cruzados**: Análise multi-label de ganchos via SQL DuckDB, correlação de dinamismo nos primeiros 3 segundos e série temporal de snapshots.

---

🔗 Upstream Engine
Esta demonstração é impulsionada pelo pipeline de extração desenvolvido no motor principal:
👉 [TStryder/vie-video-intelligence-engine](https://github.com/tstryder/vie-video-intelligence)
