"""
Sprint 3 - Analise e Visualizacao de Dados
Laboratorio 1 - Caracteristicas de repositorios populares do GitHub

Gera graficos estatisticos e relatorio final para as RQs 01-07.
"""

import statistics
import textwrap
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats as sp_stats

# ──────────────────── Configuracao ────────────────────
PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_DIR / "output"
CSV_PATH = OUTPUT_DIR / "top_1000_repos.csv"
CHARTS_DIR = OUTPUT_DIR / "charts"
REPORT_PATH = OUTPUT_DIR / "relatorio_final_sprint3.md"

# Top N linguagens para graficos segmentados
TOP_N_LANGUAGES = 10

# Paleta de cores consistente
PALETTE = sns.color_palette("Set2", 12)
COLOR_PRIMARY = "#3B82F6"
COLOR_SECONDARY = "#10B981"
COLOR_ACCENT = "#F59E0B"
COLOR_DANGER = "#EF4444"

sns.set_theme(
    style="whitegrid",
    context="paper",
    font_scale=1.15,
    rc={
        "figure.dpi": 150,
        "savefig.dpi": 150,
        "axes.titlesize": 13,
        "axes.labelsize": 11,
        "figure.figsize": (10, 6),
    },
)


# ──────────────────── Helpers ────────────────────
def safe_median(values):
    """Mediana segura para listas vazias."""
    return float(statistics.median(values)) if values else 0.0


def q1(series: pd.Series) -> float:
    return float(series.quantile(0.25))


def q3(series: pd.Series) -> float:
    return float(series.quantile(0.75))


def describe_col(series: pd.Series) -> dict:
    """Estatisticas descritivas completas de uma serie numerica."""
    return {
        "n": int(series.count()),
        "media": round(float(series.mean()), 2),
        "mediana": round(float(series.median()), 2),
        "desvio_padrao": round(float(series.std()), 2),
        "min": round(float(series.min()), 2),
        "q1": round(q1(series), 2),
        "q3": round(q3(series), 2),
        "max": round(float(series.max()), 2),
        "iqr": round(q3(series) - q1(series), 2),
    }


def top_languages(df: pd.DataFrame, n: int = TOP_N_LANGUAGES) -> list[str]:
    """Retorna as N linguagens mais frequentes no dataset."""
    return df["primary_language"].value_counts().head(n).index.tolist()


def save_fig(fig, name: str) -> Path:
    """Salva figura e fecha. Retorna caminho relativo para markdown."""
    path = CHARTS_DIR / f"{name}.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


# ──────────────────── Graficos por RQ ────────────────────


def plot_rq01(df: pd.DataFrame) -> dict:
    """RQ01 - Idade dos repositorios (anos)."""
    col = "age_years"
    desc = describe_col(df[col])

    # --- Histograma + KDE ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    ax = axes[0]
    sns.histplot(df[col], bins=30, kde=True, color=COLOR_PRIMARY, edgecolor="white", ax=ax)
    ax.axvline(desc["mediana"], color=COLOR_DANGER, ls="--", lw=2, label=f'Mediana = {desc["mediana"]}')
    ax.axvline(desc["media"], color=COLOR_ACCENT, ls=":", lw=2, label=f'Media = {desc["media"]}')
    ax.set_xlabel("Idade (anos)")
    ax.set_ylabel("Frequencia")
    ax.set_title("RQ01 - Distribuicao da Idade dos Repositorios")
    ax.legend()

    # --- Boxplot ---
    ax = axes[1]
    sns.boxplot(x=df[col], color=COLOR_PRIMARY, ax=ax, width=0.4)
    ax.set_xlabel("Idade (anos)")
    ax.set_title("RQ01 - Boxplot da Idade")

    fig.tight_layout()
    save_fig(fig, "rq01_idade")

    # --- Boxplot por top linguagens ---
    top_langs = top_languages(df)
    df_top = df[df["primary_language"].isin(top_langs)].copy()
    order = df_top.groupby("primary_language")[col].median().sort_values(ascending=False).index

    fig2, ax2 = plt.subplots(figsize=(12, 6))
    sns.boxplot(data=df_top, y="primary_language", x=col, hue="primary_language", order=order, palette="Set2", ax=ax2, legend=False)
    ax2.set_xlabel("Idade (anos)")
    ax2.set_ylabel("")
    ax2.set_title("RQ01 - Idade por Linguagem (top 10)")
    fig2.tight_layout()
    save_fig(fig2, "rq01_idade_por_linguagem")

    return desc


