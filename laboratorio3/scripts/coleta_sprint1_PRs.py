"""
Lab 03 - Sprint 01: Coleta de repositorios populares e seus Pull Requests com review.

Filtros aplicados (conforme enunciado):
  - 200 repositorios mais populares por estrelas (genericos, sem filtro de linguagem).
  - Apenas repositorios com pelo menos 100 PRs (MERGED + CLOSED).
  - Apenas PRs com status MERGED ou CLOSED.
  - Apenas PRs com pelo menos 1 review (total count do campo review).
  - Apenas PRs cuja diferenca entre criacao e fechamento (merge ou close) seja > 1 hora,
    para descartar revisoes automaticas (bots/CI).

Saidas em laboratorio3/output/lab3s2/:
  - top_200_repos.csv               -> repositorios alvo
  - pull_requests_com_reviews.csv   -> dataset principal de PRs
"""

import csv
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

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
POR_PAGINA = 100
MAX_PAGINAS_REPOS = 10
URL_BASE_REPOS = "https://api.github.com/search/repositories"
URL_BASE_PRS = "https://api.github.com/repos"
MAX_WORKERS = 12


def obter_cabecalhos() -> dict:
    load_dotenv(DIR_PROJETO / ".env")
    token = os.getenv("GITHUB_TOKEN", "").strip()
    cabecalhos = {"Accept": "application/vnd.github+json"}
    if token:
        cabecalhos["Authorization"] = f"Bearer {token}"
    return cabecalhos


def converter_iso_utc(valor: str) -> datetime:
    return datetime.fromisoformat(valor.replace("Z", "+00:00"))


def _get(url: str, cabecalhos: dict, params: Optional[dict] = None,
         timeout: int = 30, max_retries: int = 3) -> Optional[requests.Response]:
    """Wrapper de GET que respeita rate limit e tenta novamente em falhas transientes."""
    for tentativa in range(max_retries):
        try:
            resp = requests.get(url, headers=cabecalhos, params=params, timeout=timeout)
        except requests.RequestException:
            time.sleep(1.5 * (tentativa + 1))
            continue

        if resp.status_code == 200:
            return resp

        if resp.status_code in (403, 429):
            reset = resp.headers.get("X-RateLimit-Reset")
            remaining = resp.headers.get("X-RateLimit-Remaining", "?")
            if reset and remaining == "0":
                espera = max(int(reset) - int(time.time()), 1) + 2
                espera = min(espera, 120)
                print(f"    rate limit atingido, aguardando {espera}s...")
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

    for pagina in range(1, MAX_PAGINAS_REPOS + 1):
        parametros = {
            "q": "stars:>0",
            "sort": "stars",
            "order": "desc",
            "per_page": POR_PAGINA,
            "page": pagina,
        }
        resposta = _get(URL_BASE_REPOS, cabecalhos, parametros, timeout=60)
        if resposta is None or resposta.status_code != 200:
            raise RuntimeError("Falha na API do GitHub ao listar repositorios.")

        dados = resposta.json()
        itens = dados.get("items", [])
        for item in itens:
            if item.get("fork"):
                continue

            criado_em = converter_iso_utc(item["created_at"])
            atualizado_em = converter_iso_utc(item["pushed_at"])
            idade_dias = (agora - criado_em).days

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
                "dias_desde_ultimo_push": (agora - atualizado_em).days,
            })

            if len(repositorios) >= total:
                break

        print(f"Pagina {pagina}: {len(repositorios)}/{total} repositorios coletados.")
        if len(repositorios) >= total or not itens:
            break
        time.sleep(1.0)

    return repositorios[:total]


def contar_prs_fechados(dono: str, repo: str, cabecalhos: dict,
                         minimo: int = LIMITE_PRS_FECHADOS_REPO) -> int:
    """
    Conta PRs com state=closed (inclui MERGED+CLOSED na API do GitHub).

    Estrategia eficiente: pedir per_page=1 e olhar o header Link ('rel=last') para
    extrair o numero da ultima pagina, que equivale ao total. Para um numero <= minimo
    cai no fallback paginado.
    """
    url = f"{URL_BASE_PRS}/{dono}/{repo}/pulls"
    resp = _get(url, cabecalhos, params={"state": "closed", "per_page": 1}, timeout=30)
    if resp is None or resp.status_code != 200:
        return 0

    link = resp.headers.get("Link", "")
    if 'rel="last"' in link:
        for parte in link.split(","):
            if 'rel="last"' in parte:
                inicio = parte.find("<") + 1
                fim = parte.find(">")
                url_last = parte[inicio:fim]
                if "page=" in url_last:
                    try:
                        numero = int(url_last.split("page=")[-1].split("&")[0])
                        return numero
                    except ValueError:
                        return minimo

    try:
        primeiro_lote = resp.json()
        return len(primeiro_lote) if isinstance(primeiro_lote, list) else 0
    except Exception:
        return 0


def _obter_detalhes_pr(dono: str, repo: str, numero: int, cabecalhos: dict) -> Optional[dict]:
    url_pr = f"{URL_BASE_PRS}/{dono}/{repo}/pulls/{numero}"
    resp = _get(url_pr, cabecalhos, timeout=30)
    if resp is None or resp.status_code != 200:
        return None
    return resp.json()


