"""
Enriquece o CSV de repositorios com tamanho_kb e total_releases via API REST.

Executa chamadas leves (sem clone) para cada repositorio, adicionando:
  - tamanho_kb: campo 'size' retornado por GET /repos/{owner}/{repo}
  - total_releases: contagem via GET /repos/{owner}/{repo}/releases

Suporta checkpoint/resume: se o CSV de saida ja existir, pula repos
ja processados.
"""

import csv
import os
import re
import time
from pathlib import Path

import requests
from dotenv import load_dotenv


DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_SAIDA = DIR_PROJETO / "output"

CSV_ENTRADA = DIR_SAIDA / "top_1000_java_repos.csv"
CSV_SAIDA = DIR_SAIDA / "top_1000_java_repos_enriquecido.csv"

COLUNAS_NOVAS = ["tamanho_kb", "total_releases"]


def obter_cabecalhos() -> dict:
    load_dotenv(DIR_PROJETO / ".env")
    token = os.getenv("GITHUB_TOKEN", "").strip()
    cabecalhos = {"Accept": "application/vnd.github+json"}
    if token:
        cabecalhos["Authorization"] = f"Bearer {token}"
    return cabecalhos


def obter_tamanho_e_releases(dono: str, nome_repo: str, cabecalhos: dict) -> dict:
    """Busca tamanho (KB) e total de releases de um repositorio via API REST."""
    base = f"https://api.github.com/repos/{dono}/{nome_repo}"

    # Tamanho do repositorio
    resp_repo = requests.get(base, headers=cabecalhos, timeout=30)
    if resp_repo.status_code != 200:
        raise RuntimeError(f"GET {base} retornou {resp_repo.status_code}")
    tamanho_kb = resp_repo.json().get("size", 0)

    # Total de releases — pega 1 release e extrai total do header Link
    resp_rel = requests.get(
        f"{base}/releases", headers=cabecalhos, params={"per_page": 1}, timeout=30
    )
    total_releases = 0
    if resp_rel.status_code == 200:
        link_header = resp_rel.headers.get("Link", "")
        match = re.search(r'page=(\d+)>; rel="last"', link_header)
        if match:
            total_releases = int(match.group(1))
        elif resp_rel.json():
            total_releases = len(resp_rel.json())

    return {"tamanho_kb": tamanho_kb, "total_releases": total_releases}


def esperar_rate_limit(cabecalhos_resposta: dict) -> None:
    """Se restam poucas requisicoes, pausa ate o reset."""
    restante = int(cabecalhos_resposta.get("X-RateLimit-Remaining", 100))
    if restante < 50:
        reset_ts = int(cabecalhos_resposta.get("X-RateLimit-Reset", 0))
        espera = max(reset_ts - int(time.time()), 1)
        print(f"Rate limit baixo ({restante}). Pausando {espera}s...")
        time.sleep(espera)


def carregar_ja_processados(caminho_csv: Path) -> set[str]:
    """Retorna set de nome_completo ja presentes no CSV de saida."""
    if not caminho_csv.exists():
        return set()
    with caminho_csv.open("r", newline="", encoding="utf-8") as fp:
        return {linha["nome_completo"] for linha in csv.DictReader(fp)}


def main() -> None:
    cabecalhos = obter_cabecalhos()

    with CSV_ENTRADA.open("r", newline="", encoding="utf-8") as fp:
        leitor = csv.DictReader(fp)
        colunas_originais = leitor.fieldnames or []
        repos = list(leitor)

    colunas_saida = list(colunas_originais) + COLUNAS_NOVAS
    ja_processados = carregar_ja_processados(CSV_SAIDA)
    total = len(repos)

    print(f"Total de repositorios: {total}")
    print(f"Ja processados (checkpoint): {len(ja_processados)}")

    modo = "a" if ja_processados else "w"
    with CSV_SAIDA.open(modo, newline="", encoding="utf-8") as fp:
        escritor = csv.DictWriter(fp, fieldnames=colunas_saida)
        if modo == "w":
            escritor.writeheader()

        for i, repo in enumerate(repos, 1):
            nome = repo["nome_completo"]
            if nome in ja_processados:
                continue

            try:
                extras = obter_tamanho_e_releases(
                    repo["dono"], repo["nome_repo"], cabecalhos
                )
                linha = {**repo, **extras}
                escritor.writerow(linha)
                fp.flush()
                ja_processados.add(nome)

                print(f"[{i}/{total}] {nome} — {extras['tamanho_kb']} KB, "
                      f"{extras['total_releases']} releases")

                # Verifica rate limit a cada 50 repos
                if i % 50 == 0:
                    resp = requests.get(
                        "https://api.github.com/rate_limit",
                        headers=cabecalhos, timeout=10,
                    )
                    if resp.status_code == 200:
                        esperar_rate_limit(resp.headers)

                time.sleep(0.3)

            except Exception as exc:
                print(f"[{i}/{total}] ERRO em {nome}: {exc}")
                linha = {**repo, "tamanho_kb": 0, "total_releases": 0}
                escritor.writerow(linha)
                fp.flush()

    print(f"\nConcluido. CSV enriquecido em: {CSV_SAIDA}")


if __name__ == "__main__":
    main()