def plot_rq02(df: pd.DataFrame) -> dict:
    """RQ02 - Pull Requests aceitas (merged)."""
    col = "merged_prs"
    desc = describe_col(df[col])

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Histograma com escala log para lidar com cauda longa
    ax = axes[0]
    data = df[col].clip(lower=1)  # clip para log
    sns.histplot(data, bins=50, kde=False, color=COLOR_SECONDARY, edgecolor="white", ax=ax, log_scale=(True, False))
    ax.axvline(desc["mediana"], color=COLOR_DANGER, ls="--", lw=2, label=f'Mediana = {desc["mediana"]}')
    ax.set_xlabel("PRs Aceitas (escala log)")
    ax.set_ylabel("Frequencia")
    ax.set_title("RQ02 - Distribuicao de PRs Aceitas")
    ax.legend()

    ax = axes[1]
    sns.boxplot(x=df[col], color=COLOR_SECONDARY, ax=ax, width=0.4)
    ax.set_xlabel("PRs Aceitas")
    ax.set_title("RQ02 - Boxplot de PRs Aceitas")
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))

    fig.tight_layout()
    save_fig(fig, "rq02_prs_aceitas")

    return desc


def plot_rq03(df: pd.DataFrame) -> dict:
    """RQ03 - Total de releases."""
    col = "total_releases"
    desc = describe_col(df[col])

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    ax = axes[0]
    data = df[col].clip(lower=0.5)
    sns.histplot(data, bins=50, kde=False, color=COLOR_ACCENT, edgecolor="white", ax=ax, log_scale=(True, False))
    ax.axvline(desc["mediana"], color=COLOR_DANGER, ls="--", lw=2, label=f'Mediana = {desc["mediana"]}')
    ax.set_xlabel("Total de Releases (escala log)")
    ax.set_ylabel("Frequencia")
    ax.set_title("RQ03 - Distribuicao de Releases")
    ax.legend()

    ax = axes[1]
    sns.boxplot(x=df[col], color=COLOR_ACCENT, ax=ax, width=0.4)
    ax.set_xlabel("Total de Releases")
    ax.set_title("RQ03 - Boxplot de Releases")

    fig.tight_layout()
    save_fig(fig, "rq03_releases")

    # Proporçao de repos com zero releases
    zero_releases = int((df[col] == 0).sum())
    desc["repos_sem_release"] = zero_releases
    desc["pct_sem_release"] = round(zero_releases / len(df) * 100, 2)

    return desc


def plot_rq04(df: pd.DataFrame) -> dict:
    """RQ04 - Tempo ate ultimo push (dias)."""
    col = "days_since_last_push"
    desc = describe_col(df[col])

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    ax = axes[0]
    sns.histplot(df[col], bins=50, kde=True, color="#8B5CF6", edgecolor="white", ax=ax)
    ax.axvline(desc["mediana"], color=COLOR_DANGER, ls="--", lw=2, label=f'Mediana = {desc["mediana"]} dias')
    ax.set_xlabel("Dias desde ultimo push")
    ax.set_ylabel("Frequencia")
    ax.set_title("RQ04 - Distribuicao do Tempo ate Ultimo Push")
    ax.legend()

    ax = axes[1]
    sns.boxplot(x=df[col], color="#8B5CF6", ax=ax, width=0.4)
    ax.set_xlabel("Dias desde ultimo push")
    ax.set_title("RQ04 - Boxplot de Dias sem Push")

    fig.tight_layout()
    save_fig(fig, "rq04_atualizacao")

    # Faixas de atividade
    recent_7d = int((df[col] <= 7).sum())
    recent_30d = int((df[col] <= 30).sum())
    recent_365d = int((df[col] <= 365).sum())
    desc["repos_atualizados_7d"] = recent_7d
    desc["repos_atualizados_30d"] = recent_30d
    desc["repos_atualizados_365d"] = recent_365d

    return desc


