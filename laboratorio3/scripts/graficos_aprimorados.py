"""
Graficos aprimorados para o relatorio Lab 03 - Sprint 03.
Gera visualizacoes profissionais em output/lab3s3/charts_v2/.
"""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

# ── Paths ──────────────────────────────────────────────────────────────
DIR_PROJETO = Path(__file__).resolve().parent.parent
CSV_PRS = DIR_PROJETO / "output" / "lab3s2" / "pull_requests_com_reviews.csv"
CSV_COMP = DIR_PROJETO / "output" / "lab3s3" / "comparacao_status_mannwhitney.csv"
CSV_CORR = DIR_PROJETO / "output" / "lab3s3" / "correlacoes_spearman.csv"
CSV_DESC = DIR_PROJETO / "output" / "lab3s3" / "descritivas_globais.csv"
DIR_OUT  = DIR_PROJETO / "output" / "lab3s3" / "charts_v2"

# ── Visual style ───────────────────────────────────────────────────────
PAL = {"MERGED": "#2ecc71", "CLOSED": "#e74c3c"}
BG   = "#fafafa"
GRID = "#e0e0e0"
TXT  = "#2c3e50"
DPI  = 300

NOMES = {
    "changed_files": "Arquivos alterados",
    "additions": "Linhas adicionadas",
    "deletions": "Linhas removidas",
    "loc_total": "LOC total (add+del)",
    "tempo_analise_horas": "Tempo de análise (h)",
    "descricao_tamanho_chars": "Descrição (caracteres)",
    "num_participantes": "Participantes",
    "total_comentarios": "Comentários",
    "numero_reviews": "Revisões",
}

def setup_style():
    plt.rcParams.update({
        "figure.facecolor": BG, "axes.facecolor": "white",
        "axes.edgecolor": GRID, "axes.grid": True,
        "grid.color": GRID, "grid.alpha": .4, "grid.linewidth": .6,
        "font.family": "sans-serif", "font.size": 11,
        "axes.titlesize": 14, "axes.titleweight": "bold",
        "axes.labelsize": 12, "xtick.labelsize": 10, "ytick.labelsize": 10,
        "text.color": TXT, "axes.labelcolor": TXT,
        "legend.framealpha": .9, "legend.edgecolor": GRID,
    })

def load():
    df = pd.read_csv(CSV_PRS)
    df["status"] = df["status"].str.upper()
    df = df[df["status"].isin(["MERGED", "CLOSED"])].copy()
    if "tempo_analise_horas" not in df.columns and "tempo_analise_dias" in df.columns:
        df["tempo_analise_horas"] = pd.to_numeric(df["tempo_analise_dias"], errors="coerce") * 24.0
    if "loc_total" not in df.columns:
        df["loc_total"] = pd.to_numeric(df.get("additions",0), errors="coerce").fillna(0) + pd.to_numeric(df.get("deletions",0), errors="coerce").fillna(0)
    return df

