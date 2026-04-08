"""
Sprint 02 — Analise estatistica e geracao do relatorio final.

Para cada RQ:
  - Estatisticas descritivas (media, mediana, desvio padrao)
  - Correlacao de Spearman com p-valor
  - Graficos: scatter plots, heatmap de correlacao, boxplots por quartil

Gera:
  - output/charts/*.png
  - output/relatorio_final_sprint2.md
"""

from pathlib import Path
from datetime import datetime, timezone

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
RELATORIO = DIR_SAIDA / "relatorio_final_sprint2.md"

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

def calcular_descritivas(df: pd.DataFrame, coluna: str) -> dict:
    serie = df[coluna].dropna()
    return {
        "media": round(float(serie.mean()), 4),
        "mediana": round(float(serie.median()), 4),
        "desvio_padrao": round(float(serie.std()), 4),
        "min": round(float(serie.min()), 4),
        "max": round(float(serie.max()), 4),
        "n": len(serie),
    }


def calcular_spearman(df: pd.DataFrame, col_x: str, col_y: str) -> dict:
    """Correlacao de Spearman entre duas colunas, ignorando NaN."""
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

    # Linha de tendencia (regressao linear sobre ranks para consistencia com Spearman)
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
    """Heatmap de correlacao Spearman entre metricas de processo e qualidade."""
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
    """Boxplot da metrica de qualidade agrupada por quartil da metrica de processo."""
    limpo = df[[col_processo, col_qualidade]].dropna().copy()
    if len(limpo) < 4:
        return

    limpo["quartil"] = pd.qcut(limpo[col_processo], q=4, labels=["Q1", "Q2", "Q3", "Q4"],
                                duplicates="drop")
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
# Geracao do relatorio Markdown
# ---------------------------------------------------------------------------

