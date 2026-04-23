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
TOTAL_PRS_POR_REPO = 100  # PRs merged + closed
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
    """Coleta os repositórios mais populares com base em estrelas."""
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
    Executado em paralelo por ThreadPoolExecutor.
    """
    try:
        url_reviews = f"{URL_BASE_PRS}/{dono}/{repo}/pulls/{pr['number']}/reviews"
        resposta = requests.get(
            url_reviews, 
            headers=cabecalhos, 
            params={"per_page": 1}, 
            timeout=20
        )
        
        num_reviews = 0
        if resposta.status_code == 200:
            # Tentar obter total de reviews pelo header
            total_count = resposta.headers.get("X-Total-Count")
            if total_count:
                num_reviews = int(total_count)
            else:
                # Fallback: contar a resposta
                reviews = resposta.json()
                num_reviews = len(reviews) if isinstance(reviews, list) else 0
        
        # Filtrar: apenas PRs com pelo menos 1 review
        if num_reviews >= LIMITE_REVIEWS:
            criado_em = converter_iso_utc(pr["created_at"])
            merged_em = None
            dias_para_merge = None
            
            if pr.get("merged_at"):
                merged_em = converter_iso_utc(pr["merged_at"])
                dias_para_merge = (merged_em - criado_em).days

            pr_dados = {
                "repo_completo": f"{dono}/{repo}",
                "numero_pr": pr["number"],
                "titulo": pr.get("title"),
                "autora": pr.get("user", {}).get("login"),
                "status": "MERGED" if pr.get("merged_at") else "CLOSED",
                "criado_em": pr.get("created_at"),
                "atualizado_em": pr.get("updated_at"),
                "merged_em": merged_em.isoformat() if merged_em else None,
                "dias_para_merge": dias_para_merge,
                "numero_reviews": num_reviews,
                "url": pr.get("html_url"),
            }
            
            with lock:
                prs_filtradas.append(pr_dados)
    
    except Exception as e:
        print(f"    ⚠️  Erro ao verificar reviews PR #{pr['number']}: {e}")


def coletar_pull_requests(
    dono: str, repo: str, cabecalhos: dict
) -> list[dict]:
    """
    Coleta PRs com status MERGED ou CLOSED que possuem pelo menos uma revisão.
    OTIMIZADO: Usa ThreadPoolExecutor para verificar reviews em paralelo.
    """
    prs_temporarios: list[dict] = []
    pagina = 1

    # Etapa 1: Coletar todos os PRs rapidamente (sem verificar reviews ainda)
    print(f"    → Coletando PRs (sem filtro)...", end=" ", flush=True)
    
    while len(prs_temporarios) < TOTAL_PRS_POR_REPO * 3:  # Buscar mais pra compensar filtro
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

    # Etapa 2: Filtrar por reviews em paralelo
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
            for pr in prs_temporarios[:TOTAL_PRS_POR_REPO * 2]  # Limitar processamento
        ]

        # Aguardar conclusão
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"⚠️  Erro em future: {e}")

        # Parar se atingiu o limite
        if len(prs_filtradas) >= TOTAL_PRS_POR_REPO:
            # Cancelar tarefas pendentes
            for f in futures:
                f.cancel()

    print(f"Filtrados {len(prs_filtradas)} PRs")
    print(
        f"  ✓ {dono}/{repo}: {len(prs_filtradas)} PRs com reviews"
    )
    
    return prs_filtradas[:TOTAL_PRS_POR_REPO]


def escrever_csv(linhas: list[dict], caminho_saida: Path, descricao: str) -> None:
    """Escreve dados em arquivo CSV."""
    if not linhas:
        print(f"⚠️  Nenhum dado coletado para {descricao}.")
        return

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    with caminho_saida.open("w", newline="", encoding="utf-8") as fp:
        escritor = csv.DictWriter(fp, fieldnames=list(linhas[0].keys()))
        escritor.writeheader()
        escritor.writerows(linhas)

    print(f"✓ CSV gerado: {caminho_saida} ({len(linhas)} registros)")


def main() -> None:
    print("=" * 70)
    print("COLETA DE REPOSITÓRIOS E PULL REQUESTS COM CODE REVIEW")
    print("=" * 70)

    # Etapa 1: Coletar repositórios
    print(f"\n[1/3] Coletando top {TOTAL_REPOS} repositórios populares...")
    repositorios = coletar_repositorios()
    escrever_csv(repositorios, CAMINHO_CSV_REPOS, "repositórios")

    # Etapa 2: Coletar PRs com reviews de cada repositório
    print(f"\n[2/3] Coletando PRs com reviews de cada repositório...")
    cabecalhos = obter_cabecalhos()
    todos_prs: list[dict] = []

    for idx, repo in enumerate(repositorios, 1):
        print(
            f"  [{idx}/{len(repositorios)}] {repo['nome_completo']}"
        )
        prs = coletar_pull_requests(repo["dono"], repo["nome_repo"], cabecalhos)
        todos_prs.extend(prs)
        time.sleep(0.5)

    # Etapa 3: Salvar PRs
    print(f"\n[3/3] Salvando resultados...")
    escrever_csv(todos_prs, CAMINHO_CSV_PRS, "pull requests com reviews")

    # Resumo
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
