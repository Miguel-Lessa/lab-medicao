"""Exporta figuras PNG do relatorio final (mesma logica e estilo do dashboard)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from plot_style import (  # noqa: E402
    style_bar_horizontal,
    style_box,
    style_heatmap,
    style_line_multi,
    style_pareto,
    style_pie,
    style_simple,
)

DATA_FILE = ROOT_DIR / "output" / "despesas_ceap_tratadas.csv"
FIG_DIR = ROOT_DIR / "relatorios" / "figuras"
LEADERSHIP_PATTERN = r"LID|LIDER"
EXPORT_WIDTH = 1600
EXPORT_HEIGHT = 920
EXPORT_SCALE = 2


def load_data() -> pd.DataFrame:
    data = pd.read_csv(
        DATA_FILE,
        parse_dates=["data_emissao", "data_referencia"],
        low_memory=False,
    )
    data["valor_liquido"] = pd.to_numeric(data["valor_liquido"], errors="coerce").fillna(0)
    data["eh_lideranca"] = data["deputado"].str.contains(
        LEADERSHIP_PATTERN, case=False, na=False
    )
    return data


def bar_sum_horizontal(frame, group, title, x_label, top_n=15):
    grouped = (
        frame.groupby(group, as_index=False)["valor_liquido"]
        .sum()
        .sort_values("valor_liquido", ascending=False)
        .head(top_n)
    )
    fig = px.bar(
        grouped,
        x="valor_liquido",
        y=group,
        orientation="h",
        title=title,
        labels={"valor_liquido": x_label, group: ""},
        text_auto=".2s",
    ).update_layout(yaxis={"categoryorder": "total ascending"})
    return style_bar_horizontal(fig)


def bar_median_per_entity(frame, group, title, top_n=15):
    per_deputy = frame.groupby([group, "deputado"], as_index=False)["valor_liquido"].sum()
    grouped = (
        per_deputy.groupby(group, as_index=False)["valor_liquido"]
        .median()
        .sort_values("valor_liquido", ascending=False)
        .head(top_n)
    )
    fig = px.bar(
        grouped,
        x="valor_liquido",
        y=group,
        orientation="h",
        title=title,
        labels={"valor_liquido": "Mediana por deputado (R$)", group: ""},
        text_auto=".2s",
    ).update_layout(yaxis={"categoryorder": "total ascending"})
    return style_bar_horizontal(fig)


def pie_with_others(expense: pd.DataFrame, top_n: int = 7) -> go.Figure:
    top = expense.head(top_n)
    others_value = expense.iloc[top_n:]["valor_liquido"].sum()
    pie_data = top.copy()
    if others_value > 0:
        pie_data = pd.concat(
            [
                pie_data,
                pd.DataFrame([{"tipo_despesa": "Outros", "valor_liquido": others_value}]),
            ],
            ignore_index=True,
        )
    fig = px.pie(
        pie_data,
        names="tipo_despesa",
        values="valor_liquido",
        title=f"Participacao no total (top {top_n} + Outros)",
        hole=0.45,
    )
    return style_pie(fig)


def pareto_figure(expense: pd.DataFrame, top_n: int = 12) -> go.Figure:
    total = expense["valor_liquido"].sum()
    top = expense.head(top_n).copy()
    top["acumulado_pct"] = top["valor_liquido"].cumsum() / total * 100
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=top["tipo_despesa"], y=top["valor_liquido"], name="Valor liquido"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=top["tipo_despesa"],
            y=top["acumulado_pct"],
            name="% acumulado",
            mode="lines+markers",
        ),
        secondary_y=True,
    )
    fig.update_layout(title="Diagrama de Pareto — tipos de despesa")
    fig.update_yaxes(title_text="Valor liquido (R$)", secondary_y=False)
    fig.update_yaxes(title_text="% acumulado do total", secondary_y=True, range=[0, 105])
    return style_pareto(fig)


def save(fig: go.Figure, name: str) -> None:
    path = FIG_DIR / f"{name}.png"
    fig.write_image(path, width=EXPORT_WIDTH, height=EXPORT_HEIGHT, scale=EXPORT_SCALE)
    print(f"[ok] {path}")


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    data = load_data()

    yearly = (
        data.groupby("ano", as_index=False)
        .agg(
            valor_total=("valor_liquido", "sum"),
            registros=("valor_liquido", "count"),
            deputados=("deputado", "nunique"),
        )
        .sort_values("ano")
    )

    save(
        style_simple(px.bar(
            yearly,
            x="ano",
            y="valor_total",
            text_auto=".2s",
            title="Valor liquido total por ano",
            labels={"ano": "Ano", "valor_total": "Valor liquido (R$)"},
        )),
        "01_caract_valor_ano",
    )
    save(
        style_simple(px.bar(
            yearly,
            x="ano",
            y="registros",
            text_auto=",",
            title="Quantidade de lancamentos por ano",
            labels={"ano": "Ano", "registros": "Registros"},
        )),
        "02_caract_registros_ano",
    )
    save(
        style_simple(px.line(
            yearly,
            x="ano",
            y="deputados",
            markers=True,
            title="Deputados distintos por ano",
            labels={"ano": "Ano", "deputados": "Deputados"},
        )),
        "03_caract_deputados_ano",
    )

    monthly = (
        data.dropna(subset=["data_referencia"])
        .groupby("ano_mes", as_index=False)["valor_liquido"]
        .sum()
        .sort_values("ano_mes")
    )
    save(
        style_simple(px.line(
            monthly,
            x="ano_mes",
            y="valor_liquido",
            markers=True,
            title="Evolucao mensal do valor liquidado",
            labels={"ano_mes": "Mes (competencia)", "valor_liquido": "Valor liquido (R$)"},
        )),
        "04_caract_evolucao_mensal",
    )

    positive = data.loc[data["valor_liquido"] > 0, "valor_liquido"]
    cap = positive.quantile(0.99)
    save(
        style_simple(px.histogram(
            positive.clip(upper=cap),
            nbins=60,
            title="Distribuicao dos valores por lancamento (ate P99)",
            labels={"value": "Valor liquido (R$)", "count": "Frequencia"},
        )),
        "05_caract_histograma",
    )
    save(
        bar_sum_horizontal(
            data,
            "tipo_despesa",
            "Valor total por tipo de despesa (top 15)",
            "Valor liquido (R$)",
        ),
        "06_caract_tipos_despesa",
    )

    expense = (
        data.groupby("tipo_despesa", as_index=False)["valor_liquido"]
        .sum()
        .sort_values("valor_liquido", ascending=False)
    )
    save(pareto_figure(expense), "07_rq1_pareto")
    save(pie_with_others(expense), "08_rq1_pizza")
    save(
        bar_sum_horizontal(
            expense,
            "tipo_despesa",
            "Ranking dos tipos de despesa (top 12)",
            "Valor liquido (R$)",
            top_n=12,
        ),
        "09_rq1_ranking",
    )

    top_types = expense.head(5)["tipo_despesa"].tolist()
    trend = (
        data[data["tipo_despesa"].isin(top_types)]
        .groupby(["ano_mes", "tipo_despesa"], as_index=False)["valor_liquido"]
        .sum()
        .sort_values("ano_mes")
    )
    save(
        style_line_multi(px.line(
            trend,
            x="ano_mes",
            y="valor_liquido",
            color="tipo_despesa",
            markers=True,
            title="Evolucao mensal — top 5 tipos",
            labels={
                "ano_mes": "Mes (competencia)",
                "valor_liquido": "Valor liquido (R$)",
                "tipo_despesa": "Tipo de despesa",
            },
        ), n_series=5),
        "10_rq1_evolucao_top5",
    )

    save(
        bar_sum_horizontal(data, "partido", "Soma total por partido (top 20)", "Soma (R$)", 20),
        "11_rq2_partido_soma",
    )
    save(
        bar_median_per_entity(
            data, "partido", "Mediana do gasto por deputado — partido (top 20)", 20
        ),
        "12_rq2_partido_mediana",
    )
    save(bar_sum_horizontal(data, "uf", "Soma total por UF", "Soma (R$)", 27), "13_rq2_uf_soma")
    save(
        bar_median_per_entity(data, "uf", "Mediana do gasto por deputado — UF", 27),
        "14_rq2_uf_mediana",
    )

    per_deputy = data.groupby(["partido", "deputado"], as_index=False)["valor_liquido"].sum()
    top_parties = (
        per_deputy.groupby("partido")["valor_liquido"]
        .median()
        .sort_values(ascending=False)
        .head(10)
        .index
    )
    save(
        style_box(px.box(
            per_deputy[per_deputy["partido"].isin(top_parties)],
            x="partido",
            y="valor_liquido",
            title="Dispersao do gasto por deputado — top 10 partidos",
            labels={"partido": "Partido", "valor_liquido": "Gasto total do deputado (R$)"},
        )),
        "15_rq2_boxplot_partido",
    )

    pivot = pd.pivot_table(
        data,
        values="valor_liquido",
        index="partido",
        columns="tipo_despesa",
        aggfunc="sum",
        fill_value=0,
    )
    top_columns = pivot.sum().sort_values(ascending=False).head(8).index
    pivot = pivot[top_columns].head(15)
    pivot_pct = pivot.div(pivot.sum(axis=1).replace(0, pd.NA), axis=0) * 100
    save(
        style_heatmap(px.imshow(
            pivot_pct,
            aspect="auto",
            title="Composicao percentual por partido",
            labels={"x": "Tipo de despesa", "y": "Partido", "color": "% do partido"},
            color_continuous_scale="Blues",
        )),
        "16_rq2_heatmap_pct",
    )

    deputy_data = data[~data["eh_lideranca"]]
    save(
        bar_sum_horizontal(
            deputy_data,
            "deputado",
            "Top deputados por valor liquidado (top 15)",
            "Soma (R$)",
        ),
        "17_rq3_deputados",
    )
    save(
        bar_sum_horizontal(
            data,
            "fornecedor",
            "Top fornecedores por valor liquidado (top 15)",
            "Soma (R$)",
        ),
        "18_rq3_fornecedores",
    )


if __name__ == "__main__":
    main()