def savefig(fig, name):
    fig.savefig(DIR_OUT / name, dpi=DPI, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  OK {name}")

# ── 1-3. Violin split MERGED vs CLOSED ────────────────────────────────
def violin_split(df, col, fname):
    s = pd.to_numeric(df[col], errors="coerce")
    tmp = df[["status"]].copy()
    tmp["val"] = np.log1p(s.clip(lower=0))
    tmp = tmp.dropna(subset=["val"])
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.violinplot(data=tmp, x="status", y="val", hue="status",
                   palette=PAL, inner="quart", density_norm="width",
                   order=["MERGED","CLOSED"], ax=ax, linewidth=.8, legend=False)
    nm = (df["status"]=="MERGED").sum()
    nc = (df["status"]=="CLOSED").sum()
    ax.set_xticklabels([f"MERGED\n(n={nm:,})", f"CLOSED\n(n={nc:,})"])
    ax.set_ylabel(f"log(1 + {NOMES.get(col, col)})")
    ax.set_xlabel("")
    ax.set_title(f"{NOMES.get(col, col)} — MERGED vs CLOSED")
    savefig(fig, fname)

# ── 4-5. ECDF overlay ─────────────────────────────────────────────────
def ecdf_overlay(df, col, fname):
    fig, ax = plt.subplots(figsize=(8, 5))
    for st, color in PAL.items():
        s = pd.to_numeric(df[df["status"]==st][col], errors="coerce").dropna()
        xs = np.sort(s.values)
        ys = np.arange(1, len(xs)+1) / len(xs)
        ax.step(xs, ys, color=color, linewidth=2, label=f"{st} (n={len(xs):,})")
        med = np.median(xs)
        yi = np.searchsorted(xs, med) / len(xs)
        ax.axvline(med, color=color, ls="--", alpha=.6, lw=1.2)
        ax.annotate(f"med={med:,.1f}", (med, yi), fontsize=9,
                    color=color, ha="left", va="bottom",
                    xytext=(8, 4), textcoords="offset points")
    ax.set_xscale("log")
    ax.set_xlabel(NOMES.get(col, col))
    ax.set_ylabel("Proporção acumulada (ECDF)")
    ax.set_title(f"Distribuição acumulada — {NOMES.get(col, col)}")
    ax.legend(loc="lower right")
    savefig(fig, fname)

# ── 6. Forest plot Cliff's delta ──────────────────────────────────────
def forest_cliff(comp_df, fname):
    fig, ax = plt.subplots(figsize=(8, 5))
    comp = comp_df.copy()
    comp["label"] = comp["nome_metrica"]
    comp = comp.sort_values("cliffs_delta")
    y = np.arange(len(comp))
    colors = ["#e74c3c" if d < 0 else "#2ecc71" for d in comp["cliffs_delta"]]
    ax.barh(y, comp["cliffs_delta"], color=colors, height=.6, alpha=.85, edgecolor="white")
    ax.axvline(0, color=TXT, lw=1.2, ls="-")
    for t in [-.147, .147]:
        ax.axvline(t, color=GRID, lw=1, ls=":")
    ax.set_yticks(y)
    ax.set_yticklabels(comp["label"], fontsize=10)
    ax.set_xlabel("Delta de Cliff (positivo = MERGED > CLOSED)")
    ax.set_title("Tamanho do efeito — MERGED vs CLOSED (Cliff's δ)")
    for i, (d, p) in enumerate(zip(comp["cliffs_delta"], comp["interpretacao_efeito"])):
        ax.text(d + (.008 if d>=0 else -.008), i, f" {d:+.3f} ({p})",
                va="center", ha="left" if d>=0 else "right", fontsize=8.5)
    savefig(fig, fname)

# ── 7. Forest plot Spearman ρ ─────────────────────────────────────────
def forest_spearman(corr_df, fname):
    fig, ax = plt.subplots(figsize=(8, 5))
    corr = corr_df.copy()
    corr["label"] = corr["nome_metrica"]
    corr = corr.sort_values("spearman_rho")
    y = np.arange(len(corr))
    # parse IC
    lo, hi = [], []
    for ic in corr["ic95_rho"]:
        parts = ic.strip("[]").split(",")
        lo.append(float(parts[0].strip()))
        hi.append(float(parts[1].strip()))
    corr["lo"], corr["hi"] = lo, hi
    xerr = np.array([corr["spearman_rho"].values - corr["lo"].values,
                      corr["hi"].values - corr["spearman_rho"].values])
    colors = ["#3498db" if r >= .3 else "#7fb3d8" if r >= .18 else "#bdc3c7"
              for r in corr["spearman_rho"]]
    ax.barh(y, corr["spearman_rho"], xerr=xerr, color=colors, height=.6,
            alpha=.85, edgecolor="white", capsize=3)
    ax.axvline(0, color=TXT, lw=1)
    for t in [.1, .3]:
        ax.axvline(t, color=GRID, lw=1, ls=":")
    ax.set_yticks(y)
    ax.set_yticklabels(corr["label"], fontsize=10)
    ax.set_xlabel("Spearman ρ com número de revisões")
    ax.set_title("Correlação monótona com número de revisões (Spearman ρ)")
    for i, (r, interp) in enumerate(zip(corr["spearman_rho"], corr["interpretacao"])):
        ax.text(r + .015, i, f" {r:.3f} ({interp})", va="center", fontsize=8.5)
    savefig(fig, fname)

# ── 8. Taxa MERGED por decil de tempo ─────────────────────────────────
def taxa_merged_decil(df, col, fname):
    s = pd.to_numeric(df[col], errors="coerce")
    tmp = df[["status"]].copy()
    tmp["val"] = s
    tmp = tmp.dropna(subset=["val"])
    tmp["decil"] = pd.qcut(tmp["val"], 10, labels=False, duplicates="drop")
    agg = tmp.groupby("decil").agg(n=("status","size"), merged=("status", lambda x: (x=="MERGED").sum()))
    agg["taxa"] = agg["merged"] / agg["n"]
    taxa_global = (tmp["status"]=="MERGED").mean()
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = ["#2ecc71" if t >= taxa_global else "#e74c3c" for t in agg["taxa"]]
    bars = ax.bar(agg.index, agg["taxa"], color=colors, edgecolor="white", width=.8, alpha=.85)
    ax.axhline(taxa_global, color=TXT, ls="--", lw=1.5, label=f"Média global ({taxa_global:.1%})")
    for b, n in zip(bars, agg["n"]):
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+.01, f"n={n:,}",
                ha="center", fontsize=7.5, color=TXT)
    ax.set_xlabel(f"Decil de {NOMES.get(col, col)} (1=menor, 10=maior)")
    ax.set_ylabel("Taxa de MERGED")
    ax.set_title(f"Taxa de MERGED por decil de {NOMES.get(col, col)}")
    ax.set_ylim(0, 1.05)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.legend()
    savefig(fig, fname)

