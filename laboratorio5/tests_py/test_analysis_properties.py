from __future__ import annotations

import math

import numpy as np
import pandas as pd
from hypothesis import given, settings
from hypothesis import strategies as st

from lab05.analysis import compare_treatments, descriptive_stats, generate_report, reject_null


@settings(max_examples=100)
@given(
    st.lists(st.floats(min_value=0.001, max_value=10_000, allow_nan=False, allow_infinity=False), min_size=2, max_size=50),
    st.lists(st.floats(min_value=0.001, max_value=10_000, allow_nan=False, allow_infinity=False), min_size=2, max_size=50),
)
def test_property_11_descriptive_statistics_and_reduction(rest_values, graphql_values):
    """Feature: graphql-vs-rest-experiment, Property 11: Corretude das estatisticas descritivas."""
    df = pd.DataFrame(
        {
            "tecnologia": ["REST"] * len(rest_values) + ["GraphQL"] * len(graphql_values),
            "tempo_ms": rest_values + graphql_values,
            "tamanho_bytes": [100] * (len(rest_values) + len(graphql_values)),
        }
    )
    stats = descriptive_stats(df, "REST", "tempo_ms")
    comparison = compare_treatments(df, "tempo_ms")

    assert stats.count == len(rest_values)
    assert math.isclose(stats.mean, float(np.mean(rest_values)), rel_tol=1e-9)
    assert math.isclose(stats.median, float(np.median(rest_values)), rel_tol=1e-9)
    assert stats.min <= stats.mean <= stats.max
    assert stats.min <= stats.median <= stats.max

    expected_reduction = (
        (comparison.median_rest - comparison.median_graphql) / comparison.median_rest * 100
        if comparison.median_rest
        else 0.0
    )
    assert math.isclose(comparison.pct_reduction, expected_reduction, rel_tol=1e-9, abs_tol=1e-9)


@settings(max_examples=100)
@given(st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False))
def test_property_12_null_hypothesis_decision_uses_alpha(p_value):
    """Feature: graphql-vs-rest-experiment, Property 12: Decisao das hipoteses pelo nivel de significancia."""
    assert reject_null(p_value) is (p_value < 0.05)


def test_compare_treatments_documents_insufficient_data():
    df = pd.DataFrame({"tecnologia": ["REST"], "tempo_ms": [1.0], "tamanho_bytes": [10]})
    result = compare_treatments(df, "tempo_ms")
    assert math.isnan(result.p_value)
    assert result.reject_null is False


def test_generate_report_without_optional_tabulate_dependency(tmp_path):
    results = tmp_path / "results.csv"
    output = tmp_path / "relatorio.md"
    pd.DataFrame(
        {
            "tecnologia": ["REST", "REST", "GraphQL", "GraphQL"],
            "tempo_ms": [4.0, 5.0, 2.0, 2.5],
            "tamanho_bytes": [1000, 980, 80, 82],
        }
    ).to_csv(results, index=False)

    generated = generate_report(results, output)
    text = generated.read_text(encoding="utf-8")

    assert generated == output
    assert "Relatorio LAB05" in text
    assert "Decisao:" in text
