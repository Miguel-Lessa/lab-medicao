from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lab05.analysis import compare_treatments, grouped_descriptive_stats
from lab05.experiment import CSV_COLUMNS, load_results

RESULTS_PATH = ROOT / "output" / "results.csv"
VALIDATION_PATH = ROOT / "output" / "validation_results.csv"


@st.cache_data
def read_results(path: str) -> pd.DataFrame:
    return load_results(path)


def format_ms(value: float) -> str:
    return f"{value:.4f} ms"


def format_bytes(value: float) -> str:
    return f"{value:.0f} bytes"


def metric_summary(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    return (
        df.groupby("tecnologia")[metric]
        .agg(["count", "mean", "median", "std", "min", "max"])
        .reset_index()
        .round(4)
    )


def draw_boxplot(df: pd.DataFrame, metric: str, title: str, ylabel: str):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.boxplot(data=df, x="tecnologia", y=metric, hue="tecnologia", ax=ax, legend=False)
    ax.set_title(title)
    ax.set_xlabel("Tecnologia")
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    return fig


def draw_histogram(df: pd.DataFrame, metric: str, title: str, xlabel: str):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.histplot(
        data=df,
        x=metric,
        hue="tecnologia",
        kde=True,
        element="step",
        stat="density",
        common_norm=False,
        ax=ax,
    )
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Densidade")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    return fig


def render_decision_card(label: str, p_value: float, decision: str, interpretation: str):
    st.markdown(f"#### {label}")
    cols = st.columns([1, 1, 2])
    cols[0].metric("Valor-p", f"{p_value:.6f}")
    cols[1].metric("Decisao", decision)
    cols[2].write(interpretation)


def main():
    st.set_page_config(
        page_title="Lab 05 - GraphQL vs REST",
        layout="wide",
    )

    st.title("Lab 05 - GraphQL vs REST")
    st.caption("Dashboard interativo dos resultados do experimento controlado")

    if not RESULTS_PATH.exists():
        st.error("Arquivo output/results.csv nao encontrado. Execute: docker compose up --build")
        st.stop()

    try:
        df = read_results(str(RESULTS_PATH))
    except (OSError, pd.errors.EmptyDataError, ValueError) as error:
        st.error(f"Nao foi possivel carregar os resultados: {error}")
        st.stop()

    missing_columns = set(CSV_COLUMNS) - set(df.columns)
    if missing_columns:
        st.error(f"Colunas ausentes no CSV: {', '.join(sorted(missing_columns))}")
        st.stop()

    st.sidebar.header("Filtros")
    technologies = st.sidebar.multiselect(
        "Tecnologias",
        options=sorted(df["tecnologia"].unique()),
        default=sorted(df["tecnologia"].unique()),
    )
    max_rows = st.sidebar.slider("Linhas na amostra", min_value=10, max_value=200, value=30, step=10)

    filtered = df[df["tecnologia"].isin(technologies)].copy()
    if filtered.empty:
        st.warning("Nenhum dado selecionado nos filtros.")
        st.stop()

    rest_time = df.loc[df["tecnologia"] == "REST", "tempo_ms"].median()
    gql_time = df.loc[df["tecnologia"] == "GraphQL", "tempo_ms"].median()
    rest_size = df.loc[df["tecnologia"] == "REST", "tamanho_bytes"].median()
    gql_size = df.loc[df["tecnologia"] == "GraphQL", "tamanho_bytes"].median()
    size_reduction = (rest_size - gql_size) / rest_size * 100
    time_delta = rest_time - gql_time

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Registros validos", f"{len(df):,}".replace(",", "."))
    m2.metric("Falhas", "0")
    m3.metric("Mediana REST", format_ms(rest_time))
    m4.metric("Mediana GraphQL", format_ms(gql_time), delta=format_ms(time_delta))

    m5, m6, m7, m8 = st.columns(4)
    m5.metric("Payload REST", format_bytes(rest_size))
    m6.metric("Payload GraphQL", format_bytes(gql_size))
    m7.metric("Reducao de payload", f"{size_reduction:.2f}%")
    m8.metric("Amostras por tratamento", "1000")

    st.divider()

    overview, charts, stats, data = st.tabs(
        ["Resumo", "Graficos", "Estatisticas", "Dados"]
    )

    with overview:
        st.subheader("Resposta rapida para apresentacao")
        st.write(
            "GraphQL reduziu fortemente o tamanho da resposta, mas nao foi mais rapido "
            "que REST neste cenario local com base em memoria."
        )

        rq1 = compare_treatments(df, "tempo_ms")
        rq2 = compare_treatments(df, "tamanho_bytes")

        render_decision_card(
            "RQ1 - GraphQL e mais rapido?",
            rq1.p_value,
            "Nao rejeitar H0",
            "A mediana de tempo do GraphQL ficou maior que a do REST.",
        )
        render_decision_card(
            "RQ2 - GraphQL tem payload menor?",
            rq2.p_value,
            "Rejeitar H0",
            "A consulta GraphQL retornou apenas nome e gols, reduzindo o payload.",
        )

        st.markdown("#### Hipoteses")
        st.table(
            pd.DataFrame(
                [
                    ["RQ1", "H0", "Tempo medio GraphQL = tempo medio REST"],
                    ["RQ1", "H1", "Tempo medio GraphQL < tempo medio REST"],
                    ["RQ2", "H0", "Tamanho medio GraphQL = tamanho medio REST"],
                    ["RQ2", "H1", "Tamanho medio GraphQL < tamanho medio REST"],
                ],
                columns=["Questao", "Tipo", "Hipotese"],
            )
        )

    with charts:
        left, right = st.columns(2)
        with left:
            st.pyplot(
                draw_boxplot(
                    filtered,
                    "tempo_ms",
                    "Distribuicao do tempo de resposta",
                    "Tempo (ms)",
                )
            )
            st.pyplot(
                draw_histogram(
                    filtered,
                    "tempo_ms",
                    "Densidade do tempo de resposta",
                    "Tempo (ms)",
                )
            )
        with right:
            st.pyplot(
                draw_boxplot(
                    filtered,
                    "tamanho_bytes",
                    "Distribuicao do tamanho da resposta",
                    "Tamanho (bytes)",
                )
            )
            st.pyplot(
                draw_histogram(
                    filtered,
                    "tamanho_bytes",
                    "Densidade do tamanho da resposta",
                    "Tamanho (bytes)",
                )
            )

    with stats:
        st.subheader("Tabela estatistica geral")
        st.dataframe(grouped_descriptive_stats(df), width="stretch")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Tempo de resposta")
            st.dataframe(metric_summary(df, "tempo_ms"), width="stretch")
        with c2:
            st.markdown("#### Tamanho da resposta")
            st.dataframe(metric_summary(df, "tamanho_bytes"), width="stretch")

        st.markdown("#### Comparacao estatistica")
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "RQ": "RQ1",
                        "Metrica": rq1.metric,
                        "Mediana REST": rq1.median_rest,
                        "Mediana GraphQL": rq1.median_graphql,
                        "REST - GraphQL": rq1.median_diff,
                        "Reducao percentual": rq1.pct_reduction,
                        "Valor-p": rq1.p_value,
                        "Rejeita H0": rq1.reject_null,
                    },
                    {
                        "RQ": "RQ2",
                        "Metrica": rq2.metric,
                        "Mediana REST": rq2.median_rest,
                        "Mediana GraphQL": rq2.median_graphql,
                        "REST - GraphQL": rq2.median_diff,
                        "Reducao percentual": rq2.pct_reduction,
                        "Valor-p": rq2.p_value,
                        "Rejeita H0": rq2.reject_null,
                    },
                ]
            ).round(6),
            width="stretch",
        )

    with data:
        st.subheader("Dados coletados")
        st.dataframe(filtered.head(max_rows), width="stretch")

        st.download_button(
            "Baixar results.csv",
            data=RESULTS_PATH.read_bytes(),
            file_name="results.csv",
            mime="text/csv",
        )

        if VALIDATION_PATH.exists():
            st.download_button(
                "Baixar validation_results.csv",
                data=VALIDATION_PATH.read_bytes(),
                file_name="validation_results.csv",
                mime="text/csv",
            )


if __name__ == "__main__":
    main()