# ── 9-10. Hexbin scatter ──────────────────────────────────────────────
def hexbin_scatter(df, col_x, fname):
    pares = df[[col_x, "numero_reviews"]].apply(pd.to_numeric, errors="coerce").dropna()
    if len(pares) < 10:
        return
    x = np.log1p(pares[col_x].clip(lower=0))
    y = np.log1p(pares["numero_reviews"].clip(lower=0))
    rho, p = stats.spearmanr(pares[col_x], pares["numero_reviews"])
    fig, ax = plt.subplots(figsize=(8, 6))
    hb = ax.hexbin(x, y, gridsize=35, cmap="YlOrRd", mincnt=1, linewidths=.2, edgecolors="white")
    cb = fig.colorbar(hb, ax=ax, shrink=.8)
    cb.set_label("Contagem de PRs", fontsize=10)
    ax.set_xlabel(f"log(1 + {NOMES.get(col_x, col_x)})")
    ax.set_ylabel("log(1 + Revisões)")
    ax.set_title(f"{NOMES.get(col_x, col_x)} × Revisões\nSpearman ρ = {rho:.3f} | n = {len(pares):,}")
    savefig(fig, fname)

# ── 11. Mediana IC95 barras ───────────────────────────────────────────
def mediana_ic_barras(comp_df, fname):
    metricas = ["tempo_analise_horas", "loc_total", "total_comentarios", "descricao_tamanho_chars"]
    rows = comp_df[comp_df["metrica"].isin(metricas)].copy()
    if rows.empty:
        return
    fig, axes = plt.subplots(1, len(rows), figsize=(3.2*len(rows), 5), sharey=False)
    if len(rows) == 1:
        axes = [axes]
    for ax, (_, r) in zip(axes, rows.iterrows()):
        merged_val = float(r["mediana_merged"])
        closed_val = float(r["mediana_closed"])
        bars = ax.bar(["MERGED", "CLOSED"], [merged_val, closed_val],
                      color=[PAL["MERGED"], PAL["CLOSED"]], edgecolor="white", width=.6, alpha=.85)
        for b in bars:
            ax.text(b.get_x()+b.get_width()/2, b.get_height(),
                    f"{b.get_height():,.1f}", ha="center", va="bottom", fontsize=9)
        nome = r["nome_metrica"]
        if len(nome) > 22:
            nome = nome[:20] + "…"
        ax.set_title(nome, fontsize=10)
        ax.set_ylabel("Mediana")
        if max(merged_val, closed_val) > 100:
            ax.set_yscale("log")
    fig.suptitle("Medianas MERGED vs CLOSED — métricas selecionadas", fontweight="bold", fontsize=13)
    fig.tight_layout()
    savefig(fig, fname)