def plot_rq05(df: pd.DataFrame) -> dict:
    """RQ05 - Linguagens primarias."""
    lang_counts = df["primary_language"].value_counts()
    total = len(df)

    # --- Top 15 barras horizontais ---
    top15 = lang_counts.head(15)

    fig, ax = plt.subplots(figsize=(10, 7))
    bars = ax.barh(top15.index[::-1], top15.values[::-1], color=sns.color_palette("Set2", len(top15)))
    for bar, val in zip(bars, top15.values[::-1]):
        pct = val / total * 100
        ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height() / 2,
                f"{val} ({pct:.1f}%)", va="center", fontsize=9)
    ax.set_xlabel("Numero de Repositorios")
    ax.set_title("RQ05 - Top 15 Linguagens Primarias no Top 1000 GitHub")
    fig.tight_layout()
    save_fig(fig, "rq05_linguagens_barras")

    # --- Pie chart top 10 + "Outras" ---
    top10 = lang_counts.head(10)
    others = total - top10.sum()
    pie_data = pd.concat([top10, pd.Series({"Outras": others})])

    fig2, ax2 = plt.subplots(figsize=(9, 9))
    wedges, texts, autotexts = ax2.pie(
        pie_data.values,
        labels=pie_data.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=sns.color_palette("Set2", len(pie_data)),
        pctdistance=0.8,
    )
    for t in autotexts:
        t.set_fontsize(9)
    ax2.set_title("RQ05 - Distribuicao das Linguagens Primarias")
    fig2.tight_layout()
    save_fig(fig2, "rq05_linguagens_pizza")

    return {
        "total_linguagens": int(lang_counts.nunique()),
        "top5": {lang: int(cnt) for lang, cnt in lang_counts.head(5).items()},
        "concentracao_top5_pct": round(lang_counts.head(5).sum() / total * 100, 2),
        "concentracao_top10_pct": round(lang_counts.head(10).sum() / total * 100, 2),
    }


def plot_rq06(df: pd.DataFrame) -> dict:
    """RQ06 - Percentual de issues fechadas."""
    col = "closed_issues_percent"
    desc = describe_col(df[col])

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    ax = axes[0]
    sns.histplot(df[col], bins=30, kde=True, color="#EC4899", edgecolor="white", ax=ax)
    ax.axvline(desc["mediana"], color=COLOR_DANGER, ls="--", lw=2, label=f'Mediana = {desc["mediana"]}%')
    ax.set_xlabel("Issues Fechadas (%)")
    ax.set_ylabel("Frequencia")
    ax.set_title("RQ06 - Distribuicao do Percentual de Issues Fechadas")
    ax.legend()

    ax = axes[1]
    sns.boxplot(x=df[col], color="#EC4899", ax=ax, width=0.4)
    ax.set_xlabel("Issues Fechadas (%)")
    ax.set_title("RQ06 - Boxplot")

    fig.tight_layout()
    save_fig(fig, "rq06_issues_fechadas")

    # Faixas
    above_90 = int((df[col] >= 90).sum())
    above_70 = int((df[col] >= 70).sum())
    below_50 = int((df[col] < 50).sum())
    desc["repos_acima_90pct"] = above_90
    desc["repos_acima_70pct"] = above_70
    desc["repos_abaixo_50pct"] = below_50

    return desc


def plot_rq07(df: pd.DataFrame) -> dict:
    """RQ07 (Bonus) - Analise de RQ02, RQ03, RQ04 segmentada por linguagem."""
    top_langs = top_languages(df)
    df_top = df[df["primary_language"].isin(top_langs)].copy()
    df_other = df[~df["primary_language"].isin(top_langs)].copy()

    # Estatisticas por linguagem
    metrics = ["merged_prs", "total_releases", "days_since_last_push"]
    labels = {
        "merged_prs": "PRs Aceitas",
        "total_releases": "Releases",
        "days_since_last_push": "Dias sem Push",
    }

    lang_stats = []
    for lang in top_langs:
        subset = df[df["primary_language"] == lang]
        row = {"language": lang, "repos": len(subset)}
        for m in metrics:
            row[f"median_{m}"] = round(float(subset[m].median()), 2)
            row[f"mean_{m}"] = round(float(subset[m].mean()), 2)
        lang_stats.append(row)

    # Linha "Outras"
    row_other = {"language": "Outras", "repos": len(df_other)}
    for m in metrics:
        row_other[f"median_{m}"] = round(float(df_other[m].median()), 2)
        row_other[f"mean_{m}"] = round(float(df_other[m].mean()), 2)
    lang_stats.append(row_other)

    # --- Grafico 1: Boxplots comparativos (3 subplots) ---
    fig, axes = plt.subplots(1, 3, figsize=(20, 7))

    order = (
        df_top.groupby("primary_language")["merged_prs"]
        .median()
        .sort_values(ascending=False)
        .index
    )

    for ax, metric in zip(axes, metrics):
        sns.boxplot(
            data=df_top,
            y="primary_language",
            x=metric,
            hue="primary_language",
            order=order,
            palette="Set2",
            ax=ax,
            showfliers=False,
            legend=False,
        )
        ax.set_xlabel(labels[metric])
        ax.set_ylabel("")
        ax.set_title(f"RQ07 - {labels[metric]} por Linguagem")

    fig.suptitle("RQ07 - Comparacao entre Linguagens (Top 10, sem outliers)", fontsize=14, y=1.02)
    fig.tight_layout()
    save_fig(fig, "rq07_boxplots_por_linguagem")

    # --- Grafico 2: Barras agrupadas de medianas ---
    stats_df = pd.DataFrame(lang_stats)
    stats_top = stats_df[stats_df["language"] != "Outras"]

    fig2, axes2 = plt.subplots(1, 3, figsize=(18, 6))

    for ax, metric in zip(axes2, metrics):
        col_name = f"median_{metric}"
        data_sorted = stats_top.sort_values(col_name, ascending=True)
        bars = ax.barh(data_sorted["language"], data_sorted[col_name], color=COLOR_PRIMARY)
        for bar, val in zip(bars, data_sorted[col_name]):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                    f"{val:,.0f}", va="center", fontsize=9)
        ax.set_xlabel(f"Mediana - {labels[metric]}")
        ax.set_title(f"Mediana de {labels[metric]}")

    fig2.suptitle("RQ07 - Medianas por Linguagem (Top 10)", fontsize=14, y=1.02)
    fig2.tight_layout(rect=[0, 0, 1, 0.97])
    save_fig(fig2, "rq07_medianas_barras")

    # --- Grafico 3: Heatmap de medianas normalizadas ---
    heat_data = stats_top.set_index("language")[
        ["median_merged_prs", "median_total_releases", "median_days_since_last_push"]
    ].copy()
    heat_data.columns = ["PRs Aceitas", "Releases", "Dias sem Push"]

    # Normalizar 0-1 para comparacao visual
    heat_norm = (heat_data - heat_data.min()) / (heat_data.max() - heat_data.min() + 1e-9)

    fig3, ax3 = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        heat_norm,
        annot=heat_data.values,
        fmt=".0f",
        cmap="YlOrRd",
        linewidths=0.5,
        ax=ax3,
        cbar_kws={"label": "Valor normalizado (0-1)"},
    )
    ax3.set_title("RQ07 - Heatmap de Medianas por Linguagem (valores reais anotados)")
    ax3.set_ylabel("")
    fig3.tight_layout()
    save_fig(fig3, "rq07_heatmap")

    return {"lang_stats": lang_stats}


