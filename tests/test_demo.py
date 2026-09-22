"""
tests/test_demo.py

Suíte de testes de integridade para a demonstração pública do VIE.
Verifica carregamento de dados Parquet, consultas DuckDB e independência de rede.
"""

import sys
from pathlib import Path
import json
import pytest
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.analytics import AnalyticsEngine


def test_data_files_exist():
    """Verifica presença dos arquivos Parquet essenciais."""
    data_dir = REPO_ROOT / "data"
    assert data_dir.exists(), "Diretório data/ não encontrado"
    assert (data_dir / "features.parquet").exists(), "data/features.parquet não encontrado"
    assert (data_dir / "performance.parquet").exists(), "data/performance.parquet não encontrado"


def test_features_parquet_integrity():
    """Valida integridade do features.parquet sanitizado."""
    p = REPO_ROOT / "data" / "features.parquet"
    df = pd.read_parquet(p)
    assert len(df) == 10, f"Esperado exatamente 10 vídeos, encontrado {len(df)}"
    assert "hW1rdKKfacc" not in df["video_id"].values, "Vídeo excluído hW1rdKKfacc ainda presente!"
    required_cols = [
        "video_id", "author", "platform", "duration_seconds", "cuts_per_second",
        "words_per_minute", "content_category", "content_format",
        "hook_mechanism_primary", "real_views", "real_likes", "engagement_rate"
    ]
    for col in required_cols:
        assert col in df.columns, f"Coluna obrigatória {col} ausente em features.parquet"


def test_performance_parquet_integrity():
    """Valida integridade do performance.parquet sanitizado."""
    p = REPO_ROOT / "data" / "performance.parquet"
    df = pd.read_parquet(p)
    assert len(df) == 30, f"Esperado 30 snapshots (3 por vídeo), encontrado {len(df)}"
    assert "hW1rdKKfacc" not in df["video_id"].values, "Snapshots do vídeo excluído presentes!"
    assert "status_note" not in df.columns, "Coluna interna status_note não foi excluída!"
    required_cols = ["video_id", "platform", "collected_at", "views", "likes", "comments", "engagement_rate"]
    for col in required_cols:
        assert col in df.columns, f"Coluna obrigatória {col} ausente em performance.parquet"


def test_keyframes_and_json_files():
    """Verifica que os 10 vídeos possuem keyframes e final.json válidos."""
    videos_dir = REPO_ROOT / "data" / "videos"
    assert videos_dir.exists(), "Diretório data/videos/ não encontrado"
    video_dirs = [p for p in videos_dir.iterdir() if p.is_dir()]
    assert len(video_dirs) == 10, f"Esperado 10 pastas de vídeos, encontrado {len(video_dirs)}"
    
    total_frames = 0
    for vdir in video_dirs:
        final_file = vdir / "final.json"
        assert final_file.exists(), f"final.json ausente em {vdir.name}"
        with open(final_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("video_id") == vdir.name
        assert "_stage_status" not in data, f"Campo interno _stage_status presente em {vdir.name}"
        
        frames = list((vdir / "frames").glob("*.jpg"))
        assert len(frames) >= 8, f"Esperado >= 8 frames em {vdir.name}, encontrado {len(frames)}"
        total_frames += len(frames)
        
    assert total_frames == 98, f"Esperado total de 98 frames, encontrado {total_frames}"


def test_analytics_engine_queries():
    """Valida a execução de todas as consultas SQL via DuckDB."""
    engine = AnalyticsEngine()
    
    # 1. Summary
    df_summary = engine.summary()
    assert len(df_summary) == 1
    assert df_summary["total_videos"].iloc[0] == 10
    assert df_summary["total_views"].iloc[0] > 0
    assert df_summary["avg_duration_seconds"].iloc[0] > 0
    
    # 2. Mechanism Frequency
    df_freq = engine.mechanism_frequency()
    assert not df_freq.empty
    assert "occurrences" in df_freq.columns
    assert "pct_of_videos" in df_freq.columns
    
    # 3. Performance by Mechanism
    df_perf = engine.performance_by_mechanism()
    assert not df_perf.empty
    assert "median_views" in df_perf.columns
    assert "avg_engagement_pct" in df_perf.columns
    
    # 4. Category Format Matrix
    df_matrix = engine.category_format_matrix()
    assert not df_matrix.empty
    assert "content_category" in df_matrix.columns
    assert "content_format" in df_matrix.columns
    
    # 5. Pacing Correlation
    df_pacing = engine.pacing_correlation_summary()
    assert not df_pacing.empty
    assert "faixa_ritmo_3s" in df_pacing.columns
    
    # 6. Time Series Data
    df_ts = engine.get_time_series_data()
    assert len(df_ts) == 30
    assert "views" in df_ts.columns


def test_zero_external_api_imports():
    """Garante que a execução do demo não tenta importar APIs externas ou modelos pesados."""
    banned_modules = ["google.genai", "yt_dlp", "whisper", "scenedetect", "torch"]
    for mod in banned_modules:
        assert mod not in sys.modules, f"Módulo não permitido importado em runtime: {mod}"
