import csv
import os
import statistics
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

# ──────────────────── Caminhos ────────────────────
PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")
TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise ValueError("GITHUB_TOKEN nao encontrado. Defina em laboratorio1/.env")

URL = "https://api.github.com/graphql"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
TARGET_REPOS = 1000
PAGE_SIZE = 100
METRICS_BATCH_SIZE = 20
OUTPUT_DIR = PROJECT_DIR / "output"
CSV_PATH = OUTPUT_DIR / "top_1000_repos.csv"
REPORT_PATH = OUTPUT_DIR / "relatorio_sprint2.md"

BASIC_SEARCH_QUERY = """
query ($first: Int!, $after: String) {
  search(query: "stars:>0 sort:stars-desc", type: REPOSITORY, first: $first, after: $after) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      ... on Repository {
        name
        nameWithOwner
        url
        stargazerCount
        createdAt
        pushedAt
        primaryLanguage {
          name
        }
      }
    }
  }
  rateLimit {
    cost
    remaining
  }
}
"""


def run_query(query: str, variables: dict | None = None, retries: int = 6) -> dict:
    for attempt in range(1, retries + 1):
        response = requests.post(
            URL,
            json={"query": query, "variables": variables or {}},
            headers=HEADERS,
            timeout=90,
        )

        if response.status_code != 200:
            if response.status_code >= 500 and attempt < retries:
                time.sleep(5 * attempt)
                continue
            if attempt < retries:
                time.sleep(2 * attempt)
                continue
            raise RuntimeError(f"Falha HTTP {response.status_code}: {response.text}")

        payload = response.json()
        errors = payload.get("errors", [])
        if not errors:
            return payload

        msg = str(errors)
        if "rate limit" in msg.lower() and attempt < retries:
            time.sleep(30)
            continue
        raise RuntimeError(f"Erros GraphQL: {errors}")

    raise RuntimeError("Nao foi possivel concluir a query GraphQL")


def parse_iso_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def collect_top_repositories(total: int) -> tuple[list[dict], datetime]:
    now = datetime.now(timezone.utc)
    repos: list[dict] = []
    cursor = None
    page = 0

    while len(repos) < total:
        page += 1
        variables = {"first": PAGE_SIZE, "after": cursor}
        data = run_query(BASIC_SEARCH_QUERY, variables)
        search_data = data["data"]["search"]
        rate = data["data"]["rateLimit"]

        nodes = [node for node in search_data["nodes"] if node is not None]
        skipped = 0
        for node in nodes:
            # Filtra apenas repositorios que possuem linguagem de programacao
            if not node.get("primaryLanguage") or not node["primaryLanguage"].get("name"):
                skipped += 1
                continue

            created_at = parse_iso_utc(node["createdAt"])
            pushed_at = parse_iso_utc(node["pushedAt"])
            age_days = (now - created_at).days
            days_since_last_push = (now - pushed_at).days

            language = node["primaryLanguage"]["name"]

            owner, repo_name = node["nameWithOwner"].split("/", 1)
            repos.append(
                {
                    "full_name": node["nameWithOwner"],
                    "repo_name": repo_name,
                    "owner": owner,
                    "url": node["url"],
                    "stars": node["stargazerCount"],
                    "primary_language": language,
                    "created_at": node["createdAt"],
                    "pushed_at": node["pushedAt"],
                    "age_days": age_days,
                    "age_years": round(age_days / 365.25, 4),
                    "merged_prs": 0,
                    "total_releases": 0,
                    "total_issues": 0,
                    "closed_issues": 0,
                    "closed_issues_ratio": 0.0,
                    "closed_issues_percent": 0.0,
                    "days_since_last_push": days_since_last_push,
                }
            )

            if len(repos) >= total:
                break

        print(
            f"Busca base pagina {page}: {len(repos)}/{total} repos "
            f"(rate restante: {rate['remaining']}, custo: {rate['cost']}, "
            f"descartados sem linguagem: {skipped})"
        )

        if len(repos) >= total or not search_data["pageInfo"]["hasNextPage"]:
            break

        cursor = search_data["pageInfo"]["endCursor"]
        time.sleep(0.2)

    return repos[:total], now