# ── 12. Bubble chart δ × ρ ────────────────────────────────────────────
def bubble_delta_rho(comp_df, corr_df, fname):
    # merge data by metrica
    merged = []
    for _, cr in corr_df.iterrows():
        met = cr["metrica"]
        cmp = comp_df[comp_df["metrica"] == met]
        if cmp.empty:
            continue
        merged.append({
            "metrica": met,
            "label": cr["nome_metrica"],
            "delta": float(cmp.iloc[0]["cliffs_delta"]),
            "rho": float(cr["spearman_rho"]),
            "n": int(cr["n"]),
        })
    if not merged:
        return
    bdf = pd.DataFrame(merged)
    fig, ax = plt.subplots(figsize=(9, 6))
    scatter = ax.scatter(bdf["delta"], bdf["rho"], s=200, alpha=.75,
                         c=bdf["rho"], cmap="RdYlGn", edgecolors=TXT, linewidth=1.2,
                         vmin=0, vmax=.4, zorder=5)
    for _, r in bdf.iterrows():
        ax.annotate(r["label"], (r["delta"], r["rho"]),
                    fontsize=8.5, ha="center", va="bottom",
                    xytext=(0, 10), textcoords="offset points")
    ax.axhline(0, color=GRID, lw=1)
    ax.axvline(0, color=GRID, lw=1)
    ax.axhspan(.3, .5, alpha=.06, color="#2ecc71")
    ax.axvspan(-.5, -.147, alpha=.06, color="#e74c3c")
    ax.set_xlabel("Cliff's δ (Dimensão A: MERGED vs CLOSED)")
    ax.set_ylabel("Spearman ρ (Dimensão B: nº revisões)")
    ax.set_title("Cruzamento: efeito no desfecho (δ) vs efeito no esforço (ρ)")
    cb = fig.colorbar(scatter, ax=ax, shrink=.7)
    cb.set_label("Spearman ρ")
    savefig(fig, fname)

