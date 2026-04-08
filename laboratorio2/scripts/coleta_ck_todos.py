"""
Sprint 02 — Coleta de metricas CK para todos os repositorios Java.

Arquitetura: pool de workers com ThreadPoolExecutor.
Cada worker clona um repo (shallow), executa o CK, sumariza class.csv
e apaga o clone imediatamente. Resultados sao appendados com lock em
um CSV de saida com checkpoint/resume.
"""

import argparse
import csv
import logging
import os
import shutil
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv


# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------
DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_SAIDA = DIR_PROJETO / "output"
DIR_FERRAMENTAS = DIR_PROJETO / "tools"
DIR_TMP = DIR_PROJETO / "tmp"

CSV_ENTRADA = DIR_SAIDA / "top_1000_java_repos_enriquecido.csv"
CSV_RESULTADO = DIR_SAIDA / "ck_resultado_todos.csv"
LOG_ERROS = DIR_SAIDA / "erros_coleta.log"

VERSAO_CK = "0.7.0"
URL_JAR_CK = (
    "https://repo1.maven.org/maven2/com/github/mauricioaniche/ck/"
    f"{VERSAO_CK}/ck-{VERSAO_CK}-jar-with-dependencies.jar"
)

METRICAS_QUALIDADE = ("cbo", "dit", "lcom")

COLUNAS_SAIDA = [
    "nome_completo", "url", "estrelas", "idade_anos",
    "total_releases", "tamanho_kb",
    "loc_total", "loc_media", "loc_mediana",
    "cbo_media", "cbo_mediana", "cbo_desvio_padrao",
    "dit_media", "dit_mediana", "dit_desvio_padrao",
    "lcom_media", "lcom_mediana", "lcom_desvio_padrao",
]

# Repos maiores que este limite (KB) serao pulados
TAMANHO_MAX_KB = 500_000

TIMEOUT_CLONE = 120
TIMEOUT_CK = 180

# Lock para escrita thread-safe no CSV de saida
_lock_csv = threading.Lock()


# ---------------------------------------------------------------------------
# Setup de logging
# ---------------------------------------------------------------------------

def configurar_logging() -> logging.Logger:
    DIR_SAIDA.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("coleta_ck")
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler(LOG_ERROS, encoding="utf-8")
    fh.setLevel(logging.WARNING)
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(sh)

    return logger


logger = configurar_logging()


# ---------------------------------------------------------------------------
# Funcoes reutilizadas da Sprint 01
# ---------------------------------------------------------------------------

def garantir_jar_ck(caminho_jar: Path) -> Path:
    if caminho_jar.exists():
        return caminho_jar
    caminho_jar.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Baixando CK {VERSAO_CK} em: {caminho_jar}")
    with requests.get(URL_JAR_CK, timeout=120, stream=True) as resp:
        if resp.status_code != 200:
            raise RuntimeError(f"Falha ao baixar CK (HTTP {resp.status_code})")
        with caminho_jar.open("wb") as fp:
            for pedaco in resp.iter_content(chunk_size=1024 * 128):
                if pedaco:
                    fp.write(pedaco)
    return caminho_jar


def _forcar_remocao(func, caminho, _exc_info):
    """Callback para shutil.rmtree no Windows (arquivos .git read-only)."""
    os.chmod(caminho, 0o777)
    func(caminho)


def limpar_diretorio(diretorio: Path) -> None:
    if diretorio.exists():
        shutil.rmtree(diretorio, onexc=_forcar_remocao)


# ---------------------------------------------------------------------------
# Pipeline de um repositorio (executado dentro de cada worker)
# ---------------------------------------------------------------------------