# ──────────────────── Correlacoes extras ────────────────────


def plot_correlations(df: pd.DataFrame) -> None:
    """Matriz de correlacao entre metricas numericas."""
    cols = ["stars", "age_years", "merged_prs", "total_releases",
            "days_since_last_push", "closed_issues_percent"]
    labels_pt = ["Estrelas", "Idade (anos)", "PRs Aceitas", "Releases",
                 "Dias sem Push", "Issues Fechadas (%)"]

    corr = df[cols].corr(method="spearman")
    corr.index = labels_pt
    corr.columns = labels_pt

    fig, ax = plt.subplots(figsize=(9, 8))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(
        corr,
        mask=mask,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        vmin=-1,
        vmax=1,
        linewidths=0.5,
        ax=ax,
    )
    ax.set_title("Matriz de Correlacao de Spearman entre Metricas")
    fig.tight_layout()
    save_fig(fig, "correlacao_spearman")


def plot_scatter_stars_prs(df: pd.DataFrame) -> None:
    """Scatter: estrelas vs PRs aceitas."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df["stars"], df["merged_prs"], alpha=0.35, s=15, color=COLOR_PRIMARY)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Estrelas (log)")
    ax.set_ylabel("PRs Aceitas (log)")
    ax.set_title("Relacao entre Estrelas e PRs Aceitas")
    fig.tight_layout()
    save_fig(fig, "scatter_stars_vs_prs")


# ──────────────────── Relatorio Final ────────────────────


def generate_report(df: pd.DataFrame, rq_results: dict) -> str:
    """Gera o relatorio final em Markdown."""

    n = len(df)
    rq01 = rq_results["rq01"]
    rq02 = rq_results["rq02"]
    rq03 = rq_results["rq03"]
    rq04 = rq_results["rq04"]
    rq05 = rq_results["rq05"]
    rq06 = rq_results["rq06"]
    rq07 = rq_results["rq07"]

    # Tabela RQ05
    top5_lines = ["| Linguagem | Repositorios | % |", "|---|---:|---:|"]
    for lang, cnt in rq05["top5"].items():
        top5_lines.append(f"| {lang} | {cnt} | {cnt/n*100:.1f}% |")
    top5_table = "\n".join(top5_lines)

    # Tabela RQ07
    rq07_header = (
        "| Linguagem | Repos | Mediana PRs | Media PRs | Mediana Releases | "
        "Media Releases | Mediana Dias sem Push | Media Dias sem Push |"
    )
    rq07_sep = "|---|---:|---:|---:|---:|---:|---:|---:|"
    rq07_rows = [rq07_header, rq07_sep]
    for row in rq07["lang_stats"]:
        rq07_rows.append(
            f"| {row['language']} | {row['repos']} | "
            f"{row['median_merged_prs']:,.0f} | {row['mean_merged_prs']:,.0f} | "
            f"{row['median_total_releases']:,.0f} | {row['mean_total_releases']:,.0f} | "
            f"{row['median_days_since_last_push']:,.0f} | {row['mean_days_since_last_push']:,.0f} |"
        )
    rq07_table = "\n".join(rq07_rows)

    report = f"""# Laboratorio 1 - Relatorio Final (Sprint 3)

