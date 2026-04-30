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
DIR_SAIDA = DIR_PROJETO / "output"
CAMINHO_CSV_REPOS = DIR_SAIDA / "top_200_repos.csv"
CAMINHO_CSV_PRS = DIR_SAIDA / "pull_requests_com_reviews.csv"

TOTAL_REPOS = 200
TOTAL_PRS_POR_REPO = 100  # PRs final a salvar por repo
LIMITE_REVIEWS = 1  # Mínimo de reviews
POR_PAGINA = 100
MAX_PAGINAS = 10
URL_BASE_REPOS = "https://api.github.com/search/repositories"
URL_BASE_PRS = "https://api.github.com/repos"
MAX_WORKERS = 5  # Threads paralelas para verificar reviews


def obter_cabecalhos() -> dict:
    load_dotenv(DIR_PROJETO / ".env")
    token = os.getenv("GITHUB_TOKEN", "").strip()
    cabecalhos = {"Accept": "application/vnd.github+json"}
    if token:
        cabecalhos["Authorization"] = f"Bearer {token}"
    return cabecalhos


def converter_iso_utc(valor: str) -> datetime:
    return datetime.fromisoformat(valor.replace("Z", "+00:00"))


def coletar_repositorios(total: int = TOTAL_REPOS) -> list[dict]:
    cabecalhos = obter_cabecalhos()
    agora = datetime.now(timezone.utc)
    repositorios: list[dict] = []

    for pagina in range(1, MAX_PAGINAS + 1):
        parametros = {
            "q": "stars:>0",
            "sort": "stars",
            "order": "desc",
            "per_page": POR_PAGINA,
            "page": pagina,
        }
        resposta = requests.get(
            URL_BASE_REPOS, headers=cabecalhos, params=parametros, timeout=60
        )
        if resposta.status_code != 200:
            raise RuntimeError(
                f"Falha na API do GitHub (HTTP {resposta.status_code}): {resposta.text}"
            )

        dados = resposta.json()
        itens = dados.get("items", [])
        for item in itens:
            linguagem = (item.get("language") or "").lower()
            descricao = (item.get("description") or "").lower()
            nome = (item.get("name") or "").lower()

            linguagens_excluidas = {
                "", "markdown", "jupyter notebook",
            }

            if linguagem in linguagens_excluidas:
                continue

            palavras_bloqueadas = {
                "book", "books", "livro",
                "course", "curso", "tutorial",
                "awesome", "list", "roadmap",
                "interview", "questions",
                "guide", "guia",
                "notes", "anotações",
                "documentation", "docs"
            }

            texto = f"{nome} {descricao}"
            if any(p in texto for p in palavras_bloqueadas):
                continue

            if item.get("fork"):
                continue

            criado_em = converter_iso_utc(item["created_at"])
            atualizado_em = converter_iso_utc(item["pushed_at"])
            idade_dias = (agora - criado_em).days

            repositorios.append(
                {
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
                }
            )

            if len(repositorios) >= total:
                break

        print(f"Página {pagina}: {len(repositorios)}/{total} repositórios coletados.")
        if len(repositorios) >= total or not itens:
            break
        time.sleep(1.0)

    return repositorios[:total]


def _obter_detalhes_pr(dono: str, repo: str, numero: int, cabecalhos: dict) -> Optional[dict]:
    """
    Busca detalhes completos do PR (inclui additions, deletions, changed_files, body, comments, review_comments, closed_at).
    """
    url_pr = f"{URL_BASE_PRS}/{dono}/{repo}/pulls/{numero}"
    try:
        resp = requests.get(url_pr, headers=cabecalhos, timeout=30)
        if resp.status_code != 200:
            return None
        return resp.json()
    except Exception:
        return None


def _listar_comentarios_issue(dono: str, repo: str, numero: int, cabecalhos: dict) -> list[dict]:
    """
    Comentários da issue (PR) — conversas no tópico principal.
    """
    comentarios = []
    pagina = 1
    while True:
        url = f"{URL_BASE_PRS}/{dono}/{repo}/issues/{numero}/comments"
        try:
            resp = requests.get(url, headers=cabecalhos, params={"per_page": 100, "page": pagina}, timeout=20)
            if resp.status_code != 200:
                break
            batch = resp.json()
            if not batch:
                break
            comentarios.extend(batch)
            if len(batch) < 100:
                break
            pagina += 1
            time.sleep(0.1)
        except Exception:
            break
    return comentarios


def _listar_reviews(dono: str, repo: str, numero: int, cabecalhos: dict) -> list[dict]:
    reviews = []
    pagina = 1
    while True:
        url = f"{URL_BASE_PRS}/{dono}/{repo}/pulls/{numero}/reviews"
        try:
            resp = requests.get(url, headers=cabecalhos, params={"per_page": 100, "page": pagina}, timeout=20)
            if resp.status_code != 200:
                break
            batch = resp.json()
            if not batch:
                break
            reviews.extend(batch)
            if len(batch) < 100:
                break
            pagina += 1
            time.sleep(0.1)
        except Exception:
            break
    return reviews


