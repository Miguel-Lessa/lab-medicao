"""
Lab 03 - Sprint 01/02: Coleta otimizada via GitHub GraphQL API.

Usa a API GraphQL para reduzir drasticamente o numero de chamadas: cada query
retorna ate 100 PRs com TODOS os campos necessarios (additions, deletions,
changedFiles, body, reviews count, comments count, participants count,
created/closed/merged dates), eliminando a necessidade das varias chamadas
REST por PR.

Filtros aplicados (conforme enunciado):
  - 200 repositorios mais populares (estrelas).
  - Repositorio precisa ter >=100 PRs MERGED+CLOSED.
  - PR com status MERGED ou CLOSED.
  - PR com pelo menos 1 review.
  - PR com tempo (criacao -> fechamento) > 1 hora (descarta bots/CI).

Saidas em laboratorio3/output/lab3s2/:
  - top_200_repos.csv
  - pull_requests_com_reviews.csv
"""

import csv
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Any

import requests
from dotenv import load_dotenv

DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_SAIDA = DIR_PROJETO / "output" / "lab3s2"
CAMINHO_CSV_REPOS = DIR_SAIDA / "top_200_repos.csv"
CAMINHO_CSV_PRS = DIR_SAIDA / "pull_requests_com_reviews.csv"

TOTAL_REPOS = 200
TOTAL_PRS_POR_REPO = 100
LIMITE_REVIEWS = 1
LIMITE_PRS_FECHADOS_REPO = 100
TEMPO_MIN_ANALISE_HORAS = 1.0
GRAPHQL_PAGE = 100  # com participants removido, 100 cabe no orcamento
MAX_PAGINAS_PR_POR_REPO = 6  # 100 * 6 = 600 PRs brutos no maximo

URL_REST_REPOS = "https://api.github.com/search/repositories"
URL_GRAPHQL = "https://api.github.com/graphql"

QUERY_PRS = """
query ($owner: String!, $repo: String!, $cursor: String, $page: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequests(states: [MERGED, CLOSED], first: $page, after: $cursor,
                 orderBy: {field: UPDATED_AT, direction: DESC}) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        number
        title
        url
        state
        createdAt
        closedAt
        mergedAt
        body
        additions
        deletions
        changedFiles
        author { login }
        comments { totalCount }
        reviews { totalCount }
      }
    }
  }
  rateLimit {
    remaining
    resetAt
    cost
  }
}
"""


def obter_cabecalhos() -> dict:
    load_dotenv(DIR_PROJETO / ".env")
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if not token:
        raise SystemExit("GITHUB_TOKEN ausente em .env. Configure antes de coletar.")
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }


def converter_iso_utc(valor: str) -> datetime:
    return datetime.fromisoformat(valor.replace("Z", "+00:00"))


def _gql(query: str, variaveis: dict, cabecalhos: dict,
         max_retries: int = 4) -> Optional[dict]:
    for tentativa in range(max_retries):
        try:
            resp = requests.post(
                URL_GRAPHQL,
                headers=cabecalhos,
                json={"query": query, "variables": variaveis},
                timeout=60,
            )
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
            if "errors" in payload and payload.get("errors"):
                # se o erro for rate limit, espera e tenta novamente
                msg = str(payload["errors"]).lower()
                if "rate limit" in msg:
                    time.sleep(60)
                    continue
                # erros de schema/permissao -> nao adianta repetir
                return payload
            return payload

        if resp.status_code in (403, 429):
            reset = resp.headers.get("X-RateLimit-Reset")
            if reset:
                espera = max(int(reset) - int(time.time()), 1) + 2
                espera = min(espera, 120)
                print(f"    rate limit, aguardando {espera}s...")
                time.sleep(espera)
                continue
            time.sleep(5.0 * (tentativa + 1))
            continue

        return None
    return None


def _rest_get(url: str, cabecalhos: dict, params: Optional[dict] = None,
              max_retries: int = 3) -> Optional[requests.Response]:
    for tentativa in range(max_retries):
        try:
            resp = requests.get(url, headers=cabecalhos, params=params, timeout=60)
        except requests.RequestException:
            time.sleep(1.5 * (tentativa + 1))
            continue
        if resp.status_code == 200:
            return resp
        if resp.status_code in (403, 429):
            reset = resp.headers.get("X-RateLimit-Reset")
            if reset:
                espera = max(int(reset) - int(time.time()), 1) + 2
                espera = min(espera, 120)
                time.sleep(espera)
                continue
            time.sleep(2.0 * (tentativa + 1))
            continue
        if resp.status_code in (502, 503, 504):
            time.sleep(2.0 * (tentativa + 1))
            continue
        return resp
    return None


