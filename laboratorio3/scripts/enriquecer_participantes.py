"""
Lab 03 - Enriquecimento: adiciona num_participantes ao dataset principal.

Le `output/lab3s2/pull_requests_com_reviews.csv` (sem num_participantes) e
para cada PR consulta GitHub via REST `/issues/{n}/participants` (na pratica
nao existe esse endpoint; usamos GraphQL via global node id) ou via uma query
GraphQL batched que pega `participants.totalCount` de varios PRs por chamada.

Estrategia adotada:
  - Para cada repo do CSV, executa uma sequencia de queries GraphQL com
    aliases (ex.: pr0: pullRequest(number: 12) { participants { totalCount } })
    em lotes de PR_BATCH PRs por query. Isso fica dentro do orcamento de
    complexidade do GitHub mesmo com o campo participants.

Saida:
  - sobrescreve `output/lab3s2/pull_requests_com_reviews.csv` adicionando a
    coluna `num_participantes`.
  - cria um backup em
    `output/lab3s2/pull_requests_com_reviews_sem_participantes.csv`.
"""

from __future__ import annotations

import os
import shutil
import time
from pathlib import Path
from typing import Optional

import pandas as pd
import requests
from dotenv import load_dotenv

DIR_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_CSV = DIR_PROJETO / "output" / "lab3s2" / "pull_requests_com_reviews.csv"
CAMINHO_BACKUP = DIR_PROJETO / "output" / "lab3s2" / "pull_requests_com_reviews_sem_participantes.csv"
URL_GRAPHQL = "https://api.github.com/graphql"

PR_BATCH = 30
MAX_RETRIES = 4


def obter_cabecalhos() -> dict:
    load_dotenv(DIR_PROJETO / ".env")
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if not token:
        raise SystemExit("GITHUB_TOKEN ausente em .env.")
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }


def _gql(query: str, cabecalhos: dict) -> Optional[dict]:
    for tentativa in range(MAX_RETRIES):
        try:
            resp = requests.post(URL_GRAPHQL, headers=cabecalhos,
                                 json={"query": query}, timeout=60)
        except requests.RequestException:
            time.sleep(2.0 * (tentativa + 1))
            continue
        if resp.status_code in (502, 503, 504):
            time.sleep(2.0 * (tentativa + 1))
            continue
        if resp.status_code == 200:
            try:
                payload = resp.json()
            except Exception:
                time.sleep(1.0)
                continue
            return payload
        if resp.status_code in (403, 429):
            reset = resp.headers.get("X-RateLimit-Reset")
            espera = 5
            if reset:
                espera = max(int(reset) - int(time.time()), 1) + 2
                espera = min(espera, 120)
            time.sleep(espera)
            continue
        return None
    return None


def montar_query(dono: str, repo: str, numeros_pr: list[int]) -> str:
    """
    Monta uma query GraphQL com aliases (pr<n>) consultando participants
    apenas para uma lista de PRs do mesmo repositorio.
    """
    blocos = []
    for n in numeros_pr:
        blocos.append(
            f"  pr{n}: pullRequest(number: {n}) {{ "
            f"number participants {{ totalCount }} }}"
        )
    blocos_str = "\n".join(blocos)
    return (
        f"query {{\n"
        f'  repository(owner: "{dono}", name: "{repo}") {{\n'
        f"{blocos_str}\n"
        f"  }}\n"
        f"  rateLimit {{ remaining resetAt cost }}\n"
        f"}}\n"
    )


def enriquecer(df: pd.DataFrame, cabecalhos: dict) -> pd.DataFrame:
    if "num_participantes" in df.columns:
        df = df.drop(columns=["num_participantes"])
    df["num_participantes"] = pd.NA

    grupos = df.groupby("repo_completo")
    total_grupos = len(grupos)
    inicio = time.time()
    para_processar = sum(len(sub) for _, sub in grupos)
    feitos = 0

    for idx, (repo_full, sub) in enumerate(grupos, 1):
        dono, repo = repo_full.split("/", 1)
        numeros = sub["numero_pr"].astype(int).tolist()

        for ini in range(0, len(numeros), PR_BATCH):
            lote = numeros[ini:ini + PR_BATCH]
            query = montar_query(dono, repo, lote)
            payload = _gql(query, cabecalhos)
            if payload is None or "data" not in payload:
                continue

            repo_data = (payload.get("data") or {}).get("repository") or {}
            for n in lote:
                node = repo_data.get(f"pr{n}")
                if node and isinstance(node, dict):
                    parts = node.get("participants")
                    if parts and isinstance(parts, dict):
                        df.loc[
                            (df["repo_completo"] == repo_full) & (df["numero_pr"] == n),
                            "num_participantes",
                        ] = int(parts.get("totalCount") or 0)

            feitos += len(lote)

            elapsed = time.time() - inicio
            print(
                f"  [{idx}/{total_grupos}] {repo_full}: "
                f"PRs processados {feitos}/{para_processar} "
                f"(elapsed={elapsed:.0f}s)",
                flush=True,
            )

            rl = (payload.get("data") or {}).get("rateLimit") or {}
            if rl.get("remaining") is not None and rl["remaining"] < 50:
                espera = 30
                print(f"    rate limit baixo (remaining={rl['remaining']}), aguardando {espera}s")
                time.sleep(espera)

    return df


def main() -> None:
    if not CAMINHO_CSV.exists():
        raise SystemExit(f"CSV nao encontrado: {CAMINHO_CSV}")

    if not CAMINHO_BACKUP.exists():
        shutil.copy2(CAMINHO_CSV, CAMINHO_BACKUP)
        print(f"backup salvo: {CAMINHO_BACKUP}")

    cabecalhos = obter_cabecalhos()
    df = pd.read_csv(CAMINHO_CSV)
    print(f"PRs a enriquecer: {len(df)} | repos: {df['repo_completo'].nunique()}")

    df = enriquecer(df, cabecalhos)
    df.to_csv(CAMINHO_CSV, index=False)
    sem_part = df["num_participantes"].isna().sum()
    print(f"\nOK CSV atualizado: {CAMINHO_CSV}")
    print(f"   PRs sem num_participantes (falha de coleta): {sem_part}")


if __name__ == "__main__":
    main()
