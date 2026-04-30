"""
Lab 03 - Sprint 03: Analise estatistica do dataset de Pull Requests.

Le `output/lab3s2/pull_requests_com_reviews.csv` e produz:

  output/lab3s3/
    descritivas_globais.csv         estatisticas das metricas em todo o dataset
    descritivas_por_status.csv      estatisticas separadas por MERGED / CLOSED
    comparacao_status_mannwhitney.csv  RQ01-RQ04 (Mann-Whitney + Cliff's delta)
    correlacoes_spearman.csv        RQ05-RQ08 (Spearman + Pearson em log)
    resumo_rqs.md                   sumario textual com vereditos por RQ
    charts/*.png                    boxplots, scatter (log-log), heatmap, violin

Justificativa estatistica:
  - distribuicoes assimetricas com cauda longa -> testes nao parametricos.
  - RQ01-04: variavel dependente binaria (MERGED/CLOSED) -> Mann-Whitney U
    + Cliff's delta para tamanho do efeito + ponto-bisserial complementar.
  - RQ05-08: variavel dependente numerica (numero_reviews) -> Spearman rho;
    Pearson r em log(x+1) como verificacao em escala expandida.
  - alpha = 0.05; correcao Bonferroni e Holm sobre os p-valores das 8 RQs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats


DIR_PROJETO = Path(__file__).resolve().parent.parent
DIR_LAB3S2 = DIR_PROJETO / "output" / "lab3s2"
DIR_LAB3S3 = DIR_PROJETO / "output" / "lab3s3"
DIR_GRAFICOS = DIR_LAB3S3 / "charts"
CSV_PRS = DIR_LAB3S2 / "pull_requests_com_reviews.csv"

CSV_DESC_GLOBAIS = DIR_LAB3S3 / "descritivas_globais.csv"
CSV_DESC_STATUS = DIR_LAB3S3 / "descritivas_por_status.csv"
CSV_COMPARACAO = DIR_LAB3S3 / "comparacao_status_mannwhitney.csv"
CSV_CORRELACOES = DIR_LAB3S3 / "correlacoes_spearman.csv"
MD_RESUMO = DIR_LAB3S3 / "resumo_rqs.md"

ALPHA = 0.05

METRICAS = {
    "tamanho": ["changed_files", "additions", "deletions", "loc_total"],
    "tempo":   ["tempo_analise_horas"],
    "descricao": ["descricao_tamanho_chars"],
    "interacoes": ["num_participantes", "total_comentarios"],
}

NOMES = {
    "changed_files": "Arquivos alterados",
    "additions": "Linhas adicionadas",
    "deletions": "Linhas removidas",
    "loc_total": "LOC total (add+del)",
    "tempo_analise_horas": "Tempo de analise (h)",
    "descricao_tamanho_chars": "Tamanho da descricao (chars)",
    "num_participantes": "Numero de participantes",
    "total_comentarios": "Total de comentarios",
    "numero_reviews": "Numero de revisoes",
}

RQS_STATUS = {
    "RQ01": {"dimensao": "tamanho",   "metricas": METRICAS["tamanho"]},
    "RQ02": {"dimensao": "tempo",     "metricas": METRICAS["tempo"]},
    "RQ03": {"dimensao": "descricao", "metricas": METRICAS["descricao"]},
    "RQ04": {"dimensao": "interacoes","metricas": METRICAS["interacoes"]},
}

RQS_REVIEWS = {
    "RQ05": {"dimensao": "tamanho",   "metricas": METRICAS["tamanho"]},
    "RQ06": {"dimensao": "tempo",     "metricas": METRICAS["tempo"]},
    "RQ07": {"dimensao": "descricao", "metricas": METRICAS["descricao"]},
    "RQ08": {"dimensao": "interacoes","metricas": METRICAS["interacoes"]},
}


def carregar_dataset() -> pd.DataFrame:
    if not CSV_PRS.exists():
        raise SystemExit(
            f"Dataset nao encontrado: {CSV_PRS}\n"
            "Execute primeiro: python laboratorio3/scripts/coleta_graphql_PRs.py"
        )
    df = pd.read_csv(CSV_PRS)
    df["status"] = df["status"].str.upper()
    df = df[df["status"].isin(["MERGED", "CLOSED"])].copy()

    if "tempo_analise_horas" not in df.columns and "tempo_analise_dias" in df.columns:
        df["tempo_analise_horas"] = pd.to_numeric(df["tempo_analise_dias"], errors="coerce") * 24.0
    if "loc_total" not in df.columns and {"additions", "deletions"} <= set(df.columns):
        df["loc_total"] = (
            pd.to_numeric(df["additions"], errors="coerce").fillna(0)
            + pd.to_numeric(df["deletions"], errors="coerce").fillna(0)
        )
    return df


def descritivas(df: pd.DataFrame, colunas: list[str], grupo: Optional[str] = None) -> pd.DataFrame:
    linhas = []
    for col in colunas:
        if col not in df.columns:
            continue
        s = pd.to_numeric(df[col], errors="coerce").dropna()
        if s.empty:
            continue
        linhas.append({
            "grupo": grupo or "TODOS",
            "metrica": col,
            "n": int(len(s)),
            "media":   round(float(s.mean()), 4),
            "mediana": round(float(s.median()), 4),
            "desvio_padrao": round(float(s.std()), 4),
            "min": round(float(s.min()), 4),
            "p25": round(float(s.quantile(0.25)), 4),
            "p75": round(float(s.quantile(0.75)), 4),
            "p95": round(float(s.quantile(0.95)), 4),
            "max": round(float(s.max()), 4),
            "iqr": round(float(s.quantile(0.75) - s.quantile(0.25)), 4),
        })
    return pd.DataFrame(linhas)


def cliffs_delta(x: np.ndarray, y: np.ndarray) -> float:
    """
    Implementacao eficiente de Cliff's delta usando ranks.
    delta = (#x > y - #x < y) / (n_x * n_y)
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n_x, n_y = len(x), len(y)
    if n_x == 0 or n_y == 0:
        return float("nan")

    todos = np.concatenate([x, y])
    rank_todos = stats.rankdata(todos, method="average")
    soma_rank_x = rank_todos[:n_x].sum()
    U_x = soma_rank_x - n_x * (n_x + 1) / 2
    delta = (2 * U_x) / (n_x * n_y) - 1
    return float(delta)


def interpretar_cliff(delta: float) -> str:
    a = abs(delta)
    if a < 0.147:
        return "desprezivel"
    if a < 0.33:
        return "pequeno"
    if a < 0.474:
        return "medio"
    return "grande"


def interpretar_rho(rho: float) -> str:
    if rho is None or (isinstance(rho, float) and np.isnan(rho)):
        return "indefinido"
    a = abs(rho)
    direcao = "positiva" if rho >= 0 else "negativa"
    if a < 0.1:
        forca = "desprezivel"
    elif a < 0.3:
        forca = "fraca"
    elif a < 0.5:
        forca = "moderada"
    elif a < 0.7:
        forca = "forte"
    else:
        forca = "muito forte"
    return f"{forca} {direcao}"


def ajuste_holm(p_valores: list[float]) -> list[float]:
    """Correcao de Holm-Bonferroni step-down para uma lista de p-valores."""
    n = len(p_valores)
    if n == 0:
        return []
    indexados = sorted(enumerate(p_valores), key=lambda t: t[1])
    ajustados = [0.0] * n
    maior = 0.0
    for k, (idx, p) in enumerate(indexados):
        ajuste = (n - k) * p
        ajuste = min(ajuste, 1.0)
        if ajuste < maior:
            ajuste = maior
        else:
            maior = ajuste
        ajustados[idx] = ajuste
    return ajustados


def ic95_bootstrap_mediana(serie: pd.Series, n_iter: int = 1000, seed: int = 42) -> tuple[float, float]:
    valores = serie.dropna().to_numpy()
    if len(valores) < 5:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    medianas = np.empty(n_iter)
    n = len(valores)
    for i in range(n_iter):
        medianas[i] = np.median(rng.choice(valores, size=n, replace=True))
    lo, hi = np.percentile(medianas, [2.5, 97.5])
    return (round(float(lo), 4), round(float(hi), 4))


def ic95_bootstrap_rho(x: pd.Series, y: pd.Series, n_iter: int = 1000, seed: int = 42) -> tuple[float, float]:
    pares = pd.concat([x, y], axis=1).dropna()
    if len(pares) < 10:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    n = len(pares)
    rhos = np.empty(n_iter)
    arr = pares.to_numpy()
    for i in range(n_iter):
        idx = rng.integers(0, n, size=n)
        amostra = arr[idx]
        rho, _ = stats.spearmanr(amostra[:, 0], amostra[:, 1])
        rhos[i] = rho if not np.isnan(rho) else 0.0
    lo, hi = np.percentile(rhos, [2.5, 97.5])
    return (round(float(lo), 4), round(float(hi), 4))


def comparar_status(df: pd.DataFrame) -> pd.DataFrame:
    """RQ01-RQ04: Mann-Whitney U + Cliff's delta + ponto-bisserial."""
    merged = df[df["status"] == "MERGED"]
    closed = df[df["status"] == "CLOSED"]

    linhas = []
    for rq, info in RQS_STATUS.items():
        for col in info["metricas"]:
            if col not in df.columns:
                continue
            x = pd.to_numeric(merged[col], errors="coerce").dropna()
            y = pd.to_numeric(closed[col], errors="coerce").dropna()
            if len(x) < 5 or len(y) < 5:
                continue

            u, p_mw = stats.mannwhitneyu(x, y, alternative="two-sided")
            delta = cliffs_delta(x.to_numpy(), y.to_numpy())

            df_pb = pd.DataFrame({
                "valor": pd.concat([x, y], ignore_index=True),
                "binario": [1] * len(x) + [0] * len(y),
            })
            r_pb, p_pb = stats.pointbiserialr(df_pb["binario"], df_pb["valor"])

            ic_lo_m, ic_hi_m = ic95_bootstrap_mediana(x)
            ic_lo_c, ic_hi_c = ic95_bootstrap_mediana(y)

            linhas.append({
                "rq": rq,
                "dimensao": info["dimensao"],
                "metrica": col,
                "nome_metrica": NOMES.get(col, col),
                "n_merged": int(len(x)),
                "n_closed": int(len(y)),
                "mediana_merged": round(float(x.median()), 4),
                "mediana_closed": round(float(y.median()), 4),
                "mediana_merged_ic95": f"[{ic_lo_m}, {ic_hi_m}]",
                "mediana_closed_ic95": f"[{ic_lo_c}, {ic_hi_c}]",
                "U_mannwhitney": round(float(u), 2),
                "p_valor_mw": round(float(p_mw), 6),
                "cliffs_delta": round(float(delta), 4),
                "interpretacao_efeito": interpretar_cliff(delta),
                "r_pointbiserial": round(float(r_pb), 4),
                "p_valor_pb": round(float(p_pb), 6),
                "significativo_005": "sim" if p_mw < ALPHA else "nao",
            })

    if not linhas:
        return pd.DataFrame()

    df_res = pd.DataFrame(linhas)
    df_res["p_holm"] = ajuste_holm(df_res["p_valor_mw"].tolist())
    df_res["p_bonferroni"] = (df_res["p_valor_mw"] * len(df_res)).clip(upper=1.0).round(6)
    df_res["significativo_holm"] = (df_res["p_holm"] < ALPHA).map({True: "sim", False: "nao"})
    return df_res


def correlacoes_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """RQ05-RQ08: Spearman + Pearson em log(x+1) com numero_reviews."""
    if "numero_reviews" not in df.columns:
        return pd.DataFrame()

    y = pd.to_numeric(df["numero_reviews"], errors="coerce")
    linhas = []
    for rq, info in RQS_REVIEWS.items():
        for col in info["metricas"]:
            if col not in df.columns:
                continue
            x = pd.to_numeric(df[col], errors="coerce")
            pares = pd.concat([x, y], axis=1).dropna()
            if len(pares) < 10:
                continue

            if pares[col].nunique() < 2 or pares["numero_reviews"].nunique() < 2:
                rho, p_sp = float("nan"), float("nan")
                r_log, p_log = float("nan"), float("nan")
                ic_lo, ic_hi = float("nan"), float("nan")
            else:
                rho, p_sp = stats.spearmanr(pares[col], pares["numero_reviews"])
                ic_lo, ic_hi = ic95_bootstrap_rho(pares[col], pares["numero_reviews"])
                log_x = np.log1p(pares[col].clip(lower=0))
                log_y = np.log1p(pares["numero_reviews"].clip(lower=0))
                if log_x.nunique() < 2 or log_y.nunique() < 2:
                    r_log, p_log = float("nan"), float("nan")
                else:
                    r_log, p_log = stats.pearsonr(log_x, log_y)

            linhas.append({
                "rq": rq,
                "dimensao": info["dimensao"],
                "metrica": col,
                "nome_metrica": NOMES.get(col, col),
                "n": int(len(pares)),
                "spearman_rho": round(float(rho), 4),
                "p_valor_spearman": round(float(p_sp), 6),
                "ic95_rho": f"[{ic_lo}, {ic_hi}]",
                "pearson_log_r": round(float(r_log), 4),
                "p_valor_pearson_log": round(float(p_log), 6),
                "interpretacao": interpretar_rho(rho),
                "significativo_005": "sim" if p_sp < ALPHA else "nao",
            })

    if not linhas:
        return pd.DataFrame()

    df_res = pd.DataFrame(linhas)
    p_para_ajuste = df_res["p_valor_spearman"].fillna(1.0).tolist()
    df_res["p_holm"] = ajuste_holm(p_para_ajuste)
    df_res["p_bonferroni"] = (df_res["p_valor_spearman"].fillna(1.0) * len(df_res)).clip(upper=1.0).round(6)
    df_res["significativo_holm"] = (df_res["p_holm"] < ALPHA).map({True: "sim", False: "nao"})
    return df_res


def boxplot_status(df: pd.DataFrame, col: str, caminho: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 5))
    dados = []
    rotulos = []
    for rotulo in ("MERGED", "CLOSED"):
        s = pd.to_numeric(df[df["status"] == rotulo][col], errors="coerce").dropna()
        if not s.empty:
            dados.append(s.values)
            rotulos.append(f"{rotulo} (n={len(s)})")
    if not dados:
        plt.close(fig)
        return
    ax.boxplot(dados, tick_labels=rotulos, showfliers=False)
    ax.set_ylabel(NOMES.get(col, col))
    ax.set_title(f"{NOMES.get(col, col)} por status")
    fig.tight_layout()
    fig.savefig(caminho, dpi=140)
    plt.close(fig)