def coletar_repositorios(total: int = TOTAL_REPOS) -> list[dict]:
    cabecalhos = obter_cabecalhos()
    agora = datetime.now(timezone.utc)
    repositorios: list[dict] = []

    for pagina in range(1, 11):
        parametros = {
            "q": "stars:>0",
            "sort": "stars",
            "order": "desc",
            "per_page": 100,
            "page": pagina,
        }
        resposta = _rest_get(URL_REST_REPOS, cabecalhos, parametros)
        if resposta is None or resposta.status_code != 200:
            raise RuntimeError("Falha na API ao listar repositorios.")

        dados = resposta.json()
        itens = dados.get("items", [])
        for item in itens:
            if item.get("fork"):
                continue
            criado = converter_iso_utc(item["created_at"])
            push = converter_iso_utc(item["pushed_at"])
            idade_dias = (agora - criado).days
            repositorios.append({
                "nome_completo": item["full_name"],
                "nome_repo": item["name"],
                "dono": item["owner"]["login"],
                "url": item["html_url"],
                "estrelas": item["stargazers_count"],
                "criado_em": item["created_at"],
                "atualizado_em": item["pushed_at"],
                "idade_dias": idade_dias,
                "idade_anos": round(idade_dias / 365.25, 4),
                "dias_desde_ultimo_push": (agora - push).days,
            })
            if len(repositorios) >= total:
                break

        print(f"Pagina {pagina}: {len(repositorios)}/{total} repositorios coletados.")
        if len(repositorios) >= total or not itens:
            break
        time.sleep(0.5)

    return repositorios[:total]


def processar_pr_node(node: dict, dono: str, repo: str) -> Optional[dict]:
    """Aplica filtros e converte um node GraphQL em registro CSV."""
    state = (node.get("state") or "").upper()
    if state not in ("MERGED", "CLOSED"):
        return None

    num_reviews = (node.get("reviews") or {}).get("totalCount") or 0
    if num_reviews < LIMITE_REVIEWS:
        return None

    criado = node.get("createdAt")
    fechado = node.get("mergedAt") or node.get("closedAt")
    if not criado or not fechado:
        return None

    try:
        dt_c = converter_iso_utc(criado)
        dt_f = converter_iso_utc(fechado)
    except Exception:
        return None

    horas = (dt_f - dt_c).total_seconds() / 3600.0
    if horas <= TEMPO_MIN_ANALISE_HORAS:
        return None

    additions = int(node.get("additions") or 0)
    deletions = int(node.get("deletions") or 0)
    changed_files = int(node.get("changedFiles") or 0)
    corpo = node.get("body") or ""

    comments_count = int((node.get("comments") or {}).get("totalCount") or 0)
    # Mantemos `total_comentarios` como APENAS comentarios da issue (independente
    # de numero_reviews) para nao introduzir circularidade nas analises da
    # Dimensao B (variavel dependente = numero_reviews).
    total_comentarios = comments_count

    autor = (node.get("author") or {}).get("login") if node.get("author") else None

    return {
        "repo_completo": f"{dono}/{repo}",
        "numero_pr": node.get("number"),
        "titulo": node.get("title"),
        "autora": autor,
        "status": state,
        "url": node.get("url"),
        "criado_em": criado,
        "merged_em": node.get("mergedAt"),
        "closed_em": node.get("closedAt"),
        "changed_files": changed_files,
        "additions": additions,
        "deletions": deletions,
        "loc_total": additions + deletions,
        "tempo_analise_horas": round(horas, 4),
        "tempo_analise_dias": round(horas / 24.0, 4),
        "descricao_tamanho_chars": len(corpo),
        "total_comentarios": total_comentarios,
        "numero_reviews": num_reviews,
    }


def coletar_prs_repo(dono: str, repo: str, cabecalhos: dict) -> tuple[int, list[dict]]:
    """
    Pagina ate MAX_PAGINAS_PR_POR_REPO ou ate aceitar TOTAL_PRS_POR_REPO PRs.
    Retorna (total_count_no_repo, lista_de_prs_aceitos).
    """
    aceitos: list[dict] = []
    cursor: Optional[str] = None
    total_count = 0
    paginas = 0
    descartados_tempo = 0
    descartados_review = 0

    while paginas < MAX_PAGINAS_PR_POR_REPO:
        payload = _gql(
            QUERY_PRS,
            {"owner": dono, "repo": repo, "cursor": cursor, "page": GRAPHQL_PAGE},
            cabecalhos,
        )
        if payload is None:
            print("    aviso: GraphQL retornou None (pulando pagina).")
            break
        # Mesmo com errors parciais, payload['data'] pode trazer nodes validos.
        if "errors" in payload and payload.get("errors"):
            erros_unicos = {e.get("type") for e in payload["errors"] if isinstance(e, dict)}
            print(f"    aviso GraphQL (parcial): {erros_unicos}")

        repo_data = (payload.get("data") or {}).get("repository")
        if repo_data is None:
            break
        prs = repo_data.get("pullRequests") or {}
        total_count = prs.get("totalCount") or total_count
        nodes = prs.get("nodes") or []

        for node in nodes:
            registro = processar_pr_node(node, dono, repo)
            if registro is None:
                state = (node.get("state") or "").upper()
                if state in ("MERGED", "CLOSED"):
                    n_rev = (node.get("reviews") or {}).get("totalCount") or 0
                    if n_rev < LIMITE_REVIEWS:
                        descartados_review += 1
                    else:
                        descartados_tempo += 1
                continue
            aceitos.append(registro)
            if len(aceitos) >= TOTAL_PRS_POR_REPO:
                break

        page_info = prs.get("pageInfo") or {}
        if len(aceitos) >= TOTAL_PRS_POR_REPO:
            break
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")
        paginas += 1

        rl = (payload.get("data") or {}).get("rateLimit") or {}
        if rl.get("remaining") is not None and rl["remaining"] < 100:
            print(f"    rateLimit GraphQL baixo: remaining={rl['remaining']}")

    print(f"    aceitos {len(aceitos)} / total_count={total_count} "
          f"(descartados: {descartados_tempo} tempo, {descartados_review} sem review)")
    return total_count, aceitos[:TOTAL_PRS_POR_REPO]