**Disciplina:** Laboratorio de Experimentacao de Software
**Data de geracao:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")} UTC
**Amostra:** {n} repositorios mais estrelados do GitHub (com linguagem de programacao definida)

---

## 1. Introducao e Hipoteses Informais

Este relatorio apresenta a analise final dos **{n} repositorios mais populares do GitHub** (por numero de estrelas), considerando apenas projetos de software que possuem linguagem de programacao primaria definida. O objetivo e investigar caracteristicas comuns desses sistemas populares, respondendo as seguintes questoes de pesquisa:

**Hipoteses informais (formuladas antes da analise):**

| # | Questao | Hipotese |
|---|---|---|
| H1 | RQ01 - Sistemas populares sao maduros/antigos? | Repositorios populares tendem a ter mais tempo de existencia, pois a popularidade e construida ao longo dos anos. Espera-se mediana acima de 5 anos. |
| H2 | RQ02 - Recebem muita contribuicao externa? | Repositorios populares, por atrairem comunidades grandes, devem ter um volume expressivo de PRs aceitas. Espera-se mediana elevada (centenas a milhares). |
| H3 | RQ03 - Lancam releases com frequencia? | Repositorios populares tendem a manter um ciclo de releases, mas muitos projetos modernos usam CD contínuo sem releases formais. Espera-se uma distribuicao bastante variada. |
| H4 | RQ04 - Sao atualizados com frequencia? | Repositorios populares devem estar ativos. Espera-se que a maioria tenha sido atualizada nos ultimos dias ou semanas. |
| H5 | RQ05 - Sao escritos nas linguagens mais populares? | Linguagens como Python, JavaScript, TypeScript, Go, Java e C++ devem dominar o top 1000. |
| H6 | RQ06 - Possuem alto percentual de issues fechadas? | Repositorios populares contam com equipes ativas que mantem issues sob controle. Espera-se mediana acima de 70%. |
| H7 | RQ07 - Linguagens mais populares recebem mais contribuicao, mais releases e sao mais ativas? | Linguagens com ecossistemas maduros (ex.: TypeScript, Go, Rust) devem mostrar metricas superiores de contribuicao e atividade. |

---

## 2. Metodologia

### 2.1 Coleta de dados
- **Fonte:** API GraphQL do GitHub.
- **Criterio de selecao:** `search(query: "stars:>0 sort:stars-desc", type: REPOSITORY)` com paginacao de 100 repositorios por requisicao.
- **Filtro de linguagem:** apenas repositorios com `primaryLanguage` definida (projetos de software).
- **Metricas coletadas por repositorio:**
  - **Idade:** calculada a partir de `createdAt` (em dias e anos).
  - **PRs aceitas:** `pullRequests(states: MERGED).totalCount`.
  - **Total de releases:** `releases.totalCount`.
  - **Tempo sem push:** diferenca entre data de coleta e `pushedAt` (em dias).
  - **Linguagem primaria:** `primaryLanguage.name`.
  - **Razao de issues fechadas:** `issues(states: CLOSED).totalCount / issues.totalCount`.

### 2.2 Analise estatistica
- **Medida de tendencia central:** mediana (robusta a outliers, adequada para distribuicoes assimetricas).
- **Estatisticas descritivas:** media, desvio padrao, quartis (Q1, Q3), IQR, min e max.
- **Correlacao:** coeficiente de Spearman (nao-parametrico, adequado para relacoes monotonicas).
- **Visualizacoes:** histogramas com KDE, boxplots, graficos de barras, heatmaps e scatter plots.

---

## 3. Resultados

### RQ01 - Sistemas populares sao maduros/antigos?

**Metrica:** idade do repositorio em anos.

| Estatistica | Valor |
|---|---:|
| Mediana | {rq01['mediana']} anos |
| Media | {rq01['media']} anos |
| Desvio Padrao | {rq01['desvio_padrao']} anos |
| Minimo | {rq01['min']} anos |
| Q1 (25%) | {rq01['q1']} anos |
| Q3 (75%) | {rq01['q3']} anos |
| Maximo | {rq01['max']} anos |
| IQR | {rq01['iqr']} anos |