def scatter_loglog(df: pd.DataFrame, col_x: str, caminho: Path) -> None:
    pares = df[[col_x, "numero_reviews"]].apply(pd.to_numeric, errors="coerce").dropna()
    if len(pares) < 10:
        return
    if pares[col_x].nunique() < 2 or pares["numero_reviews"].nunique() < 2:
        return
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(pares[col_x] + 1, pares["numero_reviews"] + 1, alpha=0.25, s=12, edgecolors="none")
    if (pares[col_x] >= 0).all():
        ax.set_xscale("log")
    ax.set_yscale("log")
    rho, p = stats.spearmanr(pares[col_x], pares["numero_reviews"])
    ax.set_xlabel(NOMES.get(col_x, col_x) + " (log)")
    ax.set_ylabel(NOMES.get("numero_reviews") + " (log)")
    ax.set_title(f"{NOMES.get(col_x, col_x)} x {NOMES['numero_reviews']}\nSpearman rho={rho:.3f} (p={p:.3g}, n={len(pares)})")
    fig.tight_layout()
    fig.savefig(caminho, dpi=140)
    plt.close(fig)


def heatmap_spearman(df: pd.DataFrame, caminho: Path) -> None:
    colunas = [c for grp in METRICAS.values() for c in grp]
    colunas = [c for c in colunas if c in df.columns]
    if not colunas or "numero_reviews" not in df.columns:
        return

    matriz = []
    for c in colunas:
        pares = pd.concat([
            pd.to_numeric(df[c], errors="coerce"),
            pd.to_numeric(df["numero_reviews"], errors="coerce"),
        ], axis=1).dropna()
        if len(pares) < 10 or pares.iloc[:, 0].nunique() < 2 or pares.iloc[:, 1].nunique() < 2:
            matriz.append([np.nan])
            continue
        rho, _ = stats.spearmanr(pares.iloc[:, 0], pares.iloc[:, 1])
        matriz.append([round(rho, 3)])

    df_heat = pd.DataFrame(matriz, index=[NOMES.get(c, c) for c in colunas], columns=["numero_reviews"])
    fig, ax = plt.subplots(figsize=(5, 0.7 * len(df_heat) + 1.5))
    sns.heatmap(df_heat, annot=True, cmap="RdBu_r", center=0, vmin=-1, vmax=1, ax=ax)
    ax.set_title("Spearman: metricas x numero_reviews")
    fig.tight_layout()
    fig.savefig(caminho, dpi=140)
    plt.close(fig)