def _listar_paginado(url: str, cabecalhos: dict) -> list[dict]:
    resultado: list[dict] = []
    pagina = 1
    while True:
        resp = _get(url, cabecalhos, params={"per_page": 100, "page": pagina}, timeout=30)
        if resp is None or resp.status_code != 200:
            break
        batch = resp.json()
        if not isinstance(batch, list) or not batch:
            break
        resultado.extend(batch)
        if len(batch) < 100:
            break
        pagina += 1
        time.sleep(0.05)
    return resultado


def _listar_comentarios_issue(dono: str, repo: str, numero: int,
                              cabecalhos: dict) -> list[dict]:
    return _listar_paginado(
        f"{URL_BASE_PRS}/{dono}/{repo}/issues/{numero}/comments", cabecalhos
    )


def _listar_reviews(dono: str, repo: str, numero: int,
                    cabecalhos: dict) -> list[dict]:
    return _listar_paginado(
        f"{URL_BASE_PRS}/{dono}/{repo}/pulls/{numero}/reviews", cabecalhos
    )


def _possui_review(dono: str, repo: str, numero: int, cabecalhos: dict) -> bool:
    """Check rapido: pede 1 review apenas. Se vazio -> nao tem review."""
    url = f"{URL_BASE_PRS}/{dono}/{repo}/pulls/{numero}/reviews"
    resp = _get(url, cabecalhos, params={"per_page": 1, "page": 1}, timeout=20)
    if resp is None or resp.status_code != 200:
        return False
    try:
        batch = resp.json()
        return isinstance(batch, list) and len(batch) >= 1
    except Exception:
        return False


def _atende_tempo_minimo(pr: dict) -> bool:
    """Filtra PR com tempo de analise > 1h usando created_at e closed_at/merged_at do listado."""
    criado = pr.get("created_at")
    fechado = pr.get("merged_at") or pr.get("closed_at")
    if not criado or not fechado:
        return False
    try:
        dt_c = converter_iso_utc(criado)
        dt_f = converter_iso_utc(fechado)
    except Exception:
        return False
    horas = (dt_f - dt_c).total_seconds() / 3600.0
    return horas > TEMPO_MIN_ANALISE_HORAS


def processar_pr(dono: str, repo: str, pr: dict, cabecalhos: dict,
                 lock: threading.Lock, prs_filtradas: list[dict]) -> None:
    """
    Aplica os filtros do enunciado e, se aprovado, calcula as metricas
    e adiciona o PR ao dataset.
    """
    try:
        numero = pr["number"]

        if not _atende_tempo_minimo(pr):
            return

        if not _possui_review(dono, repo, numero, cabecalhos):
            return

        detalhes = _obter_detalhes_pr(dono, repo, numero, cabecalhos)
        if not detalhes:
            return

        criado_em = converter_iso_utc(detalhes["created_at"])
        if detalhes.get("merged_at"):
            fechado_em = converter_iso_utc(detalhes["merged_at"])
            status = "MERGED"
        elif detalhes.get("closed_at"):
            fechado_em = converter_iso_utc(detalhes["closed_at"])
            status = "CLOSED"
        else:
            return

        tempo_analise_horas = (fechado_em - criado_em).total_seconds() / 3600.0
        if tempo_analise_horas <= TEMPO_MIN_ANALISE_HORAS:
            return

        reviews_completos = _listar_reviews(dono, repo, numero, cabecalhos)
        num_reviews = len(reviews_completos)
        if num_reviews < LIMITE_REVIEWS:
            return

        # Participantes: aproximacao por autor + revisores unicos + assignees +
        # requested_reviewers. Evita listar comentarios da issue para nao multiplicar
        # o numero de chamadas API por PR.
        participantes: set[str] = set()
        autor = (detalhes.get("user") or {}).get("login")
        if autor:
            participantes.add(autor)
        for r in reviews_completos:
            login = (r.get("user") or {}).get("login")
            if login:
                participantes.add(login)
        for assg in detalhes.get("assignees") or []:
            login = (assg or {}).get("login")
            if login:
                participantes.add(login)
        for rev in detalhes.get("requested_reviewers") or []:
            login = (rev or {}).get("login")
            if login:
                participantes.add(login)

        comments_count = int(detalhes.get("comments") or 0)
        review_comments_count = int(detalhes.get("review_comments") or 0)
        total_comentarios = comments_count + review_comments_count

        additions = int(detalhes.get("additions") or 0)
        deletions = int(detalhes.get("deletions") or 0)
        changed_files = int(detalhes.get("changed_files") or 0)

        corpo = detalhes.get("body") or ""
        descricao_tamanho = len(corpo)

        pr_dados = {
            "repo_completo": f"{dono}/{repo}",
            "numero_pr": numero,
            "titulo": detalhes.get("title"),
            "autora": autor,
            "status": status,
            "url": detalhes.get("html_url"),
            "criado_em": detalhes.get("created_at"),
            "atualizado_em": detalhes.get("updated_at"),
            "merged_em": detalhes.get("merged_at"),
            "closed_em": detalhes.get("closed_at"),
            "changed_files": changed_files,
            "additions": additions,
            "deletions": deletions,
            "loc_total": additions + deletions,
            "tempo_analise_horas": round(tempo_analise_horas, 4),
            "tempo_analise_dias": round(tempo_analise_horas / 24.0, 4),
            "descricao_tamanho_chars": descricao_tamanho,
            "num_participantes": len(participantes),
            "total_comentarios": total_comentarios,
            "numero_reviews": num_reviews,
        }

        with lock:
            prs_filtradas.append(pr_dados)
    except Exception as exc:
        print(f"    aviso: erro processando PR #{pr.get('number')} de {dono}/{repo}: {exc}")