# ── 13. Dashboard 2x2 ────────────────────────────────────────────────
def dashboard_resumo(df, comp_df, corr_df, fname):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Resumo dos Achados — Lab 03: Code Review no GitHub",
                 fontsize=16, fontweight="bold", y=.97)

    # (0,0) Dataset overview
    ax = axes[0, 0]
    nm = (df["status"]=="MERGED").sum()
    nc = (df["status"]=="CLOSED").sum()
    wedges, texts, autotexts = ax.pie(
        [nm, nc], labels=[f"MERGED\n{nm:,}", f"CLOSED\n{nc:,}"],
        colors=[PAL["MERGED"], PAL["CLOSED"]], autopct="%.1f%%",
        startangle=90, textprops={"fontsize": 11})
    for at in autotexts:
        at.set_fontweight("bold")
    ax.set_title(f"Dataset: {len(df):,} PRs, {df['repo_completo'].nunique()} repos", fontsize=11)

    # (0,1) Tempo mediana
    ax = axes[0, 1]
    r = comp_df[comp_df["metrica"]=="tempo_analise_horas"]
    if not r.empty:
        r = r.iloc[0]
        bars = ax.bar(["MERGED", "CLOSED"],
                      [float(r["mediana_merged"]), float(r["mediana_closed"])],
                      color=[PAL["MERGED"], PAL["CLOSED"]], edgecolor="white", width=.55)
        for b in bars:
            ax.text(b.get_x()+b.get_width()/2, b.get_height(),
                    f"{b.get_height():,.0f}h", ha="center", va="bottom", fontsize=11, fontweight="bold")
        ax.set_ylabel("Mediana (horas)")
        ax.set_title("RQ02: Tempo de análise (achado mais forte)", fontsize=11)

    # (1,0) Forest cliff mini
    ax = axes[1, 0]
    comp = comp_df.sort_values("cliffs_delta")
    y = np.arange(len(comp))
    colors = ["#e74c3c" if d < 0 else "#2ecc71" for d in comp["cliffs_delta"]]
    ax.barh(y, comp["cliffs_delta"], color=colors, height=.55, alpha=.85)
    ax.axvline(0, color=TXT, lw=1)
    ax.set_yticks(y)
    ax.set_yticklabels(comp["nome_metrica"], fontsize=8.5)
    ax.set_xlabel("Cliff's δ")
    ax.set_title("Dimensão A: tamanho do efeito", fontsize=11)

    # (1,1) Forest spearman mini
    ax = axes[1, 1]
    corr = corr_df.sort_values("spearman_rho")
    y = np.arange(len(corr))
    colors = ["#3498db" if r >= .3 else "#7fb3d8" if r >= .18 else "#bdc3c7"
              for r in corr["spearman_rho"]]
    ax.barh(y, corr["spearman_rho"], color=colors, height=.55, alpha=.85)
    ax.set_yticks(y)
    ax.set_yticklabels(corr["nome_metrica"], fontsize=8.5)
    ax.set_xlabel("Spearman ρ")
    ax.set_title("Dimensão B: correlação com revisões", fontsize=11)

    fig.tight_layout(rect=[0, 0, 1, .95])
    savefig(fig, fname)

# ── 14. Ridgeline reviews por quartil LOC ─────────────────────────────
def ridgeline_reviews(df, fname):
    s_loc = pd.to_numeric(df["loc_total"], errors="coerce")
    s_rev = pd.to_numeric(df["numero_reviews"], errors="coerce")
    tmp = df[["status"]].copy()
    tmp["loc"] = s_loc
    tmp["rev"] = s_rev
    tmp = tmp.dropna()
    tmp["quartil"] = pd.qcut(tmp["loc"], 4, labels=["Q1\n(menor)", "Q2", "Q3", "Q4\n(maior)"])
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.boxenplot(data=tmp, x="quartil", y="rev", palette="Blues_d", ax=ax,
                  linewidth=.6)
    ax.set_yscale("log")
    ax.set_xlabel("Quartil de LOC total")
    ax.set_ylabel("Número de revisões (log)")
    ax.set_title("Distribuição de revisões por quartil de tamanho (LOC)")
    for i, q in enumerate(["Q1\n(menor)", "Q2", "Q3", "Q4\n(maior)"]):
        subset = tmp[tmp["quartil"]==q]
        med = subset["rev"].median()
        ax.text(i, med, f" med={med:.0f}", va="bottom", ha="center", fontsize=9,
                fontweight="bold", color=TXT)
    savefig(fig, fname)

# ── 15. Heatmap completo melhorado ────────────────────────────────────
def heatmap_completo(df, fname):
    cols = ["changed_files","additions","deletions","loc_total",
            "tempo_analise_horas","descricao_tamanho_chars",
            "num_participantes","total_comentarios","numero_reviews"]
    cols = [c for c in cols if c in df.columns]
    num = df[cols].apply(pd.to_numeric, errors="coerce")
    corr = num.corr(method="spearman")
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    labels = [NOMES.get(c, c) for c in cols]
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r",
                center=0, vmin=-1, vmax=1, square=True,
                xticklabels=labels, yticklabels=labels,
                linewidths=.8, linecolor="white", ax=ax,
                cbar_kws={"shrink": .8, "label": "Spearman ρ"})
    ax.set_title("Matriz de correlação de Spearman\n(triângulo inferior)", fontsize=13)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.yticks(fontsize=9)
    savefig(fig, fname)