def build_metrics_query(batch: list[dict]) -> str:
    parts = []
    for idx, repo in enumerate(batch):
        owner = repo["owner"].replace('"', "")
        name = repo["repo_name"].replace('"', "")
        parts.append(
            f"""
            r{idx}: repository(owner: \"{owner}\", name: \"{name}\") {{
              pullRequests(states: MERGED) {{ totalCount }}
              releases {{ totalCount }}
              issues {{ totalCount }}
              closedIssues: issues(states: CLOSED) {{ totalCount }}
            }}
            """
        )
    joined = "\n".join(parts)
    return f"query {{\n{joined}\nrateLimit {{ cost remaining }}\n}}"


def apply_metrics_to_batch(batch: list[dict], result: dict) -> None:
    for idx, repo in enumerate(batch):
        key = f"r{idx}"
        metrics = result.get(key)
        if metrics is None:
            continue

        total_issues = metrics["issues"]["totalCount"]
        closed_issues = metrics["closedIssues"]["totalCount"]
        closed_ratio = (closed_issues / total_issues) if total_issues else 0.0

        repo["merged_prs"] = metrics["pullRequests"]["totalCount"]
        repo["total_releases"] = metrics["releases"]["totalCount"]
        repo["total_issues"] = total_issues
        repo["closed_issues"] = closed_issues
        repo["closed_issues_ratio"] = round(closed_ratio, 6)
        repo["closed_issues_percent"] = round(closed_ratio * 100, 2)


def enrich_with_metrics(repos: list[dict], batch_size: int = METRICS_BATCH_SIZE) -> None:
    total = len(repos)
    queue: list[tuple[int, int]] = [
        (start, min(start + batch_size, total)) for start in range(0, total, batch_size)
    ]
    completed = 0

    while queue:
        start, end = queue.pop(0)
        batch = repos[start:end]
        query = build_metrics_query(batch)

        try:
            data = run_query(query)
            result = data["data"]
            rate = result["rateLimit"]
            apply_metrics_to_batch(batch, result)
            completed += len(batch)
            print(
                f"Metricas {completed}/{total} repos "
                f"(rate restante: {rate['remaining']}, custo: {rate['cost']})"
            )
            time.sleep(0.2)
        except Exception as exc:
            if len(batch) == 1:
                print(f"Falha definitiva em {batch[0]['full_name']}: {exc}")
                continue
            middle = start + len(batch) // 2
            queue.insert(0, (middle, end))
            queue.insert(0, (start, middle))


def median(values: list[float]) -> float:
    return float(statistics.median(values)) if values else 0.0


def build_summary(repos: list[dict]) -> dict:
    languages = Counter(repo["primary_language"] for repo in repos)
    by_language: dict[str, list[dict]] = defaultdict(list)
    for repo in repos:
        by_language[repo["primary_language"]].append(repo)

    language_breakdown = []
    for language, group in sorted(by_language.items(), key=lambda item: len(item[1]), reverse=True):
        language_breakdown.append(
            {
                "language": language,
                "repos": len(group),
                "median_merged_prs": round(median([r["merged_prs"] for r in group]), 2),
                "median_releases": round(median([r["total_releases"] for r in group]), 2),
                "median_days_since_last_push": round(median([r["days_since_last_push"] for r in group]), 2),
            }
        )

    return {
        "rq01_median_age_years": round(median([repo["age_years"] for repo in repos]), 2),
        "rq02_median_merged_prs": round(median([repo["merged_prs"] for repo in repos]), 2),
        "rq03_median_releases": round(median([repo["total_releases"] for repo in repos]), 2),
        "rq04_median_days_since_last_push": round(median([repo["days_since_last_push"] for repo in repos]), 2),
        "rq06_median_closed_issues_percent": round(median([repo["closed_issues_percent"] for repo in repos]), 2),
        "languages": languages,
        "language_breakdown": language_breakdown,
    }


def write_csv(repos: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(repos[0].keys()))
        writer.writeheader()
        writer.writerows(repos)


def render_language_counts(counter: Counter, top_n: int = 15) -> str:
    lines = ["| Linguagem | Quantidade |", "|---|---:|"]
    for language, count in counter.most_common(top_n):
        lines.append(f"| {language} | {count} |")
    return "\n".join(lines)