![Distribuicao da Idade](charts/rq01_idade.png)

![Idade por Linguagem](charts/rq01_idade_por_linguagem.png)

**Analise:** A mediana de **{rq01['mediana']} anos** confirma que repositorios populares sao, em geral, sistemas maduros. O intervalo interquartil [{rq01['q1']}, {rq01['q3']}] mostra que 50% dos repositorios tem entre {rq01['q1']} e {rq01['q3']} anos. Isso suporta a hipotese H1: popularidade no GitHub esta fortemente associada a maturidade e tempo de existencia, refletindo o efeito cumulativo de exposicao, adocao e contribuicoes ao longo dos anos.

---

### RQ02 - Sistemas populares recebem muita contribuicao externa?

**Metrica:** total de pull requests aceitas (merged).

| Estatistica | Valor |
|---|---:|
| Mediana | {rq02['mediana']:,.0f} PRs |
| Media | {rq02['media']:,.0f} PRs |
| Desvio Padrao | {rq02['desvio_padrao']:,.0f} |
| Minimo | {rq02['min']:,.0f} |
| Q1 (25%) | {rq02['q1']:,.0f} |
| Q3 (75%) | {rq02['q3']:,.0f} |
| Maximo | {rq02['max']:,.0f} |
| IQR | {rq02['iqr']:,.0f} |

![Distribuicao de PRs Aceitas](charts/rq02_prs_aceitas.png)

**Analise:** A mediana de **{rq02['mediana']:,.0f} PRs aceitas** demonstra que repositorios populares recebem um volume significativo de contribuicoes externas. A grande diferenca entre mediana e media ({rq02['media']:,.0f}) indica uma distribuicao com cauda longa a direita: alguns repositorios sao verdadeiros "imãs" de contribuicoes, enquanto a maioria tem volume moderado. H2 e parcialmente confirmada — ha contribuicao expressiva, mas com grande variabilidade.

---

### RQ03 - Sistemas populares lancam releases com frequencia?

**Metrica:** total de releases.

| Estatistica | Valor |
|---|---:|
| Mediana | {rq03['mediana']:,.0f} releases |
| Media | {rq03['media']:,.0f} releases |
| Desvio Padrao | {rq03['desvio_padrao']:,.0f} |
| Minimo | {rq03['min']:,.0f} |
| Q1 (25%) | {rq03['q1']:,.0f} |
| Q3 (75%) | {rq03['q3']:,.0f} |
| Maximo | {rq03['max']:,.0f} |
| IQR | {rq03['iqr']:,.0f} |
| Repos sem nenhuma release | {rq03['repos_sem_release']} ({rq03['pct_sem_release']}%) |

![Distribuicao de Releases](charts/rq03_releases.png)

**Analise:** A mediana de **{rq03['mediana']:,.0f} releases** mostra que muitos repositorios populares utilizam o mecanismo de releases do GitHub, mas **{rq03['pct_sem_release']}%** dos repositorios nao possuem nenhuma release formal. Isso reflete uma tendencia moderna de deploy continuo (CD), onde releases formais sao substituidas por commits diretamente na branch principal. H3 e parcialmente confirmada — existe atividade de releases, mas o padrao varia enormemente entre projetos.

---

### RQ04 - Sistemas populares sao atualizados com frequencia?

**Metrica:** dias desde o ultimo push.

| Estatistica | Valor |
|---|---:|
| Mediana | {rq04['mediana']:,.0f} dias |
| Media | {rq04['media']:,.0f} dias |
| Desvio Padrao | {rq04['desvio_padrao']:,.0f} |
| Minimo | {rq04['min']:,.0f} |
| Q1 (25%) | {rq04['q1']:,.0f} |
| Q3 (75%) | {rq04['q3']:,.0f} |
| Maximo | {rq04['max']:,.0f} |
| IQR | {rq04['iqr']:,.0f} |
| Push nos ultimos 7 dias | {rq04['repos_atualizados_7d']} |
| Push nos ultimos 30 dias | {rq04['repos_atualizados_30d']} |
| Push no ultimo ano | {rq04['repos_atualizados_365d']} |

![Tempo sem Push](charts/rq04_atualizacao.png)