# ── 16. Violin split por status para todas métricas (painel 2x4) ─────
def painel_violin_status(df, fname):
    metricas = ["changed_files","additions","loc_total","tempo_analise_horas",
                "descricao_tamanho_chars","num_participantes","total_comentarios","numero_reviews"]
    metricas = [m for m in metricas if m in df.columns]
    n = len(metricas)
    cols_grid = 4
    rows_grid = (n + cols_grid - 1) // cols_grid
    fig, axes = plt.subplots(rows_grid, cols_grid, figsize=(18, 4.5*rows_grid))
    axes = axes.flatten()
    for i, col in enumerate(metricas):
        ax = axes[i]
        s = pd.to_numeric(df[col], errors="coerce")
        tmp = df[["status"]].copy()
        tmp["val"] = np.log1p(s.clip(lower=0))
        tmp = tmp.dropna(subset=["val"])
        sns.violinplot(data=tmp, x="status", y="val", hue="status",
                       palette=PAL, inner="quart", density_norm="width",
                       order=["MERGED","CLOSED"], ax=ax, linewidth=.6, legend=False)
        ax.set_title(NOMES.get(col, col), fontsize=10, fontweight="bold")
        ax.set_xlabel("")
        ax.set_ylabel("log(1+valor)")
    for j in range(i+1, len(axes)):
        axes[j].set_visible(False)
    fig.suptitle("Distribuições por status — todas as métricas (escala log)", fontsize=15, fontweight="bold", y=1.01)
    fig.tight_layout()
    savefig(fig, fname)


def main():
    DIR_OUT.mkdir(parents=True, exist_ok=True)
    setup_style()

    print("Carregando dados...")
    df = load()
    comp_df = pd.read_csv(CSV_COMP)
    corr_df = pd.read_csv(CSV_CORR)
    print(f"  PRs: {len(df):,} | MERGED: {(df['status']=='MERGED').sum():,} | CLOSED: {(df['status']=='CLOSED').sum():,}")

    print("\nGerando graficos aprimorados...")

    # 1-3 Violin split
    violin_split(df, "tempo_analise_horas", "01_violin_tempo_status.png")
    violin_split(df, "loc_total", "02_violin_loc_status.png")
    violin_split(df, "total_comentarios", "03_violin_comentarios_status.png")

    # 4-5 ECDF
    ecdf_overlay(df, "tempo_analise_horas", "04_ecdf_tempo_status.png")
    ecdf_overlay(df, "loc_total", "05_ecdf_loc_status.png")

    # 6-7 Forest plots
    forest_cliff(comp_df, "06_forest_cliff_delta.png")
    forest_spearman(corr_df, "07_forest_spearman_rho.png")

    # 8 Taxa merged por decil
    taxa_merged_decil(df, "tempo_analise_horas", "08_taxa_merged_decil_tempo.png")

    # 9-10 Hexbin
    hexbin_scatter(df, "loc_total", "09_hexbin_loc_reviews.png")
    hexbin_scatter(df, "total_comentarios", "10_hexbin_comentarios_reviews.png")

    # 11 Mediana IC barras
    mediana_ic_barras(comp_df, "11_mediana_ic_barras.png")

    # 12 Bubble
    bubble_delta_rho(comp_df, corr_df, "12_bubble_delta_rho.png")

    # 13 Dashboard
    dashboard_resumo(df, comp_df, corr_df, "13_dashboard_resumo.png")

    # 14 Ridgeline
    ridgeline_reviews(df, "14_ridgeline_reviews_loc.png")

    # 15 Heatmap
    heatmap_completo(df, "15_heatmap_completo.png")

    # 16 Painel violin
    painel_violin_status(df, "16_painel_violin_status.png")

    print(f"\nTodos os graficos em: {DIR_OUT}")
    print("Concluido!")


if __name__ == "__main__":
    main()
