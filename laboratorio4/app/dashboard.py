"""Dashboard interativo da Sprint 03 do Laboratorio 04."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT_DIR / "output" / "despesas_ceap_tratadas.csv"
LEADERSHIP_PATTERN = r"LID|LIDER"

import sys

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


st.set_page_config(
    page_title="Lab04S03 - Despesas Parlamentares CEAP",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    if not DATA_FILE.exists():
        st.error(
            "Base tratada nao encontrada. Rode primeiro: "
            "`python laboratorio4/scripts/coleta_ceap.py` e "
            "`python laboratorio4/scripts/prepara_dados.py`."
        )
        st.stop()

    data = pd.read_csv(
        DATA_FILE,
        parse_dates=["data_emissao", "data_referencia"],
        low_memory=False,
    )
    data["ano"] = data["ano"].astype("Int64")
    data["mes"] = data["mes"].astype("Int64")
    data["valor_liquido"] = pd.to_numeric(data["valor_liquido"], errors="coerce").fillna(0)
    data["eh_lideranca"] = data["deputado"].str.contains(
        LEADERSHIP_PATTERN, case=False, na=False
    )
    return data


def format_currency(value: float) -> str:
    formatted = f"R$ {value:,.2f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def multiselect_filter(label: str, values: pd.Series, help_text: str | None = None) -> list[str]:
    options = sorted(value for value in values.dropna().unique() if str(value).strip())
    return st.sidebar.multiselect(label, options=options, default=[], help=help_text)


def apply_filters(data: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filtros")
    st.sidebar.caption("Nos filtros de texto, deixe vazio para manter todos os valores.")

    years = sorted(data["ano"].dropna().astype(int).unique())
    selected_years = st.sidebar.multiselect("Ano", years, default=years)

    months = sorted(data["mes"].dropna().astype(int).unique())
    selected_months = st.sidebar.multiselect("Mes", months, default=months)

    selected_parties = multiselect_filter("Partido", data["partido"])
    selected_ufs = multiselect_filter("UF", data["uf"])
    selected_expense_types = multiselect_filter("Tipo de despesa", data["tipo_despesa"])
    selected_deputies = multiselect_filter(
        "Deputado",
        data["deputado"],
        help_text="Use a busca do campo para localizar um parlamentar especifico.",
    )

    exclude_zeros = st.sidebar.checkbox(
        "Excluir lancamentos com valor zero",
        value=False,
        help="Remove registros com valor liquido igual a zero das visualizacoes.",
    )
    exclude_leadership = st.sidebar.checkbox(
        "Excluir estruturas de lideranca (LID/LIDER)",
        value=False,
        help="Remove registros de liderancas partidarias e da Mesa.",
    )

    filtered = data[
        data["ano"].astype("Int64").isin(selected_years)
        & data["mes"].astype("Int64").isin(selected_months)
    ].copy()

    if selected_parties:
        filtered = filtered[filtered["partido"].isin(selected_parties)]
    if selected_ufs:
        filtered = filtered[filtered["uf"].isin(selected_ufs)]
    if selected_expense_types:
        filtered = filtered[filtered["tipo_despesa"].isin(selected_expense_types)]
    if selected_deputies:
        filtered = filtered[filtered["deputado"].isin(selected_deputies)]
    if exclude_zeros:
        filtered = filtered[filtered["valor_liquido"] > 0]
    if exclude_leadership:
        filtered = filtered[~filtered["eh_lideranca"]]

    return filtered


def show_chart(fig: go.Figure, chart_id: str, caption: str | None = None) -> None:
    """Exibe grafico Plotly com botoes de exportacao PNG e HTML."""
    if caption:
        st.caption(caption)

    st.plotly_chart(fig, use_container_width=True, key=f"plot_{chart_id}")

    col_png, col_html, _ = st.columns([1, 1, 2])
    file_stem = f"lab04_{chart_id}"

    with col_png:
        try:
            png_bytes = fig.to_image(format="png", width=1600, height=920, scale=2)
            st.download_button(
                "Exportar PNG",
                data=png_bytes,
                file_name=f"{file_stem}.png",
                mime="image/png",
                key=f"png_{chart_id}",
            )
        except Exception:
            st.download_button(
                "Exportar PNG",
                data=b"",
                file_name=f"{file_stem}.png",
                mime="image/png",
                key=f"png_{chart_id}",
                disabled=True,
                help="Instale kaleido: pip install kaleido",
            )

    with col_html:
        html_bytes = fig.to_html(full_html=True, include_plotlyjs="cdn").encode("utf-8")
        st.download_button(
            "Exportar HTML",
            data=html_bytes,
            file_name=f"{file_stem}.html",
            mime="text/html",
            key=f"html_{chart_id}",
        )


def show_kpis(data: pd.DataFrame) -> None:
    period = "Sem data"
    valid_dates = data["data_referencia"].dropna()
    if not valid_dates.empty:
        period = f"{valid_dates.min():%d/%m/%Y} a {valid_dates.max():%d/%m/%Y}"

    positive = data.loc[data["valor_liquido"] > 0, "valor_liquido"]
    mediana_lanc = positive.median() if not positive.empty else 0.0

    kpis = st.columns(6)
    kpis[0].metric("Registros", f"{len(data):,}".replace(",", "."))
    kpis[1].metric("Valor total", format_currency(data["valor_liquido"].sum()))
    kpis[2].metric("Deputados", data["deputado"].nunique())
    kpis[3].metric("Partidos", data["partido"].nunique())
    kpis[4].metric("UFs", data["uf"].nunique())
    kpis[5].metric("Fornecedores", data["fornecedor"].nunique())
    st.caption(
        f"Periodo: {period} | Mediana por lancamento (valor > 0): {format_currency(mediana_lanc)}"
    )


def bar_sum_horizontal(
    frame: pd.DataFrame,
    group: str,
    title: str,
    x_label: str,
    top_n: int = 15,
) -> go.Figure:
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


def bar_median_per_entity(
    frame: pd.DataFrame,
    group: str,
    title: str,
    top_n: int = 15,
) -> go.Figure:
    """Mediana da soma de valor liquido por deputado dentro de cada grupo."""
    per_deputy = (
        frame.groupby([group, "deputado"], as_index=False)["valor_liquido"]
        .sum()
    )
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
                pd.DataFrame(
                    [{"tipo_despesa": "Outros", "valor_liquido": others_value}]
                ),
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
        go.Bar(
            x=top["tipo_despesa"],
            y=top["valor_liquido"],
            name="Valor liquido",
            marker_color="#1f77b4",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=top["tipo_despesa"],
            y=top["acumulado_pct"],
            name="% acumulado",
            mode="lines+markers",
            marker_color="#ff7f0e",
        ),
        secondary_y=True,
    )
    fig.update_layout(title="Diagrama de Pareto — tipos de despesa")
    fig.update_yaxes(title_text="Valor liquido (R$)", secondary_y=False)
    fig.update_yaxes(title_text="% acumulado do total", secondary_y=True, range=[0, 105])
    return style_pareto(fig)


def section_dataset(data: pd.DataFrame) -> None:
    st.header("Caracterizacao do Dataset")
    st.markdown(
        "Visao geral da base CEAP no recorte filtrado. As metricas usam **soma do valor "
        "liquido** e **contagens distintas** por dimensao. A competencia temporal segue "
        "ano/mes da despesa (`data_referencia`)."
    )
    show_kpis(data)

    yearly = (
        data.groupby("ano", as_index=False)
        .agg(
            valor_total=("valor_liquido", "sum"),
            registros=("valor_liquido", "count"),
            deputados=("deputado", "nunique"),
        )
        .sort_values("ano")
    )

    col1, col2 = st.columns(2)
    with col1:
        fig = style_simple(px.bar(
            yearly,
            x="ano",
            y="valor_total",
            text_auto=".2s",
            title="Valor liquido total por ano",
            labels={"ano": "Ano", "valor_total": "Valor liquido (R$)"},
        ))
        show_chart(
            fig,
            "caract_valor_ano",
            "Soma de todos os lancamentos por ano de competencia.",
        )

    with col2:
        fig = style_simple(px.bar(
            yearly,
            x="ano",
            y="registros",
            text_auto=",",
            title="Quantidade de lancamentos por ano",
            labels={"ano": "Ano", "registros": "Registros"},
        ))
        show_chart(fig, "caract_registros_ano")

    col3, col4 = st.columns(2)
    with col3:
        fig = style_simple(px.line(
            yearly,
            x="ano",
            y="deputados",
            markers=True,
            title="Deputados distintos por ano",
            labels={"ano": "Ano", "deputados": "Deputados"},
        ))
        show_chart(
            fig,
            "caract_deputados_ano",
            "Contagem de nomes distintos; inclui trocas de mandato e estruturas parlamentares.",
        )

    with col4:
        monthly = (
            data.dropna(subset=["data_referencia"])
            .groupby("ano_mes", as_index=False)["valor_liquido"]
            .sum()
            .sort_values("ano_mes")
        )
        fig = style_simple(px.line(
            monthly,
            x="ano_mes",
            y="valor_liquido",
            markers=True,
            title="Evolucao mensal do valor liquidado",
            labels={"ano_mes": "Mes (competencia)", "valor_liquido": "Valor liquido (R$)"},
        ))
        show_chart(fig, "caract_evolucao_mensal")

    col5, col6 = st.columns(2)
    with col5:
        positive = data.loc[data["valor_liquido"] > 0, "valor_liquido"]
        cap = positive.quantile(0.99) if not positive.empty else 0
        clipped = positive.clip(upper=cap) if cap else positive
        fig = style_simple(px.histogram(
            clipped,
            nbins=60,
            title="Distribuicao dos valores por lancamento (ate P99)",
            labels={"value": "Valor liquido (R$)", "count": "Frequencia"},
        ))
        show_chart(
            fig,
            "caract_histograma",
            f"Mediana: {format_currency(positive.median())} | "
            f"P95: {format_currency(positive.quantile(0.95))} | "
            f"Eixo limitado ao percentil 99 para leitura.",
        )

    with col6:
        fig = bar_sum_horizontal(
            data,
            "tipo_despesa",
            "Valor total por tipo de despesa (top 15)",
            "Valor liquido (R$)",
            top_n=15,
        )
        show_chart(fig, "caract_tipos_despesa")


def section_rq1(data: pd.DataFrame) -> None:
    st.header("RQ1: Quais tipos de despesa concentram mais gastos parlamentares?")
    st.markdown(
        "Metrica principal: **soma do valor liquido** por tipo. O Pareto mostra concentracao; "
        "a pizza inclui fatia **Outros** para fechar 100% do total."
    )

    expense = (
        data.groupby("tipo_despesa", as_index=False)["valor_liquido"]
        .sum()
        .sort_values("valor_liquido", ascending=False)
    )

    col1, col2 = st.columns(2)
    with col1:
        show_chart(
            pareto_figure(expense),
            "rq1_pareto",
            "Barras: valor por tipo. Linha: percentual acumulado sobre o total filtrado.",
        )
    with col2:
        show_chart(
            pie_with_others(expense, top_n=7),
            "rq1_pizza",
            "Top 7 categorias + demais agrupadas em Outros.",
        )

    col3, col4 = st.columns(2)
    with col3:
        fig = bar_sum_horizontal(
            expense,
            "tipo_despesa",
            "Ranking dos tipos de despesa (top 12)",
            "Valor liquido (R$)",
            top_n=12,
        )
        show_chart(fig, "rq1_ranking")

    top_types = expense.head(5)["tipo_despesa"].tolist()
    trend = (
        data[data["tipo_despesa"].isin(top_types)]
        .groupby(["ano_mes", "tipo_despesa"], as_index=False)["valor_liquido"]
        .sum()
        .sort_values("ano_mes")
    )
    with col4:
        fig = style_line_multi(px.line(
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
        ), n_series=5)
        show_chart(fig, "rq1_evolucao_top5")


def section_rq2(data: pd.DataFrame) -> None:
    st.header("RQ2: Como os gastos variam por partido e UF?")
    st.markdown(
        "Comparacoes em duas metricas: **soma total** (reflete tamanho do grupo) e "
        "**mediana da soma por deputado** (comparacao mais justa entre grupos de "
        "tamanhos diferentes). O heatmap usa **percentual dentro de cada partido**."
    )

    col1, col2 = st.columns(2)
    with col1:
        fig = bar_sum_horizontal(
            data,
            "partido",
            "Soma total por partido (top 20)",
            "Soma valor liquido (R$)",
            top_n=20,
        )
        show_chart(
            fig,
            "rq2_partido_soma",
            "Partidos com mais deputados tendem a liderar neste grafico.",
        )
    with col2:
        fig = bar_median_per_entity(
            data,
            "partido",
            "Mediana do gasto por deputado — partido (top 20)",
            top_n=20,
        )
        show_chart(
            fig,
            "rq2_partido_mediana",
            "Para cada partido: soma por deputado, depois mediana entre deputados.",
        )

    col3, col4 = st.columns(2)
    with col3:
        fig = bar_sum_horizontal(
            data,
            "uf",
            "Soma total por UF",
            "Soma valor liquido (R$)",
            top_n=27,
        )
        show_chart(fig, "rq2_uf_soma")
    with col4:
        fig = bar_median_per_entity(
            data,
            "uf",
            "Mediana do gasto por deputado — UF",
            top_n=27,
        )
        show_chart(fig, "rq2_uf_mediana")

    per_deputy = (
        data.groupby(["partido", "deputado"], as_index=False)["valor_liquido"]
        .sum()
    )
    top_parties = (
        per_deputy.groupby("partido")["valor_liquido"]
        .median()
        .sort_values(ascending=False)
        .head(10)
        .index
    )
    box_data = per_deputy[per_deputy["partido"].isin(top_parties)]
    fig_box = style_box(px.box(
        box_data,
        x="partido",
        y="valor_liquido",
        title="Dispersao do gasto por deputado — top 10 partidos (mediana)",
        labels={"partido": "Partido", "valor_liquido": "Gasto total do deputado (R$)"},
    ))
    show_chart(
        fig_box,
        "rq2_boxplot_partido",
        "Cada ponto e a soma de um deputado no periodo filtrado.",
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
    row_totals = pivot.sum(axis=1).replace(0, pd.NA)
    pivot_pct = pivot.div(row_totals, axis=0) * 100

    fig_heat = style_heatmap(px.imshow(
        pivot_pct,
        aspect="auto",
        title="Composicao percentual por partido (top 15 partidos x 8 tipos)",
        labels={"x": "Tipo de despesa", "y": "Partido", "color": "% do partido"},
        color_continuous_scale="Blues",
    ))
    show_chart(
        fig_heat,
        "rq2_heatmap_pct",
        "Cada linha soma 100%: mostra o perfil de gastos do partido, nao o volume bruto.",
    )


def section_rq3(data: pd.DataFrame) -> None:
    st.header("RQ3: Quais deputados e fornecedores concentram os maiores valores?")
    st.markdown(
        "Rankings por **soma do valor liquido** no periodo filtrado. Para deputados, "
        "ative o filtro lateral *Excluir estruturas de lideranca* para focar em parlamentares. "
        "A tabela lista apenas os **500 maiores** lancamentos."
    )

    col1, col2 = st.columns(2)
    with col1:
        fig = bar_sum_horizontal(
            data,
            "deputado",
            "Top deputados por valor liquidado (top 15)",
            "Soma valor liquido (R$)",
            top_n=15,
        )
        show_chart(
            fig,
            "rq3_deputados",
            "Use o filtro lateral para excluir estruturas de lideranca (LID/LIDER).",
        )
    with col2:
        fig = bar_sum_horizontal(
            data,
            "fornecedor",
            "Top fornecedores por valor liquidado (top 15)",
            "Soma valor liquido (R$)",
            top_n=15,
        )
        show_chart(fig, "rq3_fornecedores")

    st.subheader("Tabela detalhada (top 500 lancamentos)")
    columns = [
        "ano",
        "mes",
        "data_referencia",
        "data_emissao",
        "deputado",
        "partido",
        "uf",
        "tipo_despesa",
        "fornecedor",
        "valor_liquido",
    ]
    top_table = data[columns].sort_values("valor_liquido", ascending=False).head(500)
    st.dataframe(top_table, use_container_width=True, hide_index=True)

    csv_bytes = top_table.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Exportar tabela (CSV)",
        data=csv_bytes,
        file_name="lab04_top500_lancamentos.csv",
        mime="text/csv",
        key="dl_tabela_top500",
    )


def main() -> None:
    st.title("Despesas Parlamentares - CEAP")
    st.caption(
        "Laboratorio 04 Sprint 03 | Dados abertos da Camara dos Deputados | "
        "Exporte cada grafico em PNG ou HTML pelos botoes abaixo dele."
    )

    data = load_data()
    filtered = apply_filters(data)

    if filtered.empty:
        st.warning("Nenhum registro encontrado para os filtros selecionados.")
        st.stop()

    tabs = st.tabs([
        "Dataset",
        "RQ1 - Tipos de despesa",
        "RQ2 - Partido e UF",
        "RQ3 - Deputados e fornecedores",
    ])

    with tabs[0]:
        section_dataset(filtered)
    with tabs[1]:
        section_rq1(filtered)
    with tabs[2]:
        section_rq2(filtered)
    with tabs[3]:
        section_rq3(filtered)


if __name__ == "__main__":
    main()