def render_rq07_table(rows: list[dict], top_n: int = 15) -> str:
    lines = [
        "| Linguagem | Repos | Mediana PRs aceitas | Mediana releases | Mediana dias sem push |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in rows[:top_n]:
        lines.append(
            f"| {row['language']} | {row['repos']} | {row['median_merged_prs']} | "
            f"{row['median_releases']} | {row['median_days_since_last_push']} |"
        )
    return "\n".join(lines)


def write_report(summary: dict, collected_at: datetime, report_path: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)

    report = f"""# Laboratorio 1 - Sprint 2

## 1. Introducao e hipoteses informais

Este documento apresenta a primeira versao do relatorio para os 1.000 repositorios mais estrelados do GitHub.

Hipoteses informais (antes da analise):
- H1 (RQ01): repositorios populares tendem a ser mais antigos e maduros.
- H2 (RQ02): repositorios populares recebem volume alto de contribuicao externa (PRs aceitas).
- H3 (RQ03): repositorios populares fazem releases com frequencia moderada/alta.
- H4 (RQ04): repositorios populares costumam ter atualizacoes recentes.
- H5 (RQ05): linguagens populares (JavaScript, TypeScript, Python, Java, Go, C++) devem aparecer com mais frequencia.
- H6 (RQ06): repositorios populares devem ter percentual alto de issues fechadas.
- H7 (RQ07 - bonus): repositorios de linguagens mais populares devem concentrar mais contribuicoes, mais releases e menor tempo sem atualizacao.

Data/hora da coleta (UTC): {collected_at.strftime("%Y-%m-%d %H:%M:%S")}
Tamanho da amostra: 1000 repositorios.

## 2. Metodologia

- Fonte de dados: API GraphQL do GitHub.
- Criterio de selecao: `search(query: "stars:>0 sort:stars-desc", type: REPOSITORY)` com paginacao.
- Pagina: 100 repositorios por requisicao; 10 paginas para coletar 1000 itens.
- Metricas de RQ02, RQ03 e RQ06 coletadas em lotes de 20 repositorios por query GraphQL.
- Cada repositorio foi coletado com:
  - idade (dias/anos) via `createdAt`.
  - PRs aceitas via `pullRequests(states: MERGED).totalCount`.
  - releases via `releases.totalCount`.
  - tempo sem atualizacao via diferenca entre coleta e `pushedAt`.
  - linguagem primaria via `primaryLanguage.name`.
  - razao de issues fechadas via `issues(states: CLOSED).totalCount / issues.totalCount`.

## 3. Resultados por RQ (medianas)

- RQ01 (idade): mediana de **{summary['rq01_median_age_years']} anos**.
- RQ02 (PRs aceitas): mediana de **{summary['rq02_median_merged_prs']} PRs**.
- RQ03 (releases): mediana de **{summary['rq03_median_releases']} releases**.
- RQ04 (tempo ate ultimo push): mediana de **{summary['rq04_median_days_since_last_push']} dias**.
- RQ05 (linguagem primaria): distribuicao das linguagens no top 1000:

{render_language_counts(summary["languages"])}

- RQ06 (percentual de issues fechadas): mediana de **{summary['rq06_median_closed_issues_percent']}%**.

## 4. Bonus - RQ07 (analise por linguagem)

{render_rq07_table(summary["language_breakdown"])}

## 5. Discussao inicial (hipoteses x resultados)

- RQ01: a mediana de idade indica o nivel de maturidade dos sistemas populares.
- RQ02: a mediana de PRs aceitas mostra se a contribuicao externa tende a ser alta.
- RQ03: a mediana de releases mostra o ritmo de empacotamento/publicacao.
- RQ04: dias sem update refletem atividade recente de manutencao.
- RQ05: a distribuicao por linguagem permite verificar se o top 1000 acompanha linguagens populares.
- RQ06: a mediana de fechamento de issues indica eficiencia geral no tratamento de demandas.
- RQ07: a comparacao por linguagem ajuda a identificar diferencas de dinamica entre ecossistemas.

## 6. Arquivos gerados

- CSV com dados brutos: `output/top_1000_repos.csv`
- Este relatorio: `output/relatorio_sprint2.md`
"""
    report_path.write_text(report, encoding="utf-8")


def main() -> None:
    print("Iniciando coleta da Sprint 2 (1000 repositorios)...")
    repos, collected_at = collect_top_repositories(TARGET_REPOS)

    print("Coletando metricas por lote...")
    enrich_with_metrics(repos)

    print("Gerando CSV...")
    write_csv(repos, CSV_PATH)

    print("Calculando sumarizacao...")
    summary = build_summary(repos)

    print("Gerando relatorio...")
    write_report(summary, collected_at, REPORT_PATH)

    print("Concluido.")
    print(f"CSV: {CSV_PATH}")
    print(f"Relatorio: {REPORT_PATH}")


if __name__ == "__main__":
    main()
