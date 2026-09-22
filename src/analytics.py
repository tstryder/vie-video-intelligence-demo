"""
src/analytics.py

Analytics & Creative Intelligence Engine (Public Demo).
Executa consultas analíticas em milissegundos via DuckDB diretamente sobre
os arquivos Parquet em data/features.parquet e data/performance.parquet.

Operação 100% offline — zero dependências de APIs externas (Gemini, Whisper ou yt-dlp).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional
import duckdb
import pandas as pd

DEMO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FEATURES_PATH = DEMO_ROOT / "data" / "features.parquet"
DEFAULT_PERFORMANCE_PATH = DEMO_ROOT / "data" / "performance.parquet"


class AnalyticsEngine:
    """Motor analítico de alto desempenho baseado em DuckDB em memória."""

    def __init__(
        self,
        features_path: Optional[Path] = None,
        performance_path: Optional[Path] = None,
    ):
        self.features_path = Path(features_path or DEFAULT_FEATURES_PATH)
        self.performance_path = Path(performance_path or DEFAULT_PERFORMANCE_PATH)

        if not self.features_path.exists():
            raise FileNotFoundError(
                f"Arquivo de features não encontrado em: {self.features_path}"
            )

        self.con = duckdb.connect(database=":memory:")
        self._init_unified_view()

    def _init_unified_view(self) -> None:
        """
        Cria a view 'v_features' no DuckDB unindo features com a medição mais recente
        de performance.parquet (via ROW_NUMBER() OVER (PARTITION BY video_id ORDER BY collected_at DESC)).
        """
        features_posix = self.features_path.as_posix()
        f_cols = [
            row[0]
            for row in self.con.execute(
                f"DESCRIBE SELECT * FROM read_parquet('{features_posix}')"
            ).fetchall()
        ]

        perf_cols = [
            "real_views",
            "real_likes",
            "real_comments",
            "real_shares",
            "real_reposts",
            "real_saves",
            "engagement_rate",
            "performance_collected_at",
        ]
        cols_to_exclude = [c for c in perf_cols if c in f_cols]
        exclude_clause = (
            f"EXCLUDE ({', '.join(cols_to_exclude)})" if cols_to_exclude else ""
        )

        fallback_views = "f.real_views, 0" if "real_views" in f_cols else "0"
        fallback_likes = "f.real_likes, 0" if "real_likes" in f_cols else "0"
        fallback_comments = "f.real_comments, 0" if "real_comments" in f_cols else "0"
        fallback_eng = (
            "f.engagement_rate, 0.0" if "engagement_rate" in f_cols else "0.0"
        )

        has_performance = (
            self.performance_path.exists()
            and self.performance_path.is_file()
            and self.performance_path.stat().st_size > 0
        )

        if has_performance:
            try:
                perf_posix = self.performance_path.as_posix()
                self.con.execute(
                    f"SELECT 1 FROM read_parquet('{perf_posix}') LIMIT 1"
                )
                create_view_sql = f"""
                CREATE OR REPLACE VIEW v_features AS
                WITH latest_perf AS (
                    SELECT *,
                           ROW_NUMBER() OVER (PARTITION BY video_id ORDER BY collected_at DESC) as rn
                    FROM read_parquet('{perf_posix}')
                )
                SELECT f.* {exclude_clause},
                       COALESCE(p.views, {fallback_views}) AS real_views,
                       COALESCE(p.likes, {fallback_likes}) AS real_likes,
                       COALESCE(p.comments, {fallback_comments}) AS real_comments,
                       COALESCE(p.engagement_rate, {fallback_eng}) AS engagement_rate,
                       p.collected_at AS performance_collected_at
                FROM read_parquet('{features_posix}') f
                LEFT JOIN latest_perf p 
                    ON f.video_id = p.video_id AND p.rn = 1
                """
                self.con.execute(create_view_sql)
                return
            except Exception:
                pass

        # Fallback defensivo: sem performance.parquet
        create_view_sql = f"""
        CREATE OR REPLACE VIEW v_features AS
        SELECT f.* {exclude_clause},
               COALESCE({fallback_views}) AS real_views,
               COALESCE({fallback_likes}) AS real_likes,
               COALESCE({fallback_comments}) AS real_comments,
               COALESCE({fallback_eng}) AS engagement_rate,
               CAST(NULL AS VARCHAR) AS performance_collected_at
        FROM read_parquet('{features_posix}') f
        """
        self.con.execute(create_view_sql)

    def summary(self) -> pd.DataFrame:
        """
        Panorama estatístico geral da base: total de vídeos, médias de duração,
        WPM, cortes por segundo e taxa de engajamento.
        """
        query = """
        SELECT
            COUNT(*) AS total_videos,
            ROUND(AVG(duration_seconds), 2) AS avg_duration_seconds,
            ROUND(AVG(words_per_minute), 1) AS avg_wpm,
            ROUND(AVG(cuts_per_second), 3) AS avg_cuts_per_second,
            ROUND(AVG(speech_ratio), 3) AS avg_speech_ratio,
            CAST(SUM(real_views) AS BIGINT) AS total_views,
            ROUND(AVG(engagement_rate) * 100, 2) AS avg_engagement_pct
        FROM v_features
        """
        return self.con.execute(query).df()

    def mechanism_frequency(self) -> pd.DataFrame:
        """
        Consulta multi-label de ganchos via UNNEST(hook_mechanisms).
        """
        query = """
        WITH total AS (
            SELECT COUNT(*) AS total_videos FROM v_features
        ),
        unnested AS (
            SELECT DISTINCT video_id, UNNEST(hook_mechanisms) AS mechanism
            FROM v_features
        )
        SELECT
            mechanism,
            COUNT(*) AS occurrences,
            ROUND(COUNT(*) * 100.0 / NULLIF((SELECT total_videos FROM total), 0), 2) AS pct_of_videos
        FROM unnested
        WHERE mechanism IS NOT NULL AND mechanism != ''
        GROUP BY mechanism
        ORDER BY occurrences DESC, mechanism ASC
        """
        return self.con.execute(query).df()

    def performance_by_mechanism(self) -> pd.DataFrame:
        """
        Cruza UNNEST(hook_mechanisms) com real_views e engagement_rate
        obtidos a partir do snapshot mais recente de performance.
        """
        query = """
        WITH unnested AS (
            SELECT
                video_id,
                UNNEST(hook_mechanisms) AS mechanism,
                COALESCE(real_views, 0) AS real_views,
                COALESCE(engagement_rate, 0.0) AS engagement_rate
            FROM v_features
        )
        SELECT
            mechanism,
            COUNT(DISTINCT video_id) AS video_count,
            ROUND(MEDIAN(real_views), 0) AS median_views,
            ROUND(AVG(engagement_rate) * 100, 2) AS avg_engagement_pct
        FROM unnested
        WHERE mechanism IS NOT NULL AND mechanism != ''
        GROUP BY mechanism
        ORDER BY median_views DESC, video_count DESC
        """
        return self.con.execute(query).df()

    def category_format_matrix(self) -> pd.DataFrame:
        """
        Matriz de frequência cruzando content_category e content_format.
        """
        query = """
        SELECT
            COALESCE(NULLIF(content_category, ''), 'unspecified') AS content_category,
            COALESCE(NULLIF(content_format, ''), 'unspecified') AS content_format,
            COUNT(*) AS video_count,
            ROUND(AVG(words_per_minute), 1) AS avg_wpm,
            ROUND(AVG(cuts_in_first_3s), 2) AS avg_cuts_in_first_3s,
            ROUND(AVG(engagement_rate) * 100, 2) AS avg_engagement_pct
        FROM v_features
        GROUP BY content_category, content_format
        ORDER BY video_count DESC, content_category ASC, content_format ASC
        """
        return self.con.execute(query).df()

    def pacing_correlation_summary(self) -> pd.DataFrame:
        """
        Agrupa por faixas de ritmo de abertura (cortes nos primeiros 3s)
        e analisa WPM, cortes/s e visualizações.
        """
        query = """
        SELECT
            CASE
                WHEN cuts_in_first_3s = 0 THEN '0 cortes (estático)'
                WHEN cuts_in_first_3s BETWEEN 1 AND 2 THEN '1-2 cortes (moderado)'
                ELSE '3+ cortes (rápido)'
            END AS faixa_ritmo_3s,
            COUNT(*) AS video_count,
            ROUND(AVG(words_per_minute), 1) AS avg_wpm,
            ROUND(AVG(cuts_per_second), 3) AS avg_cuts_per_second,
            ROUND(AVG(COALESCE(real_views, 0)), 0) AS avg_views,
            ROUND(MEDIAN(COALESCE(real_views, 0)), 0) AS median_views,
            ROUND(AVG(engagement_rate) * 100, 2) AS avg_engagement_pct
        FROM v_features
        GROUP BY faixa_ritmo_3s
        ORDER BY MIN(cuts_in_first_3s) ASC
        """
        return self.con.execute(query).df()

    def get_time_series_data(self) -> pd.DataFrame:
        """
        Retorna a série temporal completa de snapshots a partir de data/performance.parquet.
        """
        if not self.performance_path.exists():
            return pd.DataFrame()
        perf_posix = self.performance_path.as_posix()
        query = f"""
        SELECT 
            video_id,
            platform,
            collected_at,
            views,
            likes,
            comments,
            shares,
            reposts,
            saves,
            ROUND(engagement_rate * 100, 2) AS engagement_pct
        FROM read_parquet('{perf_posix}')
        ORDER BY video_id, collected_at ASC
        """
        return self.con.execute(query).df()