def escrever_csv(linhas: list[dict], caminho_saida: Path, descricao: str) -> None:
    if not linhas:
        print(f"aviso: nenhum dado coletado para {descricao}.")
        return
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list({k for linha in linhas for k in linha.keys()})
    prioridade = [
        "repo_completo", "numero_pr", "titulo", "autora", "status", "url",
        "criado_em", "merged_em", "closed_em",
        "changed_files", "additions", "deletions", "loc_total",
        "tempo_analise_horas", "tempo_analise_dias",
        "descricao_tamanho_chars", "num_participantes", "total_comentarios",
        "numero_reviews",
    ]
    ordered = [k for k in prioridade if k in fieldnames]
    ordered += sorted([k for k in fieldnames if k not in prioridade])
    with caminho_saida.open("w", newline="", encoding="utf-8") as fp:
        escritor = csv.DictWriter(fp, fieldnames=ordered)
        escritor.writeheader()
        for linha in linhas:
            escritor.writerow(linha)
    print(f"OK CSV gerado: {caminho_saida} ({len(linhas)} registros)")


def main() -> None:
    print("=" * 70)
    print("LAB 03 (GraphQL) - Coleta de repositorios e Pull Requests")
    print("=" * 70)

    print(f"\n[1/3] Coletando top {TOTAL_REPOS} repositorios populares...")
    repositorios = coletar_repositorios()
    escrever_csv(repositorios, CAMINHO_CSV_REPOS, "repositorios")

    print("\n[2/3] Coletando PRs via GraphQL...")
    cabecalhos = obter_cabecalhos()
    todos_prs: list[dict] = []
    aceitos_repos: list[str] = []
    descartados_repos: list[tuple[str, int]] = []

    inicio = time.time()
    for idx, repo in enumerate(repositorios, 1):
        nome_completo = repo["nome_completo"]
        dono = repo["dono"]
        nome_repo = repo["nome_repo"]
        elapsed = time.time() - inicio
        print(f"  [{idx}/{len(repositorios)}] {nome_completo} (elapsed={elapsed:.0f}s)")

        try:
            total_count, prs = coletar_prs_repo(dono, nome_repo, cabecalhos)
        except Exception as exc:
            print(f"    erro: {exc}")
            continue

        if total_count < LIMITE_PRS_FECHADOS_REPO:
            print(f"    descartado: apenas {total_count} PRs MERGED+CLOSED no repo.")
            descartados_repos.append((nome_completo, total_count))
            continue

        if not prs:
            print(f"    aviso: 0 PRs aprovados em {nome_completo} (total no repo={total_count}).")
            continue

        aceitos_repos.append(nome_completo)
        todos_prs.extend(prs)

        if idx % 10 == 0 and todos_prs:
            escrever_csv(todos_prs, CAMINHO_CSV_PRS, "pull requests (parcial)")

    print("\n[3/3] Salvando resultados finais...")
    escrever_csv(todos_prs, CAMINHO_CSV_PRS, "pull requests com reviews")

    print("\n" + "=" * 70)
    print("RESUMO DA COLETA (GraphQL)")
    print("=" * 70)
    print(f"Repositorios candidatos:       {len(repositorios)}")
    print(f"Repositorios aceitos (>=100):  {len(aceitos_repos)}")
    print(f"Repositorios descartados:      {len(descartados_repos)}")
    print(f"Total de PRs no dataset:       {len(todos_prs)}")
    if aceitos_repos:
        print(f"Media de PRs por repo aceito:  {len(todos_prs)/len(aceitos_repos):.2f}")
    print(f"Saida: {DIR_SAIDA}")
    print("=" * 70)


if __name__ == "__main__":
    main()