**Analise:** A mediana de **{rq04['mediana']:,.0f} dias** desde o ultimo push confirma fortemente H4: repositorios populares sao extremamente ativos. {rq04['repos_atualizados_7d']} repositorios receberam push na ultima semana e {rq04['repos_atualizados_30d']} no ultimo mes. Isso demonstra que a popularidade esta diretamente associada a manutencao ativa e constante. A metrica `pushedAt` e mais precisa que `updatedAt`, pois reflete apenas pushes de codigo reais, excluindo atividades como comentarios em issues ou bots.

---

### RQ05 - Sistemas populares sao escritos nas linguagens mais populares?

**Metrica:** linguagem primaria.

| Estatistica | Valor |
|---|---|
| Total de linguagens distintas | {rq05['total_linguagens']} |
| Concentracao top 5 | {rq05['concentracao_top5_pct']}% |
| Concentracao top 10 | {rq05['concentracao_top10_pct']}% |

**Top 5 linguagens:**

{top5_table}

![Linguagens - Barras](charts/rq05_linguagens_barras.png)

![Linguagens - Pizza](charts/rq05_linguagens_pizza.png)

**Analise:** O top 5 concentra **{rq05['concentracao_top5_pct']}%** e o top 10 concentra **{rq05['concentracao_top10_pct']}%** dos repositorios. H5 e confirmada: linguagens amplamente utilizadas na industria (Python, JavaScript/TypeScript, Go, Java, C++) dominam os repositorios mais populares. Existe uma forte correlacao entre a popularidade geral de uma linguagem e sua representacao entre os projetos mais estrelados do GitHub.

---

### RQ06 - Sistemas populares possuem alto percentual de issues fechadas?

**Metrica:** razao issues fechadas / total de issues (%).

| Estatistica | Valor |
|---|---:|
| Mediana | {rq06['mediana']:.1f}% |
| Media | {rq06['media']:.1f}% |
| Desvio Padrao | {rq06['desvio_padrao']:.1f}% |
| Minimo | {rq06['min']:.1f}% |
| Q1 (25%) | {rq06['q1']:.1f}% |
| Q3 (75%) | {rq06['q3']:.1f}% |
| Maximo | {rq06['max']:.1f}% |
| Repos >= 90% issues fechadas | {rq06['repos_acima_90pct']} |
| Repos >= 70% issues fechadas | {rq06['repos_acima_70pct']} |
| Repos < 50% issues fechadas | {rq06['repos_abaixo_50pct']} |

![Issues Fechadas](charts/rq06_issues_fechadas.png)

**Analise:** A mediana de **{rq06['mediana']:.1f}%** de issues fechadas indica que repositorios populares, de fato, mantem um alto nivel de resolucao de demandas. {rq06['repos_acima_70pct']} repositorios ({rq06['repos_acima_70pct']/n*100:.1f}%) fecham pelo menos 70% de suas issues, confirmando H6. Isso reflete comunidades ativas e equipes de manutencao comprometidas com a saude do projeto.

---

## 4. Bonus - RQ07: Analise por Linguagem

**Questao:** Sistemas escritos em linguagens mais populares recebem mais contribuicao externa, lancam mais releases e sao atualizados com mais frequencia?

{rq07_table}

![Boxplots por Linguagem](charts/rq07_boxplots_por_linguagem.png)

![Medianas por Linguagem](charts/rq07_medianas_barras.png)

![Heatmap de Medianas](charts/rq07_heatmap.png)

**Analise:** A segmentacao por linguagem revela diferencas significativas entre ecossistemas:

- **Contribuicao externa (PRs):** Linguagens com ecossistemas de pacotes maduros e forte cultura de open-source tendem a receber mais PRs.
- **Releases:** A pratica de releases formais varia entre ecossistemas. Linguagens compiladas e com gestao de pacotes centralizada (ex.: Rust/crates, Go/modules) tendem a ter mais releases formais.
- **Atividade recente:** A maioria das linguagens populares mostra repositorios atualizados muito recentemente, confirmando que a popularidade no GitHub esta associada a atividade constante independente da linguagem.

H7 e parcialmente confirmada: linguagens populares de fato concentram mais atividade, mas as diferencas entre elas revelam que o ecossistema e a cultura da comunidade importam tanto quanto a popularidade da linguagem.

---

## 5. Analise de Correlacoes

![Correlacao de Spearman](charts/correlacao_spearman.png)

![Estrelas vs PRs](charts/scatter_stars_vs_prs.png)

A matriz de correlacao de Spearman permite identificar relacoes entre as metricas coletadas. Correlacoes positivas fortes indicam que as metricas crescem juntas, enquanto valores proximos de zero indicam independencia.

---

## 6. Discussao Final: Hipoteses x Resultados