def verificar_reviews_paralelo(
    dono: str,
    repo: str,
    pr: dict,
    cabecalhos: dict,
    lock: threading.Lock,
    prs_filtradas: list[dict]
) -> None:
    """
    Verifica se um PR tem reviews e adiciona à lista se passar no filtro.
    Também coleta métricas adicionais solicitadas.
    """
    try:
        numero = pr["number"]

        # 1) Confirmar existência de reviews (somente cabeçalho rápido)
        url_reviews_head = f"{URL_BASE_PRS}/{dono}/{repo}/pulls/{numero}/reviews"
        resp_reviews_head = requests.get(url_reviews_head, headers=cabecalhos, params={"per_page": 1}, timeout=20)

        num_reviews = 0
        if resp_reviews_head.status_code == 200:
            total_count = resp_reviews_head.headers.get("X-Total-Count")
            if total_count:
                try:
                    num_reviews = int(total_count)
                except Exception:
                    num_reviews = 0
            else:
                try:
                    reviews_sample = resp_reviews_head.json()
                    num_reviews = len(reviews_sample) if isinstance(reviews_sample, list) else 0
                except Exception:
                    num_reviews = 0

        if num_reviews < LIMITE_REVIEWS:
            return

        # 2) Buscar detalhes completos do PR (includes additions/deletions/changed_files/body/closed_at)
        detalhes = _obter_detalhes_pr(dono, repo, numero, cabecalhos)
        if not detalhes:
            # se não obteve detalhes, continuar com fallback mínimo
            detalhes = pr

        # 3) Coletar comentários e reviews completos para calcular participantes e total comments
        comentarios_issue = _listar_comentarios_issue(dono, repo, numero, cabecalhos)
        reviews_completos = _listar_reviews(dono, repo, numero, cabecalhos)

        # participants: autor + autores de comentários + autores de reviews -> contar únicos
        participantes = set()
        autor = (detalhes.get("user") or {}).get("login")
        if autor:
            participantes.add(autor)

        for c in comentarios_issue:
            login = (c.get("user") or {}).get("login")
            if login:
                participantes.add(login)

        for r in reviews_completos:
            login = (r.get("user") or {}).get("login")
            if login:
                participantes.add(login)

        num_participantes = len(participantes)

        # comments: sumarizar comments (issue comments) + review_comments (in-line review comments)
        comments_count = int(detalhes.get("comments") or 0)
        review_comments_count = int(detalhes.get("review_comments") or 0)

        # Em alguns casos, detalhes podem não conter review_comments; usar len(reviews_completos) não representa comentários inline.
        # Já contamos issue comments via 'comments_count' e review comments via 'review_comments_count' quando disponíveis.
        total_comentarios = comments_count + review_comments_count

        # Tamanho: changed_files, additions, deletions
        additions = int(detalhes.get("additions") or 0)
        deletions = int(detalhes.get("deletions") or 0)
        changed_files = int(detalhes.get("changed_files") or 0)

        # Tempo de análise: de created_at até merged_at ou closed_at (usar closed_at se merged_at for None)
        criado_em = converter_iso_utc(detalhes["created_at"])
        fechado_em = None
        if detalhes.get("merged_at"):
            fechado_em = converter_iso_utc(detalhes["merged_at"])
        elif detalhes.get("closed_at"):
            fechado_em = converter_iso_utc(detalhes["closed_at"])

        tempo_analise_dias = None
        if fechado_em:
            tempo_analise_dias = (fechado_em - criado_em).total_seconds() / 86400.0  # dias em float

        # Descrição: número de caracteres do corpo (body). Se markdown: a API retorna body em markdown por padrão.
        corpo = detalhes.get("body") or ""
        descricao_tamanho = len(corpo)

        pr_dados = {
            "repo_completo": f"{dono}/{repo}",
            "numero_pr": numero,
            "titulo": pr.get("title"),
            "autora": (pr.get("user") or {}).get("login"),
            "status": "MERGED" if pr.get("merged_at") else "CLOSED",
            "criado_em": pr.get("created_at"),
            "atualizado_em": pr.get("updated_at"),
            "merged_em": detalhes.get("merged_at") or None,
            "closed_em": detalhes.get("closed_at") or None,
            "dias_para_merge": int((converter_iso_utc(detalhes["merged_at"]) - converter_iso_utc(detalhes["created_at"])).days) if detalhes.get("merged_at") else None,
            "numero_reviews": num_reviews,
            "url": pr.get("html_url"),
            # novos campos solicitados:
            "changed_files": changed_files,
            "additions": additions,
            "deletions": deletions,
            "tempo_analise_dias": round(tempo_analise_dias, 4) if tempo_analise_dias is not None else None,
            "descricao_tamanho_chars": descricao_tamanho,
            "num_participantes": num_participantes,
            "total_comentarios": total_comentarios,
        }

        with lock:
            prs_filtradas.append(pr_dados)

    except Exception as e:
        print(f"    ⚠️  Erro ao verificar reviews PR #{pr.get('number')}: {e}")


