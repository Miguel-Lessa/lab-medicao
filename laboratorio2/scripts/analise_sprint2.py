"""
Sprint 02 — Analise estatistica dos dados coletados.

Gera dados organizados para elaboracao manual do relatorio:
  - output/descritivas_globais.csv       (estatisticas descritivas de todas as metricas)
  - output/correlacoes_spearman.csv      (rho + p-valor para cada par processo x qualidade)
  - output/charts/RQxx_scatter_*.png     (scatter plots com linha de tendencia)
  - output/charts/RQxx_boxplot_*.png     (boxplots por quartil)
  - output/charts/heatmap_correlacao.png (heatmap geral de Spearman)
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats


# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------
DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_SAIDA = DIR_PROJETO / "output"
DIR_GRAFICOS = DIR_SAIDA / "charts"
CSV_RESULTADO = DIR_SAIDA / "ck_resultado_todos.csv"

CSV_DESCRITIVAS = DIR_SAIDA / "descritivas_globais.csv"
CSV_CORRELACOES = DIR_SAIDA / "correlacoes_spearman.csv"

METRICAS_QUALIDADE = ["cbo_mediana", "dit_mediana", "lcom_mediana"]
NOMES_QUALIDADE = {"cbo_mediana": "CBO", "dit_mediana": "DIT", "lcom_mediana": "LCOM"}

RQS = {
    "RQ01": {
        "titulo": "Popularidade x Qualidade",
        "metrica_processo": "estrelas",
        "nome_processo": "Estrelas",
    },
    "RQ02": {
        "titulo": "Maturidade x Qualidade",
        "metrica_processo": "idade_anos",
        "nome_processo": "Idade (anos)",
    },
    "RQ03": {
        "titulo": "Atividade x Qualidade",
        "metrica_processo": "total_releases",
        "nome_processo": "Total de Releases",
    },
    "RQ04": {
        "titulo": "Tamanho x Qualidade",
        "metrica_processo": "loc_total",
        "nome_processo": "LOC Total",
    },
}


# ---------------------------------------------------------------------------
# Funcoes de analise
# ---------------------------------------------------------------------------

def calcular_descritivas(df: pd.DataFrame, colunas: list[str]) -> pd.DataFrame:
    """Retorna DataFrame com media, mediana, desvio padrao, min, max, n de cada coluna."""
    linhas = []
    for col in colunas:
        if col not in df.columns:
            continue
        serie = df[col].dropna()
        linhas.append({
            "metrica": col,
            "media": round(float(serie.mean()), 4),
            "mediana": round(float(serie.median()), 4),
            "desvio_padrao": round(float(serie.std()), 4),
            "min": round(float(serie.min()), 4),
            "max": round(float(serie.max()), 4),
            "n": len(serie),
        })
    return pd.DataFrame(linhas)


def calcular_spearman(df: pd.DataFrame, col_x: str, col_y: str) -> dict:
    limpo = df[[col_x, col_y]].dropna()
    if len(limpo) < 3:
        return {"rho": float("nan"), "p_valor": float("nan"), "n": len(limpo)}
    rho, p = stats.spearmanr(limpo[col_x], limpo[col_y])
    return {"rho": round(float(rho), 4), "p_valor": round(float(p), 6), "n": len(limpo)}


def interpretar_correlacao(rho: float) -> str:
    abs_rho = abs(rho)
    if abs_rho < 0.1:
        forca = "desprezivel"
    elif abs_rho < 0.3:
        forca = "fraca"
    elif abs_rho < 0.5:
        forca = "moderada"
    elif abs_rho < 0.7:
        forca = "forte"
    else:
        forca = "muito forte"
    direcao = "positiva" if rho >= 0 else "negativa"
    return f"{forca} {direcao}"


# ---------------------------------------------------------------------------
# Funcoes de visualizacao
# ---------------------------------------------------------------------------

def gerar_scatter(df: pd.DataFrame, col_x: str, col_y: str,
                  label_x: str, label_y: str, titulo: str, caminho: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(df[col_x], df[col_y], alpha=0.3, s=15, edgecolors="none")

    limpo = df[[col_x, col_y]].dropna()
    if len(limpo) > 2:
        z = np.polyfit(limpo[col_x], limpo[col_y], 1)
        p = np.poly1d(z)
        x_sorted = np.sort(limpo[col_x])
        ax.plot(x_sorted, p(x_sorted), "r--", alpha=0.7, linewidth=1)

    ax.set_xlabel(label_x)
    ax.set_ylabel(label_y)
    ax.set_title(titulo)
    fig.tight_layout()
    fig.savefig(caminho, dpi=150)
    plt.close(fig)


def gerar_heatmap(df: pd.DataFrame, colunas_x: list, colunas_y: list,
                  labels_x: list, labels_y: list, caminho: Path) -> None:
    matriz = []
    for cy in colunas_y:
        linha = []
        for cx in colunas_x:
            limpo = df[[cx, cy]].dropna()
            if len(limpo) > 2:
                rho, _ = stats.spearmanr(limpo[cx], limpo[cy])
                linha.append(round(rho, 3))
            else:
                linha.append(0.0)
        matriz.append(linha)

    df_heat = pd.DataFrame(matriz, index=labels_y, columns=labels_x)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(df_heat, annot=True, cmap="RdBu_r", center=0, vmin=-1, vmax=1, ax=ax)
    ax.set_title("Correlacao de Spearman: Processo x Qualidade")
    fig.tight_layout()
    fig.savefig(caminho, dpi=150)
    plt.close(fig)


def gerar_boxplots_quartil(df: pd.DataFrame, col_processo: str, col_qualidade: str,
                           label_processo: str, label_qualidade: str,
                           caminho: Path) -> None:
    limpo = df[[col_processo, col_qualidade]].dropna().copy()
    if len(limpo) < 4:
        return
    try:
        limpo["quartil"] = pd.qcut(limpo[col_processo], q=4, duplicates="drop")
        limpo["quartil"] = limpo["quartil"].cat.rename_categories(
            {c: f"Q{i+1}" for i, c in enumerate(limpo["quartil"].cat.categories)}
        )
    except ValueError:
        return
    fig, ax = plt.subplots(figsize=(8, 5))
    limpo.boxplot(column=col_qualidade, by="quartil", ax=ax, grid=False)
    ax.set_xlabel(f"Quartil de {label_processo}")
    ax.set_ylabel(label_qualidade)
    ax.set_title(f"{label_qualidade} por quartil de {label_processo}")
    fig.suptitle("")
    fig.tight_layout()
    fig.savefig(caminho, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def main() -> None:
    if not CSV_RESULTADO.exists():
        print(f"CSV nao encontrado: {CSV_RESULTADO}")
        print("Execute primeiro: python scripts/coleta_ck_todos.py")
        return

    DIR_GRAFICOS.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(CSV_RESULTADO)
    print(f"Repositorios carregados: {len(df)}")

    # 1. Estatisticas descritivas globais
    colunas_interesse = [
        "estrelas", "idade_anos", "total_releases", "loc_total",
        "cbo_mediana", "dit_mediana", "lcom_mediana",
        "cbo_media", "dit_media", "lcom_media",
    ]
    df_descritivas = calcular_descritivas(df, colunas_interesse)
    df_descritivas.to_csv(CSV_DESCRITIVAS, index=False)
    print(f"\nEstatisticas descritivas salvas em: {CSV_DESCRITIVAS}")
    print(df_descritivas.to_string(index=False))

    # 2. Correlacoes de Spearman por RQ
    linhas_corr = []
    for rq_id, rq_info in RQS.items():
        col_proc = rq_info["metrica_processo"]
        nome_proc = rq_info["nome_processo"]

        if col_proc not in df.columns:
            print(f"\nAVISO: coluna '{col_proc}' ausente. Pulando {rq_id}.")
            continue

        print(f"\n--- {rq_id}: {rq_info['titulo']} ---")

        for mq in METRICAS_QUALIDADE:
            corr = calcular_spearman(df, col_proc, mq)
            nome_mq = NOMES_QUALIDADE[mq]
            interp = interpretar_correlacao(corr["rho"])
            sig = "sim" if corr["p_valor"] < 0.05 else "nao"

            linhas_corr.append({
                "rq": rq_id,
                "metrica_processo": col_proc,
                "nome_processo": nome_proc,
                "metrica_qualidade": mq,
                "nome_qualidade": nome_mq,
                "rho": corr["rho"],
                "p_valor": corr["p_valor"],
                "n": corr["n"],
                "interpretacao": interp,
                "significativo_005": sig,
            })

            print(f"  {nome_mq}: rho={corr['rho']}, p={corr['p_valor']} ({interp}, sig={sig})")

            # Scatter plot
            gerar_scatter(
                df, col_proc, mq, nome_proc, nome_mq,
                f"{rq_id}: {nome_proc} x {nome_mq}",
                DIR_GRAFICOS / f"{rq_id}_scatter_{nome_mq.lower()}.png",
            )

            # Boxplot por quartil
            gerar_boxplots_quartil(
                df, col_proc, mq, nome_proc, nome_mq,
                DIR_GRAFICOS / f"{rq_id}_boxplot_{nome_mq.lower()}.png",
            )

    df_corr = pd.DataFrame(linhas_corr)
    df_corr.to_csv(CSV_CORRELACOES, index=False)
    print(f"\nCorrelacoes salvas em: {CSV_CORRELACOES}")
    print(df_corr.to_string(index=False))

    # 3. Heatmap geral
    colunas_proc = [rq["metrica_processo"] for rq in RQS.values() if rq["metrica_processo"] in df.columns]
    labels_proc = [rq["nome_processo"] for rq in RQS.values() if rq["metrica_processo"] in df.columns]
    labels_qual = [NOMES_QUALIDADE[m] for m in METRICAS_QUALIDADE]

    gerar_heatmap(df, colunas_proc, METRICAS_QUALIDADE, labels_proc, labels_qual,
                  DIR_GRAFICOS / "heatmap_correlacao.png")

    print(f"\nGraficos salvos em: {DIR_GRAFICOS}")
    print("Concluido. Use os CSVs e graficos para elaborar o relatorio.")


if __name__ == "__main__":
    main()