def gerar_relatorio(df: pd.DataFrame, resultados_rqs: dict) -> str:
    agora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    n = len(df)

    md = []
    md.append("# Laboratorio 02 — Relatorio Final (Sprint 02)")
    md.append("")
    md.append("## 1. Introducao")
    md.append("")
    md.append("Este relatorio apresenta a analise de qualidade interna de repositorios ")
    md.append("Java open-source populares do GitHub, correlacionando caracteristicas do ")
    md.append("processo de desenvolvimento com metricas de qualidade de codigo calculadas ")
    md.append("pela ferramenta CK.")
    md.append("")
    md.append("### 1.1 Hipoteses Informais")
    md.append("")
    md.append("- **H1 (RQ01):** Repositorios mais populares tendem a ter menor CBO e LCOM ")
    md.append("  (melhor modularidade e coesao), pois recebem mais revisao da comunidade.")
    md.append("- **H2 (RQ02):** Repositorios mais maduros tendem a ter maior DIT e CBO ")
    md.append("  (maior complexidade acumulada ao longo do tempo).")
    md.append("- **H3 (RQ03):** Repositorios com mais releases tendem a ter menor LCOM e CBO ")
    md.append("  (ciclos de release frequentes incentivam refatoracao).")
    md.append("- **H4 (RQ04):** Repositorios maiores (mais LOC) tendem a ter maior CBO e LCOM ")
    md.append("  (mais acoplamento e menos coesao por escala).")
    md.append("")

    md.append("## 2. Metodologia")
    md.append("")
    md.append("### 2.1 GQM (Goal-Question-Metric)")
    md.append("")
    md.append("**Goal:** Analisar a qualidade interna de repositorios Java open-source populares ")
    md.append("do GitHub, correlacionando caracteristicas de processo com metricas CK.")
    md.append("")
    md.append("| RQ | Questao | Metrica de Processo | Metricas de Qualidade |")
    md.append("|---|---|---|---|")
    md.append("| RQ01 | Popularidade x Qualidade | Estrelas | CBO, DIT, LCOM |")
    md.append("| RQ02 | Maturidade x Qualidade | Idade (anos) | CBO, DIT, LCOM |")
    md.append("| RQ03 | Atividade x Qualidade | Releases | CBO, DIT, LCOM |")
    md.append("| RQ04 | Tamanho x Qualidade | LOC | CBO, DIT, LCOM |")
    md.append("")
    md.append("### 2.2 Coleta de Dados")
    md.append("")
    md.append("- Fonte: API REST do GitHub + ferramenta CK v0.7.0")
    md.append(f"- Amostra: {n} repositorios Java mais populares (por estrelas)")
    md.append("- Metricas de processo: estrelas, idade, releases, LOC")
    md.append("- Metricas de qualidade: CBO, DIT, LCOM (sumarizadas por repositorio: mediana)")
    md.append("- Teste estatistico: correlacao de Spearman (adequada para dados nao-normais)")
    md.append(f"- Data da analise: {agora}")
    md.append("")

    md.append("## 3. Resultados")
    md.append("")

    # Estatisticas descritivas globais
    md.append("### 3.1 Estatisticas Descritivas Globais")
    md.append("")
    md.append("| Metrica | Media | Mediana | Desvio Padrao | Min | Max |")
    md.append("|---|---|---|---|---|---|")

    for col in ["estrelas", "idade_anos", "total_releases", "loc_total",
                "cbo_mediana", "dit_mediana", "lcom_mediana"]:
        if col in df.columns:
            d = calcular_descritivas(df, col)
            md.append(f"| {col} | {d['media']} | {d['mediana']} | "
                      f"{d['desvio_padrao']} | {d['min']} | {d['max']} |")
    md.append("")

    # Resultados por RQ
    for rq_id, rq_info in RQS.items():
        resultado = resultados_rqs[rq_id]
        md.append(f"### 3.2 {rq_id}: {rq_info['titulo']}")
        md.append("")
        md.append(f"**Metrica de processo:** {rq_info['nome_processo']} (`{rq_info['metrica_processo']}`)")
        md.append("")
        md.append("| Metrica Qualidade | rho (Spearman) | p-valor | Interpretacao |")
        md.append("|---|---|---|---|")

        for mq in METRICAS_QUALIDADE:
            corr = resultado["correlacoes"][mq]
            interp = interpretar_correlacao(corr["rho"])
            sig = "significativo" if corr["p_valor"] < 0.05 else "nao significativo"
            md.append(
                f"| {NOMES_QUALIDADE[mq]} | {corr['rho']} | {corr['p_valor']} | "
                f"{interp} ({sig}) |"
            )
        md.append("")

        md.append(f"![Scatter {rq_id} CBO](charts/{rq_id}_scatter_cbo.png)")
        md.append(f"![Scatter {rq_id} DIT](charts/{rq_id}_scatter_dit.png)")
        md.append(f"![Scatter {rq_id} LCOM](charts/{rq_id}_scatter_lcom.png)")
        md.append(f"![Boxplot {rq_id} CBO](charts/{rq_id}_boxplot_cbo.png)")
        md.append(f"![Boxplot {rq_id} DIT](charts/{rq_id}_boxplot_dit.png)")
        md.append(f"![Boxplot {rq_id} LCOM](charts/{rq_id}_boxplot_lcom.png)")
        md.append("")

    md.append("### 3.3 Heatmap de Correlacao Geral")
    md.append("")
    md.append("![Heatmap de Correlacao](charts/heatmap_correlacao.png)")
    md.append("")

    md.append("## 4. Discussao")
    md.append("")

    for rq_id, rq_info in RQS.items():
        resultado = resultados_rqs[rq_id]
        md.append(f"### {rq_id}: {rq_info['titulo']}")
        md.append("")
        for mq in METRICAS_QUALIDADE:
            corr = resultado["correlacoes"][mq]
            nome_mq = NOMES_QUALIDADE[mq]
            interp = interpretar_correlacao(corr["rho"])
            if corr["p_valor"] < 0.05:
                md.append(
                    f"- **{nome_mq}**: correlacao {interp} (rho={corr['rho']}, "
                    f"p={corr['p_valor']}). Resultado estatisticamente significativo."
                )
            else:
                md.append(
                    f"- **{nome_mq}**: correlacao {interp} (rho={corr['rho']}, "
                    f"p={corr['p_valor']}). Resultado **nao** estatisticamente significativo."
                )
        md.append("")

    md.append("### Confronto com Hipoteses")
    md.append("")
    md.append("As hipoteses informais serao confirmadas ou refutadas com base nos ")
    md.append("coeficientes de Spearman acima. Valores de rho proximos de zero indicam ")
    md.append("ausencia de relacao monotonica; p-valores acima de 0.05 indicam que a ")
    md.append("correlacao observada nao e estatisticamente significativa.")
    md.append("")

    md.append("## 5. Conclusao")
    md.append("")
    md.append(f"Este estudo analisou {n} repositorios Java populares do GitHub, ")
    md.append("correlacionando metricas de processo (popularidade, maturidade, atividade, ")
    md.append("tamanho) com metricas de qualidade interna (CBO, DIT, LCOM) obtidas via CK. ")
    md.append("Os resultados permitem observar tendencias gerais sobre como caracteristicas ")
    md.append("do processo de desenvolvimento se relacionam com a qualidade do codigo.")
    md.append("")
    md.append("**Limitacoes:**")
    md.append("- Analise limitada ao branch principal (shallow clone).")
    md.append("- Repositorios com poucos arquivos .java podem distorcer medianas.")
    md.append("- Repositorios muito grandes (>500 MB) foram excluidos da amostra.")
    md.append("")

    return "\n".join(md)


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

    resultados_rqs: dict = {}

    for rq_id, rq_info in RQS.items():
        col_proc = rq_info["metrica_processo"]
        nome_proc = rq_info["nome_processo"]

        if col_proc not in df.columns:
            print(f"AVISO: coluna '{col_proc}' ausente no CSV. Pulando {rq_id}.")
            continue

        print(f"\n--- {rq_id}: {rq_info['titulo']} ---")

        correlacoes = {}
        for mq in METRICAS_QUALIDADE:
            corr = calcular_spearman(df, col_proc, mq)
            correlacoes[mq] = corr
            nome_mq = NOMES_QUALIDADE[mq]
            print(f"  {nome_mq}: rho={corr['rho']}, p={corr['p_valor']} "
                  f"({interpretar_correlacao(corr['rho'])})")

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

        resultados_rqs[rq_id] = {"correlacoes": correlacoes}

    # Heatmap geral
    colunas_proc = [rq["metrica_processo"] for rq in RQS.values() if rq["metrica_processo"] in df.columns]
    labels_proc = [rq["nome_processo"] for rq in RQS.values() if rq["metrica_processo"] in df.columns]
    labels_qual = [NOMES_QUALIDADE[m] for m in METRICAS_QUALIDADE]

    gerar_heatmap(df, colunas_proc, METRICAS_QUALIDADE, labels_proc, labels_qual,
                  DIR_GRAFICOS / "heatmap_correlacao.png")

    # Gerar relatorio Markdown
    print("\nGerando relatorio...")
    texto = gerar_relatorio(df, resultados_rqs)
    RELATORIO.write_text(texto, encoding="utf-8")
    print(f"Relatorio gerado em: {RELATORIO}")
    print(f"Graficos em: {DIR_GRAFICOS}")


if __name__ == "__main__":
    main()
