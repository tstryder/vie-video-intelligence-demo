"""
app.py

VIE — Video Intelligence Engine (Public Demonstration Dashboard).
Dashboard interativo de inteligência criativa multimodal operando sobre DuckDB e Parquet.

100% Offline & Autônomo — sem chamadas a APIs pagas, modelos pesados ou scrapers.
"""

from __future__ import annotations

import sys
import asyncio
from pathlib import Path
import json
import re
from typing import Any, Optional

# Fix para ProactorEventLoop no Windows com Python 3.13
if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

import pandas as pd
import streamlit as st
import altair as alt
import plotly.express as px

# Inclusão da raiz no sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.analytics import AnalyticsEngine

FEATURES_PATH = ROOT_DIR / "data" / "features.parquet"
PERFORMANCE_PATH = ROOT_DIR / "data" / "performance.parquet"
VIDEOS_DIR = ROOT_DIR / "data" / "videos"

st.set_page_config(
    page_title="VIE — Video Intelligence Engine",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Funções Utilitárias Defensivas
# ---------------------------------------------------------------------------

def safe_str(val: object, default: str = "") -> str:
    """Evita quebra de NAType/None ao converter para string."""
    if val is None or pd.isna(val):
        return default
    s = str(val).strip()
    return default if s.lower() in ("<na>", "none", "nan", "") else s


def safe_float(val: object, default: float = 0.0) -> float:
    """Conversão segura para float."""
    if val is None or pd.isna(val):
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def safe_int(val: object, default: int = 0) -> int:
    """Conversão segura para int."""
    if val is None or pd.isna(val):
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def safe_bool(val: object, default: bool = False) -> bool:
    """Conversão segura para bool."""
    if val is None or pd.isna(val):
        return default
    try:
        return bool(val)
    except Exception:
        return default


@st.cache_data(show_spinner="Carregando base de dados...")
def load_features_dataframe() -> pd.DataFrame:
    """Carrega o Feature Store sanitizado com DuckDB."""
    engine = AnalyticsEngine(FEATURES_PATH, PERFORMANCE_PATH)
    # Seleciona v_features completa
    df = engine.con.execute("SELECT * FROM v_features ORDER BY real_views DESC").df()
    return df


@st.cache_data(show_spinner=False)
def load_video_final_json(video_id: str) -> Optional[dict[str, Any]]:
    """Carrega o final.json sanitizado do vídeo para exibir evidências amarradas."""
    p = VIDEOS_DIR / video_id / "final.json"
    if p.exists():
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def get_video_frames(video_id: str) -> list[dict[str, Any]]:
    """Recupera a lista ordenada de keyframes em disco com seus timestamps."""
    frames_dir = VIDEOS_DIR / video_id / "frames"
    if not frames_dir.exists():
        return []
    
    results: list[dict[str, Any]] = []
    for f in frames_dir.glob("*.jpg"):
        ts = 0.0
        m = re.search(r"_(\d+(?:\.\d+)?)s\.jpg$", f.name)
        if m:
            try:
                ts = float(m.group(1))
            except ValueError:
                pass
        results.append({
            "path": f,
            "name": f.name,
            "timestamp": ts,
            "label": f"{ts:.2f}s" if m else f.name
        })
    results.sort(key=lambda x: x["timestamp"])
    return results

def find_matching_frame(
    frames: list[dict[str, Any]],
    frame_id: Optional[str] = None,
    timestamp: float = 0.0,
) -> tuple[Optional[dict[str, Any]], bool, float]:
    """
    Localiza o frame vinculado à evidência.
    Retorna uma tupla: (frame_dict, is_exact_match, delta_seconds).
    1. Busca por nome exato (frame_id).
    2. Fallback: busca o keyframe com menor diferença temporal em relação ao timestamp.
    """
    if not frames:
        return None, False, 0.0

    clean_fid = (frame_id or "").strip()
    if clean_fid:
        for f in frames:
            if f["name"] == clean_fid or f["path"].name == clean_fid:
                delta = abs(f["timestamp"] - timestamp)
                return f, True, delta

    # Busca o keyframe mais próximo temporalmente
    closest = min(frames, key=lambda f: abs(f["timestamp"] - timestamp))
    delta = abs(closest["timestamp"] - timestamp)
    return closest, False, delta


# ---------------------------------------------------------------------------
# Sidebar & Filtros
# ---------------------------------------------------------------------------

df = load_features_dataframe()

st.sidebar.markdown("## 🎬 VIE Demo V3")
st.sidebar.caption("Video Intelligence Engine — Multimodal Analytics")
st.sidebar.markdown("---")

if st.sidebar.button("🔄 Atualizar Visualizações", width="stretch"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.subheader("Filtros da Base")

# Filtro de Plataforma
platforms = ["Todas"] + sorted(df["platform"].dropna().unique().tolist())
selected_plat = st.sidebar.selectbox("Plataforma:", platforms)

# Filtro de Categoria
categories = ["Todas"] + sorted(df["content_category"].dropna().unique().tolist())
selected_cat = st.sidebar.selectbox("Categoria:", categories)

# Filtro de Formato
formats = ["Todos"] + sorted(df["content_format"].dropna().unique().tolist())
selected_format = st.sidebar.selectbox("Formato:", formats)

# Filtro de Mecanismo de Gancho
mechs = ["Todos"] + sorted(df["hook_mechanism_primary"].dropna().unique().tolist())
selected_mech = st.sidebar.selectbox("Mecanismo de Gancho:", mechs)

# Aplicação dos Filtros
df_filtered = df.copy()
if selected_plat != "Todas":
    df_filtered = df_filtered[df_filtered["platform"] == selected_plat]
if selected_cat != "Todas":
    df_filtered = df_filtered[df_filtered["content_category"] == selected_cat]
if selected_format != "Todos":
    df_filtered = df_filtered[df_filtered["content_format"] == selected_format]
if selected_mech != "Todos":
    df_filtered = df_filtered[df_filtered["hook_mechanism_primary"] == selected_mech]

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **ℹ️ Metodologia & Escopo**  
    Amostra demonstrativa de **10 vídeos públicos** (YouTube Shorts) para exibição de arquitetura de dados, modelagem multidimensional e inteligência multimodal. Não constitui inferência causal sobre o algoritmo de recomendação de terceiros.
    """
)
st.sidebar.caption("Engenharia: DuckDB + Parquet + Streamlit")


# ---------------------------------------------------------------------------
# Cabeçalho Principal
# ---------------------------------------------------------------------------

st.title("🎬 Video Intelligence Engine (VIE)")
st.markdown(
    "Pipeline analítico multimodal que converte vídeos curtos em dados estruturados, "
    "unindo medições físicas determinísticas (FFprobe, PySceneDetect, Whisper) a observações "
    "e interpretações de IA (Gemini)."
)

tab_overview, tab_inspector, tab_insights = st.tabs([
    "📊 Panorama da Base & Métricas",
    "🔍 Creative Inspector & Keyframes",
    "📈 Performance & Insights Cruzados"
])

# ===========================================================================
# ABA 1: PANORAMA DA BASE & MÉTRICAS
# ===========================================================================
with tab_overview:
    total_vids = len(df_filtered)
    avg_dur = df_filtered["duration_seconds"].mean() if total_vids > 0 else 0.0
    avg_wpm = df_filtered["words_per_minute"].mean() if total_vids > 0 else 0.0
    avg_cuts = df_filtered["cuts_per_second"].mean() if total_vids > 0 else 0.0
    total_views = int(df_filtered["real_views"].sum()) if total_vids > 0 else 0
    avg_eng = (df_filtered["engagement_rate"].mean() * 100.0) if total_vids > 0 else 0.0

    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    kpi1.metric("Vídeos", total_vids)
    kpi2.metric("Duração Média", f"{avg_dur:.1f}s")
    kpi3.metric("Ritmo Médio", f"{avg_wpm:.0f} WPM")
    kpi4.metric("Cortes/s Médio", f"{avg_cuts:.2f}")
    kpi5.metric("Total Views", f"{total_views:,}")
    kpi6.metric("Engajamento Médio", f"{avg_eng:.2f}%")

    st.markdown("---")
    st.subheader("📋 Tabela Consolidada de Vídeos (Fatos & Performance)")

    cols_display = [
        "video_id", "author", "duration_seconds", "cuts_per_second",
        "words_per_minute", "hook_mechanism_primary", "content_category",
        "content_format", "real_views", "engagement_rate"
    ]
    df_table = df_filtered[[c for c in cols_display if c in df_filtered.columns]].copy()
    
    st.dataframe(
        df_table,
        width="stretch",
        hide_index=True,
        column_config={
            "video_id": st.column_config.TextColumn("ID do Vídeo", width="small"),
            "author": st.column_config.TextColumn("Canal / Autor", width="medium"),
            "duration_seconds": st.column_config.NumberColumn("Duração (s)", format="%.1f"),
            "cuts_per_second": st.column_config.NumberColumn("Cortes/s", format="%.2f"),
            "words_per_minute": st.column_config.NumberColumn("Palavras/min", format="%.0f"),
            "hook_mechanism_primary": st.column_config.TextColumn("Gancho Primário"),
            "content_category": st.column_config.TextColumn("Categoria"),
            "content_format": st.column_config.TextColumn("Formato"),
            "real_views": st.column_config.NumberColumn("Visualizações", format="%d"),
            "engagement_rate": st.column_config.ProgressColumn(
                "Taxa de Engajamento",
                format="%.2f%%",
                min_value=0.0,
                max_value=0.25,
            ),
        },
    )

    st.markdown("---")
    st.subheader("📊 Distribuição de Categorias e Formatos")
    
    c_chart1, c_chart2 = st.columns(2)
    with c_chart1:
        cat_counts = df_filtered["content_category"].value_counts().reset_index()
        cat_counts.columns = ["Categoria", "Vídeos"]
        fig_cat = px.bar(
            cat_counts, x="Categoria", y="Vídeos",
            color="Categoria", title="Distribuição por Categoria",
            text="Vídeos", template="plotly_dark"
        )
        fig_cat.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_cat, width="stretch")

    with c_chart2:
        fmt_counts = df_filtered["content_format"].value_counts().reset_index()
        fmt_counts.columns = ["Formato", "Vídeos"]
        fig_fmt = px.pie(
            fmt_counts, names="Formato", values="Vídeos",
            title="Distribuição por Formato Estrutural",
            hole=0.4, template="plotly_dark"
        )
        fig_fmt.update_layout(height=350)
        st.plotly_chart(fig_fmt, width="stretch")


# ===========================================================================
# ABA 2: CREATIVE INSPECTOR & KEYFRAMES
# ===========================================================================
with tab_inspector:
    st.subheader("🔍 Inspeção Detalhada do Criativo, Evidências & Keyframes")
    
    video_list = list(df_filtered["video_id"].unique())
    if not video_list:
        video_list = list(df["video_id"].unique())

    if not video_list:
        st.warning("Nenhum vídeo disponível com os filtros atuais.")
    else:
        # Seletor com formato legível
        selected_vid = st.selectbox(
            "Selecione um vídeo para inspecionar:",
            video_list,
            format_func=lambda vid: f"{vid} | {safe_str(df.loc[df['video_id']==vid, 'author'].iloc[0])} — {safe_str(df.loc[df['video_id']==vid, 'content_category'].iloc[0])} ({safe_str(df.loc[df['video_id']==vid, 'content_format'].iloc[0])})",
            key="inspector_video_select"
        )
        
        v_row = df[df["video_id"] == selected_vid].iloc[0]
        final_json = load_video_final_json(selected_vid)
        
        # Layout em duas colunas principais
        col_meta, col_visual = st.columns([1.1, 1.1])
        
        with col_meta:
            st.markdown("### 📋 Ficha Técnica & Diagnóstico")
            
            src_url = safe_str(v_row.get("source_url"))
            if src_url:
                st.markdown(f"🔗 **URL Pública:** [{src_url}]({src_url})")

            # 1. Metadados Físicos
            st.markdown("**1. Metadados Técnicos do Arquivo (FFprobe):**")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Duração", f"{safe_float(v_row.get('duration_seconds')):.1f}s")
            m2.metric("FPS", f"{safe_float(v_row.get('fps')):.1f}")
            m3.metric("Resolução", f"{safe_int(v_row.get('width'))}x{safe_int(v_row.get('height'))}")
            m4.metric("Aspect Ratio", f"{safe_float(v_row.get('aspect_ratio')):.2f}")

            # 2. Medições Determinísticas
            st.markdown("**2. Medições de Edição & Fala (PySceneDetect + Whisper):**")
            e1, e2, e3, e4 = st.columns(4)
            e1.metric("Cortes/s", f"{safe_float(v_row.get('cuts_per_second')):.2f}")
            e2.metric("Cortes 3s", safe_int(v_row.get("cuts_in_first_3s")))
            e3.metric("Ritmo Fala", f"{safe_float(v_row.get('words_per_minute')):.0f} WPM")
            e4.metric("Ratio de Fala", f"{safe_float(v_row.get('speech_ratio')) * 100:.1f}%")

            # 3. Performance Observada
            st.markdown("**3. Performance Pública Observada (yt-dlp):**")
            p1, p2, p3, p4 = st.columns(4)
            p1.metric("Visualizações", f"{safe_int(v_row.get('real_views')):,}")
            p2.metric("Curtidas", f"{safe_int(v_row.get('real_likes')):,}")
            p3.metric("Comentários", f"{safe_int(v_row.get('real_comments')):,}")
            p4.metric("Engajamento", f"{safe_float(v_row.get('engagement_rate')) * 100:.2f}%")

            # 4. Observações Multimodais
            st.markdown("---")
            st.markdown("**4. Observações Sensoriais (Gemini Vision/Audio):**")
            o1, o2 = st.columns(2)
            with o1:
                st.write(f"• **Face Visível:** {'Sim' if safe_bool(v_row.get('face_visible')) else 'Não'}")
                st.write(f"• **Produto Visível:** {'Sim' if safe_bool(v_row.get('product_visible')) else 'Não'}")
                st.write(f"• **Webcam:** {'Sim' if safe_bool(v_row.get('has_webcam')) else 'Não'}")
            with o2:
                st.write(f"• **Legenda Centralizada:** {'Sim' if safe_bool(v_row.get('has_center_caption')) else 'Não'}")
                st.write(f"• **Tela Dividida:** {'Sim' if safe_bool(v_row.get('split_screen')) else 'Não'}")
                st.write(f"• **Cenário:** `{safe_str(v_row.get('environment_type'), 'N/A')}`")

            # 5. Interpretação Semântica
            st.markdown("---")
            st.markdown("**5. Interpretação Semântica da IA (Gemini):**")
            hook_prim = safe_str(v_row.get("hook_mechanism_primary"))
            st.info(f"🎯 **Mecanismo de Gancho Primário:** `{hook_prim}`")
            
            st.write(f"• **Sujeito do Gancho:** {safe_str(v_row.get('hook_subject'), 'N/A')}")
            st.write(f"• **Ação de Abertura:** {safe_str(v_row.get('hook_opening_action'), 'N/A')}")
            st.write(f"• **Estrutura Narrativa:** `{safe_str(v_row.get('narrative_structure'), 'N/A')}`")
            st.write(f"• **Mecanismos Retóricos:** {safe_str(v_row.get('rhetorical_mechanisms'), 'Nenhum')}")
            st.write(f"• **Chamada para Ação (CTA):** {'Sim' if safe_bool(v_row.get('cta_present')) else 'Não'} (Tipo: `{safe_str(v_row.get('cta_types'), 'none')}`)")

            # Expander de legenda original
            caption_text = safe_str(v_row.get("caption"))
            if caption_text:
                with st.expander("📝 Legenda Original do Vídeo"):
                    st.text_area("Texto bruto da descrição:", caption_text, height=180, disabled=True)

        with col_visual:
            st.markdown("### 🎯 Evidências Multimodais & Keyframes")
            st.caption(
                "A IA do VIE vincula cada fenômeno cognitivo a um timestamp da linha do tempo. "
                "Abaixo, cada insight citado é exibido diretamente com o keyframe correspondente daquele momento."
            )
            frames = get_video_frames(selected_vid)

            if final_json and "interpretations" in final_json:
                interp = final_json["interpretations"]

                # Coleta evidências de todas as dimensões
                ev_items = []
                for m in interp.get("hook", {}).get("mechanisms", []):
                    for ev in m.get("evidence", []):
                        ev_items.append(("Gancho", m.get("type"), ev))
                for ev in interp.get("narrative", {}).get("evidence", []):
                    ev_items.append(("Narrativa", interp.get("narrative", {}).get("structure"), ev))
                for r in interp.get("rhetorical_mechanisms", []):
                    for ev in r.get("evidence", []):
                        ev_items.append(("Retórica", r.get("mechanism"), ev))
                for ev in interp.get("cta", {}).get("evidence", []):
                    ev_items.append(("CTA", str(interp.get("cta", {}).get("types")), ev))

                if ev_items:
                    for cat, sub, ev in ev_items:
                        t_sec = safe_float(ev.get("timestamp_seconds"))
                        fid = safe_str(ev.get("frame_id"))
                        txt = safe_str(ev.get("text"))
                        obs = safe_str(ev.get("observation"))

                        matched_frame, is_exact, delta = find_matching_frame(frames, fid, t_sec)

                        with st.container():
                            if matched_frame:
                                c_info, c_thumb = st.columns([1.3, 1.0])
                                with c_info:
                                    st.markdown(f"**[{cat}: `{sub}`]** — ⏱️ `{t_sec:.1f}s`")
                                    if is_exact:
                                        st.caption(f"🎯 **Frame exato citado**: `{matched_frame['name']}` (Δt={delta:.2f}s)")
                                    else:
                                        st.caption(f"⏱️ **Keyframe correspondente**: `{matched_frame['name']}` (Δt={delta:.2f}s)")
                                    st.markdown(f"*{obs}*")
                                    if txt:
                                        st.markdown(f'> 💬 *"{txt}"*')
                                with c_thumb:
                                    st.image(
                                        str(matched_frame["path"]),
                                        caption=f"📸 Keyframe em {matched_frame['label']}",
                                        width="stretch"
                                    )
                            else:
                                st.markdown(f"**[{cat}: `{sub}`]** — ⏱️ `{t_sec:.1f}s` | `🎙️ Áudio/Fala`")
                                st.markdown(f"*{obs}*")
                                if txt:
                                    st.markdown(f'> 💬 *"{txt}"*')
                            st.markdown("<hr style='margin: 10px 0; border: none; border-top: 1px solid #334155;'/>", unsafe_allow_html=True)
                else:
                    st.info("Nenhuma evidência estruturada listada para este vídeo.")
            else:
                st.info("Arquivo final.json não encontrado para carregar evidências completas.")

            # Galeria Completa em Expander
            if frames:
                with st.expander(f"🎞️ Galeria Completa de Todos os Keyframes ({len(frames)} frames)"):
                    st.caption("Visão sequencial de todos os cortes detectados pelo PySceneDetect:")
                    grid_cols = st.columns(3)
                    for i, f_item in enumerate(frames):
                        with grid_cols[i % 3]:
                            st.image(
                                str(f_item["path"]),
                                caption=f"⏱️ {f_item['label']}",
                                width="stretch"
                            )


# ===========================================================================
# ABA 3: PERFORMANCE & INSIGHTS CRUZADOS
# ===========================================================================
with tab_insights:
    st.subheader("📈 Inteligência Analítica Cruzada (DuckDB SQL)")
    
    engine = AnalyticsEngine(FEATURES_PATH, PERFORMANCE_PATH)
    
    col_chart_a, col_chart_b = st.columns(2)
    
    with col_chart_a:
        st.markdown("#### 🎯 Frequência de Mecanismos de Gancho (Multi-label)")
        df_mech_freq = engine.mechanism_frequency()
        if not df_mech_freq.empty:
            fig_freq = px.bar(
                df_mech_freq, x="occurrences", y="mechanism",
                orientation="h",
                text="occurrences",
                color="occurrences",
                color_continuous_scale="Blues",
                labels={"occurrences": "Ocorrências na Base", "mechanism": "Mecanismo"},
                template="plotly_dark"
            )
            fig_freq.update_layout(height=380, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_freq, width="stretch")
        else:
            st.info("Dados insuficientes.")

    with col_chart_b:
        st.markdown("#### 🏆 Performance por Mecanismo de Gancho")
        df_mech_perf = engine.performance_by_mechanism()
        if not df_mech_perf.empty:
            fig_perf = px.bar(
                df_mech_perf, x="mechanism", y="median_views",
                color="avg_engagement_pct",
                color_continuous_scale="Viridis",
                text="avg_engagement_pct",
                labels={
                    "median_views": "Mediana de Visualizações",
                    "mechanism": "Mecanismo",
                    "avg_engagement_pct": "Engajamento Médio (%)"
                },
                template="plotly_dark"
            )
            fig_perf.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_perf.update_layout(height=380)
            st.plotly_chart(fig_perf, width="stretch")
        else:
            st.info("Dados insuficientes.")

    st.markdown("---")
    
    col_pacing, col_series = st.columns(2)
    
    with col_pacing:
        st.markdown("#### ⚡ Ritmo de Abertura (Cortes nos Primeiros 3s)")
        df_pacing = engine.pacing_correlation_summary()
        st.dataframe(
            df_pacing,
            width="stretch",
            hide_index=True,
            column_config={
                "faixa_ritmo_3s": st.column_config.TextColumn("Faixa de Ritmo"),
                "video_count": st.column_config.NumberColumn("Qtd Vídeos"),
                "avg_wpm": st.column_config.NumberColumn("WPM Médio", format="%.0f"),
                "avg_cuts_per_second": st.column_config.NumberColumn("Cortes/s", format="%.2f"),
                "avg_views": st.column_config.NumberColumn("Views Médias", format="%d"),
                "avg_engagement_pct": st.column_config.NumberColumn("Engajamento", format="%.2f%%"),
            }
        )
        st.caption("Agrupamento SQL comparando o impacto do dinamismo nos primeiros 3 segundos.")

    with col_series:
        st.markdown("#### ⏳ Série Temporal de Coletas (Snapshots DuckDB)")
        df_ts = engine.get_time_series_data()
        if not df_ts.empty:
            fig_ts = px.line(
                df_ts, x="collected_at", y="views", color="video_id",
                markers=True,
                labels={"collected_at": "Horário da Coleta (UTC)", "views": "Visualizações", "video_id": "ID do Vídeo"},
                title="Evolução Longitudinal de Views por Snapshot",
                template="plotly_dark"
            )
            fig_ts.update_layout(height=340, legend={"orientation": "h", "y": -0.2})
            st.plotly_chart(fig_ts, width="stretch")
        else:
            st.info("Snapshots de performance indisponíveis.")

# ---------------------------------------------------------------------------
# Rodapé com Disclaimer Metodológico
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #94A3B8; font-size: 0.85rem;'>
        <b>VIE (Video Intelligence Engine) — Demonstração Pública</b> | Arquitetura de Dados & Inteligência Multimodal<br/>
        <i>Aviso Legal & Metodológico: Amostra observacional demonstrativa (N=10) derivada de vídeos públicos no YouTube Shorts.
        Não constitui inferência causal sobre algoritmos de distribuição. Todos os direitos dos conteúdos citados pertencem aos respectivos criadores.</i>
    </div>
    """,
    unsafe_allow_html=True
)