def coletar_pull_requests(dono: str, repo: str, cabecalhos: dict) -> list[dict]:
    """
    Coleta lista bruta de PRs fechados (MERGED+CLOSED) e filtra os que
    satisfazem todos os criterios do experimento.
    """
    prs_brutos: list[dict] = []
    pagina = 1
    paginas_max = 5

    print(f"    coletando PRs fechados (paginas)...", end=" ", flush=True)
    while pagina <= paginas_max:
        url = f"{URL_BASE_PRS}/{dono}/{repo}/pulls"
        parametros = {
            "state": "closed",
            "sort": "updated",
            "direction": "desc",
            "per_page": 100,
            "page": pagina,
        }
        resp = _get(url, cabecalhos, parametros, timeout=60)
        if resp is None or resp.status_code != 200:
            break
        prs = resp.json()
        if not isinstance(prs, list) or not prs:
            break
        prs_brutos.extend(prs)
        if len(prs) < 100:
            break
        pagina += 1
        time.sleep(0.1)

    print(f"obtidos {len(prs_brutos)}.", end=" ", flush=True)
    print(f"avaliando filtros (review>=1, tempo>1h)...")

    prs_filtradas: list[dict] = []
    lock = threading.Lock()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(processar_pr, dono, repo, pr, cabecalhos, lock, prs_filtradas)
            for pr in prs_brutos
        ]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                print(f"    erro em future: {exc}")
            if len(prs_filtradas) >= TOTAL_PRS_POR_REPO:
                for f in futures:
                    f.cancel()
                break

    prs_filtradas.sort(
        key=lambda p: p.get("criado_em") or "", reverse=True
    )
    return prs_filtradas[:TOTAL_PRS_POR_REPO]


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
    print("LAB 03 - Coleta de repositorios e Pull Requests com code review")
    print("=" * 70)

    print(f"\n[1/3] Coletando top {TOTAL_REPOS} repositorios populares...")
    repositorios = coletar_repositorios()
    escrever_csv(repositorios, CAMINHO_CSV_REPOS, "repositorios")

    print("\n[2/3] Validando criterio de >=100 PRs fechados e coletando PRs com review...")
    cabecalhos = obter_cabecalhos()
    todos_prs: list[dict] = []
    repos_aceitos: list[str] = []
    repos_descartados: list[tuple[str, int]] = []

    for idx, repo in enumerate(repositorios, 1):
        nome_completo = repo["nome_completo"]
        dono = repo["dono"]
        nome_repo = repo["nome_repo"]
        print(f"  [{idx}/{len(repositorios)}] {nome_completo}")

        total_fechados = contar_prs_fechados(dono, nome_repo, cabecalhos)
        if total_fechados < LIMITE_PRS_FECHADOS_REPO:
            print(f"    descartado: apenas {total_fechados} PRs fechados (<{LIMITE_PRS_FECHADOS_REPO}).")
            repos_descartados.append((nome_completo, total_fechados))
            continue

        prs = coletar_pull_requests(dono, nome_repo, cabecalhos)
        if not prs:
            print(f"    aviso: 0 PRs aprovaram os filtros em {nome_completo}.")
            continue

        print(f"    aceito com {len(prs)} PRs apos filtros.")
        repos_aceitos.append(nome_completo)
        todos_prs.extend(prs)
        time.sleep(0.3)

        if idx % 20 == 0 and todos_prs:
            escrever_csv(todos_prs, CAMINHO_CSV_PRS, "pull requests (parcial)")

    print("\n[3/3] Salvando resultados finais...")
    escrever_csv(todos_prs, CAMINHO_CSV_PRS, "pull requests com reviews")

    print("\n" + "=" * 70)
    print("RESUMO DA COLETA")
    print("=" * 70)
    print(f"Repositorios candidatos:       {len(repositorios)}")
    print(f"Repositorios aceitos (>=100):  {len(repos_aceitos)}")
    print(f"Repositorios descartados:      {len(repos_descartados)}")
    print(f"Total de PRs no dataset:       {len(todos_prs)}")
    if repos_aceitos:
        print(f"Media de PRs por repo aceito:  {len(todos_prs)/len(repos_aceitos):.2f}")
    print(f"Saida: {DIR_SAIDA}")
    print("=" * 70)


if __name__ == "__main__":
    main()
