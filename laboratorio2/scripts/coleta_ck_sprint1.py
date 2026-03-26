"""
Sprint 01 — Clone de repositorio Java + analise estatica com CK.

Pipeline:
  1. Garante que o JAR do CK esta disponivel (baixa se necessario).
  2. Le o primeiro repositorio do CSV gerado pela coleta.
  3. Clona o repositorio (shallow clone).
  4. Executa o CK sobre o codigo-fonte clonado.
  5. Sumariza as metricas CBO, DIT e LCOM (media, mediana, desvio padrao).
  6. Exporta o resultado em um CSV de validacao.
"""

import argparse
import csv
import os
import shutil
import subprocess
from pathlib import Path

import pandas as pd
import requests

# ---------------------------------------------------------------------------
# Caminhos do projeto
# ---------------------------------------------------------------------------
DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_SAIDA = DIR_PROJETO / "output"
DIR_FERRAMENTAS = DIR_PROJETO / "tools"
DIR_REPOS = DIR_PROJETO / "repos"
DIR_TMP = DIR_PROJETO / "tmp"

CSV_REPOSITORIOS = DIR_SAIDA / "top_1000_java_repos.csv"
CSV_RESULTADO = DIR_SAIDA / "ck_resultado_1_repo.csv"

# ---------------------------------------------------------------------------
# Configuracao do CK
# ---------------------------------------------------------------------------
VERSAO_CK = "0.7.0"
URL_JAR_CK = (
    "https://repo1.maven.org/maven2/com/github/mauricioaniche/ck/"
    f"{VERSAO_CK}/ck-{VERSAO_CK}-jar-with-dependencies.jar"
)

# Metricas de qualidade que o enunciado pede para sumarizar
METRICAS_QUALIDADE = ("cbo", "dit", "lcom")


# ---------------------------------------------------------------------------
# Funcoes auxiliares
# ---------------------------------------------------------------------------

def garantir_jar_ck(caminho_jar: Path) -> Path:
    """Retorna o caminho do JAR do CK; baixa do Maven Central se nao existir."""
    if caminho_jar.exists():
        return caminho_jar

    caminho_jar.parent.mkdir(parents=True, exist_ok=True)
    print(f"Baixando CK {VERSAO_CK} em: {caminho_jar}")

    with requests.get(URL_JAR_CK, timeout=120, stream=True) as resposta:
        if resposta.status_code != 200:
            raise RuntimeError(
                f"Falha ao baixar CK (HTTP {resposta.status_code}): {resposta.text}"
            )
        with caminho_jar.open("wb") as fp:
            for pedaco in resposta.iter_content(chunk_size=1024 * 128):
                if pedaco:
                    fp.write(pedaco)

    return caminho_jar


def carregar_primeiro_repo(caminho_csv: Path) -> dict:
    """Le apenas a primeira linha do CSV de repositorios (validacao da sprint)."""
    if not caminho_csv.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {caminho_csv}")

    with caminho_csv.open("r", newline="", encoding="utf-8") as fp:
        leitor = csv.DictReader(fp)
        primeiro = next(leitor, None)

    if not primeiro:
        raise ValueError("CSV de repositorios vazio.")
    return primeiro


def _forcar_remocao(func, caminho, _exc_info):
    """Callback para shutil.rmtree: no Windows, arquivos .git sao read-only
    e precisam ter a permissao alterada antes de serem deletados."""
    os.chmod(caminho, 0o777)
    func(caminho)


def executar_clone_git(url_repo: str, dir_destino: Path) -> None:
    """Faz um shallow clone (--depth 1) do repositorio.
    Se o diretorio destino ja existir, remove antes de clonar."""
    if dir_destino.exists():
        shutil.rmtree(dir_destino, onexc=_forcar_remocao)

    dir_destino.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "--depth", "1", url_repo, str(dir_destino)],
        check=True,
    )