def violin_distribuicao(df: pd.DataFrame, col: str, caminho: Path) -> None:
    s = pd.to_numeric(df[col], errors="coerce").dropna()
    if s.empty:
        return
    fig, ax = plt.subplots(figsize=(7, 4))
    log_s = np.log1p(s.clip(lower=0))
    ax.violinplot(log_s.values, vert=False, showmedians=True)
    ax.set_xlabel(f"log(1 + {NOMES.get(col, col)})")
    ax.set_yticks([])
    ax.set_title(f"Distribuicao: {NOMES.get(col, col)} (escala log)")
    fig.tight_layout()
    fig.savefig(caminho, dpi=140)
    plt.close(fig)


def gerar_resumo_md(df: pd.DataFrame, df_status: pd.DataFrame, df_corr: pd.DataFrame) -> None:
    n_total = len(df)
    n_merged = (df["status"] == "MERGED").sum()
    n_closed = (df["status"] == "CLOSED").sum()
    n_repos = df["repo_completo"].nunique() if "repo_completo" in df.columns else 0

    linhas = [
        "# Resumo das RQs - Lab 03",
        "",
        f"- Total de PRs: **{n_total}**",
        f"- MERGED: **{n_merged}** | CLOSED: **{n_closed}**",
        f"- Repositorios distintos: **{n_repos}**",
        f"- alpha = {ALPHA} (Holm step-down aplicado)",
        "",
        "## Dimensao A - Feedback final (MERGED vs CLOSED)",
        "",
        "| RQ | Metrica | Mediana MERGED | Mediana CLOSED | p-valor | p-Holm | Cliff delta | Efeito |",
        "|----|---------|---------------:|---------------:|--------:|-------:|------------:|--------|",
    ]
    for _, r in df_status.iterrows():
        linhas.append(
            f"| {r['rq']} | {r['nome_metrica']} | {r['mediana_merged']} | {r['mediana_closed']} | "
            f"{r['p_valor_mw']:.3g} | {r['p_holm']:.3g} | {r['cliffs_delta']} | {r['interpretacao_efeito']} |"
        )

    linhas += [
        "",
        "## Dimensao B - Numero de revisoes",
        "",
        "| RQ | Metrica | n | Spearman rho | p-valor | p-Holm | IC95 rho | Interpretacao |",
        "|----|---------|--:|-------------:|--------:|-------:|----------|---------------|",
    ]
    for _, r in df_corr.iterrows():
        linhas.append(
            f"| {r['rq']} | {r['nome_metrica']} | {r['n']} | {r['spearman_rho']} | "
            f"{r['p_valor_spearman']:.3g} | {r['p_holm']:.3g} | {r['ic95_rho']} | {r['interpretacao']} |"
        )

    MD_RESUMO.write_text("\n".join(linhas), encoding="utf-8")


