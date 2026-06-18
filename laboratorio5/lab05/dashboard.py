from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .analysis import grouped_descriptive_stats
from .experiment import CSV_COLUMNS, load_results


def _plot_metric(df: pd.DataFrame, metric: str, title: str):
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=df, x="tecnologia", y=metric, hue="tecnologia", ax=ax, legend=False)
    ax.set_title(title)
    ax.set_xlabel("Tecnologia")
    ax.set_ylabel(metric)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    return fig


def render_dashboard(results_path: str | Path = "results.csv", output_dir: str | Path | None = None):
    path = Path(results_path)
    if not path.exists():
        return {
            "status": "missing",
            "message": "dados de resultados nao foram encontrados",
            "figures": {},
            "stats": None,
        }

    try:
        df = load_results(path)
    except (OSError, pd.errors.EmptyDataError, ValueError):
        return {
            "status": "missing",
            "message": "dados de resultados nao foram encontrados",
            "figures": {},
            "stats": None,
        }

    if df.empty:
        return {
            "status": "empty",
            "message": "nao ha dados suficientes para gerar as visualizacoes",
            "figures": {},
            "stats": None,
        }

    missing_columns = set(CSV_COLUMNS) - set(df.columns)
    if missing_columns:
        return {
            "status": "missing",
            "message": f"colunas ausentes: {', '.join(sorted(missing_columns))}",
            "figures": {},
            "stats": None,
        }

    stats_table = grouped_descriptive_stats(df)
    figures = {
        "tempo_ms": _plot_metric(df, "tempo_ms", "Comparacao de tempo de resposta"),
        "tamanho_bytes": _plot_metric(df, "tamanho_bytes", "Comparacao de tamanho da resposta"),
    }

    saved_files = {}
    if output_dir is not None:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        for name, fig in figures.items():
            file_path = out / f"{name}.png"
            fig.savefig(file_path, dpi=150)
            saved_files[name] = file_path

    return {
        "status": "ok",
        "message": "dashboard renderizado",
        "figures": figures,
        "saved_files": saved_files,
        "stats": stats_table,
    }