def executar_ck(caminho_jar: Path, dir_repo: Path, dir_saida_ck: Path) -> None:
    """Roda o CK via linha de comando.

    Argumentos do CK (em ordem):
      1. diretorio do projeto
      2. usar JARs do projeto como dependencia (false)
      3. max arquivos por particao (0 = automatico)
      4. metricas de variavel/campo (false — so precisamos de classe)
      5. diretorio de saida (DEVE terminar com separador, senao o CK
         concatena o nome da pasta direto no nome do CSV)
    """
    dir_saida_ck.mkdir(parents=True, exist_ok=True)

    # O CK exige que o caminho termine com separador de diretorio
    caminho_saida = str(dir_saida_ck) + os.sep

    subprocess.run(
        [
            "java", "-jar", str(caminho_jar),
            str(dir_repo),    # projeto a analisar
            "false",          # useJars
            "0",              # maxAtOnce (0 = auto)
            "false",          # variablesAndFields
            caminho_saida,    # diretorio de saida
        ],
        check=True,
    )


def sumarizar_metricas_classe(caminho_csv_classe: Path, repo: dict) -> pd.DataFrame:
    """Le o class.csv gerado pelo CK e calcula media, mediana e desvio padrao
    das metricas CBO, DIT e LCOM — agregando todas as classes do repositorio
    em uma unica linha de resumo."""
    if not caminho_csv_classe.exists():
        raise FileNotFoundError(
            f"Arquivo de classe do CK nao encontrado: {caminho_csv_classe}"
        )

    df = pd.read_csv(caminho_csv_classe)

    for coluna in METRICAS_QUALIDADE:
        if coluna not in df.columns:
            raise ValueError(f"Coluna obrigatoria ausente no CK: {coluna}")

    resumo: dict = {
        "nome_completo": repo["nome_completo"],
        "url": repo["url"],
        "estrelas": int(repo["estrelas"]),
    }

    for metrica in METRICAS_QUALIDADE:
        serie = df[metrica]
        resumo[f"{metrica}_media"] = round(float(serie.mean()), 4)
        resumo[f"{metrica}_mediana"] = round(float(serie.median()), 4)
        resumo[f"{metrica}_desvio_padrao"] = round(float(serie.std(ddof=0)), 4)

    return pd.DataFrame([resumo])


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Executa clone + CK para 1 repositorio Java (Sprint 01)."
    )
    parser.add_argument(
        "--ck-jar",
        default=str(DIR_FERRAMENTAS / "ck.jar"),
        help="Caminho para o arquivo ck.jar; se nao existir, sera baixado automaticamente.",
    )
    args = parser.parse_args()

    # 1. Garantir que o JAR do CK existe
    caminho_jar = garantir_jar_ck(Path(args.ck_jar))

    # 2. Ler o primeiro repositorio do CSV
    repo = carregar_primeiro_repo(CSV_REPOSITORIOS)

    dir_repo = DIR_REPOS / repo["nome_repo"]
    dir_saida_ck = DIR_TMP / "ck_saida_1repo"

    # 3. Clonar o repositorio
    print(f"Clonando repositorio: {repo['nome_completo']}")
    executar_clone_git(repo["url"], dir_repo)

    # 4. Executar o CK (limpa saida anterior se existir)
    print("Executando CK...")
    if dir_saida_ck.exists():
        shutil.rmtree(dir_saida_ck)
    executar_ck(caminho_jar, dir_repo, dir_saida_ck)

    # 5. Sumarizar metricas e exportar CSV
    caminho_csv_classe = dir_saida_ck / "class.csv"
    print(f"Sumarizando metricas de: {caminho_csv_classe}")
    df_resumo = sumarizar_metricas_classe(caminho_csv_classe, repo)

    DIR_SAIDA.mkdir(parents=True, exist_ok=True)
    df_resumo.to_csv(CSV_RESULTADO, index=False)
    print(f"Concluido. CSV de validacao gerado em: {CSV_RESULTADO}")


if __name__ == "__main__":
    main()