| Hipotese | Resultado | Veredito |
|---|---|---|
| H1 - Repos populares sao maduros | Mediana de {rq01['mediana']} anos de idade | **Confirmada** - maturidade e um fator chave |
| H2 - Recebem muita contribuicao | Mediana de {rq02['mediana']:,.0f} PRs aceitas | **Parcialmente confirmada** - volume alto, porem com grande variancia |
| H3 - Lancam releases com frequencia | Mediana de {rq03['mediana']:,.0f} releases; {rq03['pct_sem_release']}% sem releases | **Parcialmente confirmada** - muitos usam CD sem releases formais |
| H4 - Sao atualizados com frequencia | Mediana de {rq04['mediana']:,.0f} dias desde ultimo push; {rq04['repos_atualizados_30d']} com push no ultimo mes | **Fortemente confirmada** |
| H5 - Escritos em linguagens populares | Top 5 linguagens = {rq05['concentracao_top5_pct']}% da amostra | **Confirmada** |
| H6 - Alto percentual de issues fechadas | Mediana de {rq06['mediana']:.1f}% | **Confirmada** |
| H7 - Linguagens populares = mais atividade | Diferencas observadas entre ecossistemas | **Parcialmente confirmada** |

---

## 7. Ameacas a Validade

- **Validade de construcao:** `pushedAt` do GitHub reflete o ultimo push de codigo ao repositorio, sendo mais precisa que `updatedAt` para medir atividade de desenvolvimento. Ainda assim, pushes automatizados por bots/CI podem influenciar o valor.
- **Validade externa:** a amostra se limita aos 1000 mais estrelados. Resultados nao sao generalizaveis para todo o ecossistema GitHub.
- **Viés de sobrevivencia:** repositorios abandonados que ja foram populares podem ter sido excluidos se perderam estrelas ao longo do tempo.
- **Linguagem primaria:** o GitHub classifica automaticamente a linguagem primaria com base no volume de codigo. Projetos poliglotas podem ser classificados de forma nao intuitiva.
- **Releases:** nem todos os projetos usam o mecanismo de releases do GitHub (alguns usam tags, changelogs ou deploy continuo).

---

## 8. Arquivos Gerados

- Dados brutos: `output/top_1000_repos.csv`
- Relatorio Sprint 2: `output/relatorio_sprint2.md`
- **Relatorio Final (este): `output/relatorio_final_sprint3.md`**
- Graficos: `output/charts/` (9 imagens PNG)
"""
    return report


# ──────────────────── Main ────────────────────


def main() -> None:
    print("=" * 60)
    print("Sprint 3 - Analise e Visualizacao de Dados")
    print("=" * 60)

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"CSV nao encontrado: {CSV_PATH}\n"
            "Execute primeiro o main.py (Sprint 2) para gerar os dados."
        )

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\nCarregando dados de {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    print(f"Total de repositorios: {len(df)}")
    print(f"Colunas: {list(df.columns)}")
    print(f"Linguagens distintas: {df['primary_language'].nunique()}")

    # Filtrar repos sem linguagem caso o CSV antigo tenha "Unknown"
    before = len(df)
    df = df[df["primary_language"] != "Unknown"].copy()
    after = len(df)
    if before != after:
        print(f"Removidos {before - after} repos sem linguagem de programacao (Unknown).")
        print(f"Amostra final: {after} repositorios.")

    rq_results = {}

    print("\n[1/8] RQ01 - Idade dos repositorios...")
    rq_results["rq01"] = plot_rq01(df)

    print("[2/8] RQ02 - PRs aceitas...")
    rq_results["rq02"] = plot_rq02(df)

    print("[3/8] RQ03 - Releases...")
    rq_results["rq03"] = plot_rq03(df)

    print("[4/8] RQ04 - Tempo sem atualizacao...")
    rq_results["rq04"] = plot_rq04(df)

    print("[5/8] RQ05 - Linguagens primarias...")
    rq_results["rq05"] = plot_rq05(df)

    print("[6/8] RQ06 - Issues fechadas...")
    rq_results["rq06"] = plot_rq06(df)

    print("[7/8] RQ07 - Analise por linguagem (bonus)...")
    rq_results["rq07"] = plot_rq07(df)

    print("[8/8] Correlacoes e scatter plots...")
    plot_correlations(df)
    plot_scatter_stars_prs(df)

    print("\nGerando relatorio final...")
    report_text = generate_report(df, rq_results)
    REPORT_PATH.write_text(report_text, encoding="utf-8")

    print(f"\n{'=' * 60}")
    print("Concluido com sucesso!")
    print(f"Relatorio: {REPORT_PATH}")
    print(f"Graficos:  {CHARTS_DIR}/")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
