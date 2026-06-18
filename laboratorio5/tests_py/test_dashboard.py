from __future__ import annotations

import pandas as pd

from lab05.dashboard import render_dashboard


def test_dashboard_renders_comparative_graphs_and_stats(tmp_path):
    results = tmp_path / "results.csv"
    pd.DataFrame(
        {
            "tecnologia": ["REST", "REST", "GraphQL", "GraphQL"],
            "tempo_ms": [4.0, 5.0, 2.0, 2.5],
            "tamanho_bytes": [1000, 980, 80, 82],
        }
    ).to_csv(results, index=False)

    rendered = render_dashboard(results, tmp_path / "figures")

    assert rendered["status"] == "ok"
    assert set(rendered["figures"]) == {"tempo_ms", "tamanho_bytes"}
    assert set(rendered["saved_files"]) == {"tempo_ms", "tamanho_bytes"}
    assert all(path.exists() for path in rendered["saved_files"].values())
    assert "REST" in rendered["stats"].index
    assert "GraphQL" in rendered["stats"].index


def test_dashboard_handles_missing_csv(tmp_path):
    rendered = render_dashboard(tmp_path / "missing.csv")
    assert rendered["status"] == "missing"
    assert rendered["figures"] == {}


def test_dashboard_handles_empty_csv(tmp_path):
    results = tmp_path / "results.csv"
    pd.DataFrame(columns=["tecnologia", "tempo_ms", "tamanho_bytes"]).to_csv(results, index=False)
    rendered = render_dashboard(results)
    assert rendered["status"] == "empty"
    assert rendered["figures"] == {}