def main() -> None:
    DIR_LAB3S3.mkdir(parents=True, exist_ok=True)
    DIR_GRAFICOS.mkdir(parents=True, exist_ok=True)

    df = carregar_dataset()
    print(f"PRs carregados: {len(df)} | repos: {df['repo_completo'].nunique()}")
    print(f"MERGED: {(df['status']=='MERGED').sum()} | CLOSED: {(df['status']=='CLOSED').sum()}")

    todas_metricas = [c for grp in METRICAS.values() for c in grp] + ["numero_reviews"]
    df_global = descritivas(df, todas_metricas, grupo="TODOS")
    df_global.to_csv(CSV_DESC_GLOBAIS, index=False)
    print(f"OK descritivas globais: {CSV_DESC_GLOBAIS}")

    df_merged = descritivas(df[df["status"] == "MERGED"], todas_metricas, grupo="MERGED")
    df_closed = descritivas(df[df["status"] == "CLOSED"], todas_metricas, grupo="CLOSED")
    pd.concat([df_merged, df_closed], ignore_index=True).to_csv(CSV_DESC_STATUS, index=False)
    print(f"OK descritivas por status: {CSV_DESC_STATUS}")

    df_status = comparar_status(df)
    if not df_status.empty:
        df_status.to_csv(CSV_COMPARACAO, index=False)
        print(f"OK RQ01-RQ04: {CSV_COMPARACAO}")
    else:
        print("aviso: sem dados suficientes para RQ01-RQ04")

    df_corr = correlacoes_reviews(df)
    if not df_corr.empty:
        df_corr.to_csv(CSV_CORRELACOES, index=False)
        print(f"OK RQ05-RQ08: {CSV_CORRELACOES}")
    else:
        print("aviso: sem dados suficientes para RQ05-RQ08")

    print("\nGerando graficos...")
    for col in [c for grp in METRICAS.values() for c in grp]:
        if col in df.columns:
            boxplot_status(df, col, DIR_GRAFICOS / f"boxplot_{col}_status.png")
            scatter_loglog(df, col, DIR_GRAFICOS / f"scatter_{col}_x_reviews.png")
            violin_distribuicao(df, col, DIR_GRAFICOS / f"violin_{col}.png")

    heatmap_spearman(df, DIR_GRAFICOS / "heatmap_spearman_reviews.png")

    if not df_status.empty and not df_corr.empty:
        gerar_resumo_md(df, df_status, df_corr)
        print(f"OK resumo: {MD_RESUMO}")

    print(f"\nGraficos em: {DIR_GRAFICOS}")
    print("Concluido.")


if __name__ == "__main__":
    main()
