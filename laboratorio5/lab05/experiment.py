from __future__ import annotations

import csv
import json
import logging
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

import pandas as pd
import requests

DEFAULT_ITERATIONS = 1000
VALIDATION_ITERATIONS = 10
TIMEOUT_MS = 30000
PLAYER_COUNT = 60
CSV_COLUMNS = ["tecnologia", "tempo_ms", "tamanho_bytes"]
GRAPHQL_QUERY = "query($id: Int!) { player(id: $id) { nome gols } }"

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Measurement:
    tecnologia: str
    tempo_ms: float
    tamanho_bytes: int


@dataclass(frozen=True)
class Failure:
    tecnologia: str
    player_id: int
    reason: str


@dataclass(frozen=True)
class ExperimentSummary:
    iterations: int
    successful_records: int
    failures: tuple[Failure, ...]
    output_path: Path


class ResultsWriter:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(CSV_COLUMNS)

    def append(self, measurement: Measurement) -> bool:
        try:
            with self.path.open("a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(
                    [
                        measurement.tecnologia,
                        f"{measurement.tempo_ms:.6f}",
                        int(measurement.tamanho_bytes),
                    ]
                )
            return True
        except OSError as error:
            logger.error("falha ao gravar resultado: %s", error)
            return False


def load_results(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path, usecols=CSV_COLUMNS)


def select_player_id(player_count: int, rng: random.Random | None = None) -> int:
    if player_count < 1:
        raise ValueError("player_count deve ser positivo")
    generator = rng or random
    return generator.randint(1, player_count)


def make_paired_requests(player_id: int) -> tuple[tuple[str, int], tuple[str, int]]:
    return (("REST", player_id), ("GraphQL", player_id))


def is_failure(response=None, error: Exception | None = None, body_json=None) -> bool:
    if error is not None or response is None:
        return True
    if getattr(response, "status_code", 0) >= 400:
        return True

    payload = body_json
    if payload is None:
        try:
            payload = response.json()
        except (ValueError, AttributeError):
            payload = None

    if isinstance(payload, dict) and ("errors" in payload or "error" in payload):
        return True
    return False


def measure_request(
    tecnologia: str,
    send_fn: Callable[[float], requests.Response],
    timeout_ms: int = TIMEOUT_MS,
) -> tuple[Measurement | None, str | None]:
    timeout_seconds = timeout_ms / 1000
    start = time.perf_counter()
    try:
        response = send_fn(timeout_seconds)
        content = response.content
        elapsed_ms = (time.perf_counter() - start) * 1000
        if is_failure(response=response):
            return None, f"resposta invalida para {tecnologia}"
        return Measurement(tecnologia, elapsed_ms, len(content)), None
    except requests.Timeout:
        return None, "timeout"
    except requests.RequestException as error:
        return None, str(error)


def run_experiment(
    base_url: str = "http://localhost:4000",
    iterations: int = DEFAULT_ITERATIONS,
    output_path: str | Path = "results.csv",
    player_count: int = PLAYER_COUNT,
    rng: random.Random | None = None,
) -> ExperimentSummary:
    writer = ResultsWriter(output_path)
    failures: list[Failure] = []
    successful_records = 0
    session = requests.Session()

    for _ in range(iterations):
        player_id = select_player_id(player_count, rng)
        for tecnologia, paired_id in make_paired_requests(player_id):
            if tecnologia == "REST":
                send_fn = lambda timeout, pid=paired_id: session.get(
                    f"{base_url}/rest/players/{pid}", timeout=timeout
                )
            else:
                send_fn = lambda timeout, pid=paired_id: session.post(
                    f"{base_url}/graphql",
                    json={"query": GRAPHQL_QUERY, "variables": {"id": pid}},
                    timeout=timeout,
                )

            measurement, reason = measure_request(tecnologia, send_fn)
            if measurement is None:
                failures.append(Failure(tecnologia, paired_id, reason or "falha desconhecida"))
                continue
            if writer.append(measurement):
                successful_records += 1

    return ExperimentSummary(iterations, successful_records, tuple(failures), Path(output_path))


def validate_environment(base_url: str = "http://localhost:4000") -> tuple[bool, list[str]]:
    errors: list[str] = []
    session = requests.Session()
    try:
        rest = session.get(f"{base_url}/rest/players/1", timeout=5)
        if rest.status_code != 200:
            errors.append(f"REST retornou status {rest.status_code}")
    except requests.RequestException as error:
        errors.append(f"REST indisponivel: {error}")

    try:
        gql = session.post(
            f"{base_url}/graphql",
            json={"query": GRAPHQL_QUERY, "variables": {"id": 1}},
            timeout=5,
        )
        payload = gql.json()
        if gql.status_code != 200 or "errors" in payload:
            errors.append("GraphQL retornou erro na consulta de teste")
    except (requests.RequestException, json.JSONDecodeError, ValueError) as error:
        errors.append(f"GraphQL indisponivel: {error}")

    return not errors, errors


def should_enable_official_collection(failure_count: int) -> bool:
    return failure_count == 0


def run_validation_then_official(
    base_url: str = "http://localhost:4000",
    validation_output: str | Path = "validation_results.csv",
    official_output: str | Path = "results.csv",
) -> ExperimentSummary:
    ok, errors = validate_environment(base_url)
    if not ok:
        raise RuntimeError("; ".join(errors))

    validation = run_experiment(base_url, VALIDATION_ITERATIONS, validation_output)
    if not should_enable_official_collection(len(validation.failures)):
        raise RuntimeError("validacao registrou falhas; coleta oficial interrompida")

    return run_experiment(base_url, DEFAULT_ITERATIONS, official_output)


def count_successful_records(records: Iterable[Measurement]) -> int:
    return sum(1 for _ in records)
