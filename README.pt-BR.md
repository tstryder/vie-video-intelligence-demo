# Video Intelligence Engine (VIE) — Multimodal Video Analytics

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![DuckDB](https://img.shields.io/badge/duckdb-1.0+-yellow.svg)](https://duckdb.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.39+-red.svg)](https://vie-video-intelligence-demo.streamlit.app/)
[![Status](https://img.shields.io/badge/Mode-100%25%20Offline%20%2F%20Zero--API-success.svg)]()

[English](README.md) | Português

> Demonstração pública da camada analítica do **Video Intelligence Engine (VIE)**, um sistema multimodal que transforma sinais de vídeo, áudio e análise semântica em dados estruturados e consultáveis.

Este repositório demonstra a **camada analítica e de visualização** do VIE utilizando dados previamente processados pelo pipeline de extração.

A demonstração é **100% autônoma e offline**: não requer chaves de API, inferência de LLM ou processamento de vídeo durante a execução.

🔗 **[Acessar Demo Online](https://vie-video-intelligence-demo.streamlit.app/)** | 📦 **[Código do Motor Principal](https://github.com/TStryder/vie-video-intelligence-engine)**

---

## Visão Geral da Arquitetura

O pipeline completo do VIE separa extração, validação e análise. Este repositório público demonstra principalmente a camada final de análise.

```text
                         VIE CORE ENGINE
                              │
                              ▼
                  PROCESSAMENTO DE VÍDEO/ÁUDIO
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
        SINAIS DETERMINÍSTICOS       ANÁLISE MULTIMODAL
        FFprobe / PySceneDetect      Gemini / Whisper
                 │                         │
                 └────────────┬────────────┘
                              ▼
                    DADOS ESTRUTURADOS
                     + EVIDÊNCIAS TEMPORAIS
                              │
                              ▼
                    features.parquet
                              │
                              ▼
                    ┌─────────────────┐
                    │     DuckDB      │
                    │ Camada Analítica│
                    └────────┬────────┘
                             │
                             ▼
                    DASHBOARD STREAMLIT
                             │
             ┌───────────────┼────────────────┐
             ▼               ▼                ▼
          Overview      Creative Inspector   Performance
```

O **VIE Engine** realiza a extração e transformação dos dados. Este repositório contém um dataset já processado e demonstra como esses dados podem ser consultados, correlacionados e explorados sem executar novamente o pipeline de IA.

---

## Dataset e Escopo Técnico

O dataset da demonstração é composto por **10 vídeos reais** processados pelo pipeline VIE V3.

### Fatos físicos (`measurements`)

Métricas determinísticas calculadas a partir do conteúdo de vídeo e áudio utilizando ferramentas como:

* FFprobe
* PySceneDetect
* Whisper
* Python

Exemplos:

* duração do vídeo
* cortes por segundo
* palavras por minuto (WPM)
* cadência de fala
* duração de segmentos

### Observações multimodais (`observations`)

Características identificadas a partir da análise visual e de áudio, incluindo:

* presença de webcam
* tela dividida
* legendas dinâmicas
* detecção facial
* presença de produtos
* características de áudio

### Interpretações semânticas (`interpretations`)

Estruturas derivadas da análise multimodal, incluindo:

* mecanismos de gancho
* arcos narrativos
* recursos retóricos
* chamadas para ação
* evidências temporais associadas às interpretações

### Keyframes

Quadros JPEG extraídos em pontos relevantes do vídeo e associados aos nós de evidência correspondentes.

### Performance observada (`performance`)

Snapshots longitudinais de métricas públicas de desempenho, incluindo:

* views
* likes
* comentários
* métricas derivadas de engajamento

Os snapshots foram coletados a partir de dados públicos utilizando `yt-dlp`.

---

## Camada Analítica

Os dados são armazenados em **Parquet** e consultados através do **DuckDB**.

A camada analítica demonstra:

* consultas SQL sobre dados estruturados;
* normalização de campos multi-label com `UNNEST`;
* cruzamento entre características criativas e performance;
* joins temporais entre snapshots;
* agregações e métricas descritivas;
* exploração dos dados sem executar novamente o modelo de IA.

Isso permite separar a etapa computacionalmente mais pesada de **extração/inferência** da etapa de **análise exploratória e consulta**.

---

## Aviso Metodológico

> [!NOTE]
> **Amostra observacional demonstrativa:** o dataset é uma amostra não probabilística restrita ($N = 10$) derivada de publicações públicas no YouTube Shorts. Seu objetivo é demonstrar processamento, modelagem dimensional e análise de dados, não produzir conclusões estatísticas generalizáveis.
>
> **Ausência de causalidade:** as relações apresentadas no dashboard são observacionais e descritivas. O projeto não estabelece relações de causa e efeito entre características dos vídeos e desempenho nas plataformas.
>
> **Conteúdo de terceiros:** os arquivos de mídia originais (`.mp4`/`.wav`) não são redistribuídos neste repositório. Marcas, títulos, vídeos e identificadores de criadores pertencem aos respectivos detentores de direitos.

---

## Como Executar

### 1. Clonar o repositório

```bash
git clone https://github.com/TStryder/vie-video-intelligence-demo.git
cd vie-video-intelligence-demo
```

### 2. Criar o ambiente virtual

```bash
python -m venv .venv
```

No Windows:

```bash
.venv\Scripts\activate
```

No Linux/macOS:

```bash
source .venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Iniciar o dashboard

```bash
streamlit run app.py
```

O dashboard estará disponível em:

```text
http://localhost:8501
```

### 5. Executar os testes

```bash
pytest tests/ -v
```

---

## Estrutura das Abas do Dashboard

### 📊 Panorama da Base & Métricas

Visão geral do dataset com métricas descritivas como:

* WPM
* cortes por segundo
* proporção de fala
* views
* métricas de performance

Também apresenta uma tabela consolidada combinando características dos vídeos e dados observados de performance.

### 🔍 Creative Inspector & Keyframes

Inspeção individual dos vídeos, incluindo:

* ficha técnica;
* características físicas;
* observações multimodais;
* interpretações semânticas;
* evidências associadas a timestamps;
* galeria de keyframes.

### 📈 Performance & Insights Cruzados

Exploração das relações entre características criativas e performance observada utilizando DuckDB.

Inclui:

* análise multi-label de mecanismos de gancho;
* métricas de dinamismo nos primeiros segundos;
* cruzamentos entre features e performance;
* snapshots longitudinais;
* séries temporais.

---

## Relação com o VIE Engine

Este repositório **não contém o pipeline completo de ingestão e extração**.

O fluxo é:

```text
VIE Engine
    │
    ├── Video / Audio Processing
    ├── Deterministic Feature Extraction
    ├── Multimodal LLM Analysis
    ├── Structured Validation
    └── Feature Dataset
            │
            ▼
      VIE Demo
            │
            ├── DuckDB
            ├── SQL Analytics
            └── Streamlit Dashboard
```

O motor principal contém a implementação responsável pelo processamento e extração dos dados utilizados nesta demonstração.

🔗 **[VIE Engine](https://github.com/TStryder/vie-video-intelligence-engine)**

---

## Demo Online

A demonstração pode ser executada diretamente no Streamlit Community Cloud:

🔗 **[vie-video-intelligence-demo.streamlit.app](https://vie-video-intelligence-demo.streamlit.app/)**

O dashboard utiliza apenas os dados já presentes no repositório e não requer chamadas externas de API para funcionar.