def processar_repositorio(
    repo: dict, caminho_jar: Path, worker_id: int
) -> dict | None:
    """Clona, executa CK, sumariza e limpa. Retorna dict ou None em caso de falha."""
    nome = repo["nome_completo"]
    dir_worker = DIR_TMP / f"worker_{worker_id}"
    dir_clone = dir_worker / "repo"
    dir_ck = dir_worker / "ck_out"

    try:
        # Filtro de tamanho
        tamanho_kb = int(repo.get("tamanho_kb", 0))
        if tamanho_kb > TAMANHO_MAX_KB:
            logger.warning(f"SKIP (tamanho {tamanho_kb} KB > {TAMANHO_MAX_KB} KB): {nome}")
            return None

        # 1. Clone minimalista com timeout
        limpar_diretorio(dir_clone)
        dir_clone.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                "git", "clone",
                "--depth", "1",
                "--single-branch",
                "--quiet",
                "--no-tags",
                repo["url"],
                str(dir_clone),
            ],
            check=True,
            timeout=TIMEOUT_CLONE,
            capture_output=True,
        )

        # 2. Executar CK com timeout
        limpar_diretorio(dir_ck)
        dir_ck.mkdir(parents=True, exist_ok=True)
        caminho_saida_ck = str(dir_ck) + os.sep
        subprocess.run(
            [
                "java", "-jar", str(caminho_jar),
                str(dir_clone), "false", "0", "false", caminho_saida_ck,
            ],
            check=True,
            timeout=TIMEOUT_CK,
            capture_output=True,
        )

        # 3. Apagar clone imediatamente para liberar disco
        limpar_diretorio(dir_clone)

        # 4. Sumarizar class.csv
        class_csv = dir_ck / "class.csv"
        if not class_csv.exists() or class_csv.stat().st_size < 10:
            logger.warning(f"SKIP (class.csv vazio/inexistente): {nome}")
            return None

        df = pd.read_csv(class_csv)
        if df.empty or not all(c in df.columns for c in METRICAS_QUALIDADE):
            logger.warning(f"SKIP (colunas CK ausentes): {nome}")
            return None

        resumo: dict = {
            "nome_completo": nome,
            "url": repo["url"],
            "estrelas": int(repo.get("estrelas", 0)),
            "idade_anos": float(repo.get("idade_anos", 0)),
            "total_releases": int(repo.get("total_releases", 0)),
            "tamanho_kb": tamanho_kb,
        }

        # LOC vem do CK (coluna 'loc' no class.csv)
        if "loc" in df.columns:
            resumo["loc_total"] = int(df["loc"].sum())
            resumo["loc_media"] = round(float(df["loc"].mean()), 4)
            resumo["loc_mediana"] = round(float(df["loc"].median()), 4)
        else:
            resumo["loc_total"] = 0
            resumo["loc_media"] = 0.0
            resumo["loc_mediana"] = 0.0

        for metrica in METRICAS_QUALIDADE:
            serie = df[metrica]
            resumo[f"{metrica}_media"] = round(float(serie.mean()), 4)
            resumo[f"{metrica}_mediana"] = round(float(serie.median()), 4)
            resumo[f"{metrica}_desvio_padrao"] = round(float(serie.std(ddof=0)), 4)

        # Limpar saida do CK
        limpar_diretorio(dir_ck)
        return resumo

    except subprocess.TimeoutExpired:
        logger.warning(f"TIMEOUT: {nome}")
    except subprocess.CalledProcessError as exc:
        logger.warning(f"ERRO processo: {nome} — {exc}")
    except Exception as exc:
        logger.warning(f"ERRO inesperado: {nome} — {exc}")
    finally:
        limpar_diretorio(dir_clone)
        limpar_diretorio(dir_ck)

    return None


# ---------------------------------------------------------------------------
# Checkpoint: repos ja processados
# ---------------------------------------------------------------------------

def carregar_ja_processados() -> set[str]:
    if not CSV_RESULTADO.exists():
        return set()
    with CSV_RESULTADO.open("r", newline="", encoding="utf-8") as fp:
        return {linha["nome_completo"] for linha in csv.DictReader(fp)}


def appendar_resultado(resultado: dict) -> None:
    """Appenda uma linha no CSV de saida de forma thread-safe."""
    with _lock_csv:
        existe = CSV_RESULTADO.exists() and CSV_RESULTADO.stat().st_size > 0
        with CSV_RESULTADO.open("a", newline="", encoding="utf-8") as fp:
            escritor = csv.DictWriter(fp, fieldnames=COLUNAS_SAIDA)
            if not existe:
                escritor.writeheader()
            escritor.writerow(resultado)


# ---------------------------------------------------------------------------
# Pipeline principal com ThreadPoolExecutor
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Coleta metricas CK de todos os repositorios Java (Sprint 02)."
    )
    parser.add_argument(
        "--workers", type=int, default=4,
        help="Numero de workers paralelos (padrao: 4).",
    )
    parser.add_argument(
        "--ck-jar", default=str(DIR_FERRAMENTAS / "ck.jar"),
        help="Caminho para o ck.jar.",
    )
    args = parser.parse_args()

    caminho_jar = garantir_jar_ck(Path(args.ck_jar))

    # Carregar lista de repositorios enriquecida
    if not CSV_ENTRADA.exists():
        logger.error(f"CSV de entrada nao encontrado: {CSV_ENTRADA}")
        logger.error("Execute primeiro: python scripts/enriquecer_repos.py")
        return

    with CSV_ENTRADA.open("r", newline="", encoding="utf-8") as fp:
        repos = list(csv.DictReader(fp))

    ja_processados = carregar_ja_processados()
    pendentes = [r for r in repos if r["nome_completo"] not in ja_processados]

    total = len(repos)
    pular = total - len(pendentes)
    logger.info(f"Total: {total} | Ja processados: {pular} | Pendentes: {len(pendentes)}")

    sucesso = 0
    falha = 0
    inicio = time.time()

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futuros = {
            pool.submit(processar_repositorio, repo, caminho_jar, i % args.workers): repo
            for i, repo in enumerate(pendentes)
        }

        for futuro in as_completed(futuros):
            repo = futuros[futuro]
            nome = repo["nome_completo"]
            resultado = futuro.result()

            if resultado:
                appendar_resultado(resultado)
                sucesso += 1
                processados = pular + sucesso + falha
                logger.info(
                    f"[{processados}/{total}] OK: {nome} "
                    f"(CBO={resultado['cbo_mediana']}, "
                    f"DIT={resultado['dit_mediana']}, "
                    f"LCOM={resultado['lcom_mediana']})"
                )
            else:
                falha += 1
                processados = pular + sucesso + falha
                logger.info(f"[{processados}/{total}] FALHA/SKIP: {nome}")

    duracao = time.time() - inicio
    logger.info(
        f"\nConcluido em {duracao / 60:.1f} min. "
        f"Sucesso: {sucesso} | Falha/Skip: {falha} | "
        f"CSV: {CSV_RESULTADO}"
    )


if __name__ == "__main__":
    main()
