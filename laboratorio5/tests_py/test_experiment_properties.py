from __future__ import annotations

import random
import tempfile
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from hypothesis import given, settings
from hypothesis import strategies as st

from lab05.experiment import (
    CSV_COLUMNS,
    Measurement,
    ResultsWriter,
    is_failure,
    load_results,
    make_paired_requests,
    select_player_id,
    should_enable_official_collection,
)


@dataclass
class FakeResponse:
    status_code: int
    payload: dict | None = None

    def json(self):
        if self.payload is None:
            raise ValueError("sem json")
        return self.payload


@settings(max_examples=100)
@given(st.integers(min_value=1, max_value=10_000))
def test_property_7_paired_iteration_uses_same_identifier(player_id):
    """Feature: graphql-vs-rest-experiment, Property 7: Iteracao pareada usa o mesmo identificador."""
    pairs = make_paired_requests(player_id)
    assert pairs == (("REST", player_id), ("GraphQL", player_id))


@settings(max_examples=100)
@given(st.integers(min_value=1, max_value=500), st.integers(min_value=0, max_value=2**32 - 1))
def test_property_8_selected_identifier_belongs_to_valid_domain(player_count, seed):
    """Feature: graphql-vs-rest-experiment, Property 8: Identificador sorteado pertence ao dominio valido."""
    player_id = select_player_id(player_count, random.Random(seed))
    assert 1 <= player_id <= player_count


@settings(max_examples=100)
@given(
    st.one_of(st.none(), st.integers(min_value=100, max_value=599)),
    st.booleans(),
    st.booleans(),
    st.booleans(),
)
def test_property_9_request_failure_classification(status_code, has_error_field, has_errors_field, has_exception):
    """Feature: graphql-vs-rest-experiment, Property 9: Classificacao de falha de requisicao."""
    payload = {}
    if has_error_field:
        payload["error"] = "erro"
    if has_errors_field:
        payload["errors"] = [{"message": "erro"}]
    response = None if status_code is None else FakeResponse(status_code, payload or None)
    expected = has_exception or response is None or status_code >= 400 or has_error_field or has_errors_field
    assert is_failure(response=response, error=Exception("x") if has_exception else None) is expected


@settings(max_examples=100)
@given(
    st.lists(
        st.tuples(
            st.sampled_from(["REST", "GraphQL"]),
            st.floats(min_value=0, max_value=10_000, allow_nan=False, allow_infinity=False),
            st.integers(min_value=0, max_value=1_000_000),
        ),
        min_size=1,
        max_size=50,
    )
)
def test_property_10_results_file_round_trip(rows):
    """Feature: graphql-vs-rest-experiment, Property 10: Round-trip do arquivo de resultados."""
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "results.csv"
        writer = ResultsWriter(path)
        for tecnologia, tempo_ms, tamanho_bytes in rows:
            assert writer.append(Measurement(tecnologia, tempo_ms, tamanho_bytes))

        df = load_results(path)
        assert list(df.columns) == CSV_COLUMNS
        assert len(df) == len(rows)
        assert set(df["tecnologia"]).issubset({"REST", "GraphQL"})


@settings(max_examples=100)
@given(st.integers(min_value=0, max_value=100))
def test_property_13_official_collection_enabled_only_without_failures(failure_count):
    """Feature: graphql-vs-rest-experiment, Property 13: Habilitacao da coleta oficial apos a validacao."""
    assert should_enable_official_collection(failure_count) is (failure_count == 0)


def test_official_count_range_with_mocked_failure_rate():
    records = [
        Measurement("REST" if i % 2 == 0 else "GraphQL", 1.0, 10)
        for i in range(1900)
    ]
    assert 1800 <= len(records) <= 2000


def test_csv_has_single_header(tmp_path):
    path = tmp_path / "results.csv"
    writer = ResultsWriter(path)
    writer.append(Measurement("REST", 1.25, 123))
    content = path.read_text(encoding="utf-8").splitlines()
    assert content[0] == ",".join(CSV_COLUMNS)
    assert sum(1 for line in content if line == ",".join(CSV_COLUMNS)) == 1
    assert isinstance(pd.read_csv(path), pd.DataFrame)