def coletar_pull_requests(
    dono: str, repo: str, cabecalhos: dict
) -> list[dict]:
    prs_temporarios: list[dict] = []
    pagina = 1

    print(f"    → Coletando PRs (sem filtro)...", end=" ", flush=True)

    while len(prs_temporarios) < TOTAL_PRS_POR_REPO * 3:
        url = f"{URL_BASE_PRS}/{dono}/{repo}/pulls"
        parametros = {
            "state": "closed",
            "sort": "updated",
            "direction": "desc",
            "per_page": 100,
            "page": pagina,
        }

        try:
            resposta = requests.get(
                url, headers=cabecalhos, params=parametros, timeout=60
            )
            if resposta.status_code != 200:
                print(f"\n  ⚠️  Erro ao coletar PRs: HTTP {resposta.status_code}")
                break

            prs = resposta.json()
            if not prs:
                break

            prs_temporarios.extend(prs)
            pagina += 1
            time.sleep(0.3)

        except Exception as e:
            print(f"\n  ⚠️  Erro na requisição: {e}")
            break

    print(f"Coletados {len(prs_temporarios)} PRs")

    print(f"    → Filtrando PRs com reviews...", end=" ", flush=True)

    prs_filtradas: list[dict] = []
    lock = threading.Lock()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(
                verificar_reviews_paralelo,
                dono,
                repo,
                pr,
                cabecalhos,
                lock,
                prs_filtradas
            )
            for pr in prs_temporarios[:TOTAL_PRS_POR_REPO * 2]
        ]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"⚠️  Erro em future: {e}")

            if len(prs_filtradas) >= TOTAL_PRS_POR_REPO:
                # tentar cancelar as demais tarefas
                for f in futures:
                    f.cancel()
                break

    print(f"Filtrados {len(prs_filtradas)} PRs")
    print(f"  ✓ {dono}/{repo}: {len(prs_filtradas)} PRs com reviews")

    return prs_filtradas[:TOTAL_PRS_POR_REPO]


def escrever_csv(linhas: list[dict], caminho_saida: Path, descricao: str) -> None:
    if not linhas:
        print(f"⚠️  Nenhum dado coletado para {descricao}.")
        return

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    # Garantir ordem consistente de colunas: combinar todas as chaves encontradas
    fieldnames = list({k for linha in linhas for k in linha.keys()})
    # ordenar algumas chaves chave primeiro (opcional)
    prioridade = ["repo_completo", "numero_pr", "titulo", "autora", "status", "url"]
    ordered = [k for k in prioridade if k in fieldnames] + sorted([k for k in fieldnames if k not in prioridade])
    with caminho_saida.open("w", newline="", encoding="utf-8") as fp:
        escritor = csv.DictWriter(fp, fieldnames=ordered)
        escritor.writeheader()
        for l in linhas:
            escritor.writerow(l)

    print(f"✓ CSV gerado: {caminho_saida} ({len(linhas)} registros)")


def main() -> None:
    print("=" * 70)
    print("COLETA DE REPOSITÓRIOS E PULL REQUESTS COM CODE REVIEW (COM MÉTRICAS)")
    print("=" * 70)

    print(f"\n[1/3] Coletando top {TOTAL_REPOS} repositórios populares...")
    repositorios = coletar_repositorios()
    escrever_csv(repositorios, CAMINHO_CSV_REPOS, "repositórios")

    print(f"\n[2/3] Coletando PRs com reviews de cada repositórios...")
    cabecalhos = obter_cabecalhos()
    todos_prs: list[dict] = []

    for idx, repo in enumerate(repositorios, 1):
        print(f"  [{idx}/{len(repositorios)}] {repo['nome_completo']}")
        prs = coletar_pull_requests(repo["dono"], repo["nome_repo"], cabecalhos)
        todos_prs.extend(prs)
        time.sleep(0.5)

    print(f"\n[3/3] Salvando resultados...")
    escrever_csv(todos_prs, CAMINHO_CSV_PRS, "pull requests com reviews")

    print("\n" + "=" * 70)
    print("RESUMO DA COLETA")
    print("=" * 70)
    print(f"✓ Total de repositórios: {len(repositorios)}")
    print(f"✓ Total de PRs com reviews: {len(todos_prs)}")
    if repositorios:
        media_prs = len(todos_prs) / len(repositorios)
        print(f"✓ Média de PRs por repositório: {media_prs:.2f}")
    print(f"✓ Arquivos salvos em: {DIR_SAIDA}")
    print("=" * 70)


if __name__ == "__main__":
    main()