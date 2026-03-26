import csv
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv


DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_SAIDA = DIR_PROJETO / "output"
CAMINHO_CSV = DIR_SAIDA / "top_1000_java_repos.csv"

TOTAL_REPOS = 1000
POR_PAGINA = 100
MAX_PAGINAS = 10
URL_BASE = "https://api.github.com/search/repositories"


def obter_cabecalhos() -> dict:
    load_dotenv(DIR_PROJETO / ".env")
    token = os.getenv("GITHUB_TOKEN", "").strip()
    cabecalhos = {"Accept": "application/vnd.github+json"}
    if token:
        cabecalhos["Authorization"] = f"Bearer {token}"
    return cabecalhos


def converter_iso_utc(valor: str) -> datetime:
    return datetime.fromisoformat(valor.replace("Z", "+00:00"))


def coletar_repositorios_java(total: int = TOTAL_REPOS) -> list[dict]:
    cabecalhos = obter_cabecalhos()
    agora = datetime.now(timezone.utc)
    repositorios: list[dict] = []

    for pagina in range(1, MAX_PAGINAS + 1):
        parametros = {
            "q": "language:Java stars:>0",
            "sort": "stars",
            "order": "desc",
            "per_page": POR_PAGINA,
            "page": pagina,
        }
        resposta = requests.get(URL_BASE, headers=cabecalhos, params=parametros, timeout=60)
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

        print(f"Pagina {pagina}: {len(repositorios)}/{total} repositorios Java coletados.")
        if len(repositorios) >= total or not itens:
            break
        time.sleep(1.0)

    return repositorios[:total]


def escrever_csv(linhas: list[dict], caminho_saida: Path) -> None:
    if not linhas:
        raise ValueError("Nenhum repositorio coletado.")
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    with caminho_saida.open("w", newline="", encoding="utf-8") as fp:
        escritor = csv.DictWriter(fp, fieldnames=list(linhas[0].keys()))
        escritor.writeheader()
        escritor.writerows(linhas)


def main() -> None:
    print("Iniciando coleta da Sprint 01 (Top 1000 repositorios Java)...")
    repositorios = coletar_repositorios_java()
    escrever_csv(repositorios, CAMINHO_CSV)
    print(f"Concluido. CSV gerado em: {CAMINHO_CSV}")


if __name__ == "__main__":
    main()
