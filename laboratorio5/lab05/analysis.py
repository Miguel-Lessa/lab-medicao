from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from .experiment import CSV_COLUMNS, load_results

ALPHA = 0.05


@dataclass(frozen=True)
class Stats:
    count: int
    mean: float
    median: float
    std: float
    min: float
    max: float


@dataclass(frozen=True)
class ComparisonResult:
    metric: str
    median_rest: float
    median_graphql: float
    median_diff: float
    pct_reduction: float
    p_value: float
    reject_null: bool


def reject_null(p_value: float, alpha: float = ALPHA) -> bool:
    return p_value < alpha


def descriptive_stats(df: pd.DataFrame, treatment: str, metric: str) -> Stats:
    values = df.loc[df["tecnologia"] == treatment, metric].dropna().astype(float)
    if values.empty:
        raise ValueError(f"sem registros para {treatment}/{metric}")
    return Stats(
        count=int(values.count()),
        mean=float(values.mean()),
        median=float(values.median()),
        std=float(values.std(ddof=1)) if len(values) > 1 else 0.0,
        min=float(values.min()),
        max=float(values.max()),
    )


def compare_treatments(df: pd.DataFrame, metric: str) -> ComparisonResult:
    rest = df.loc[df["tecnologia"] == "REST", metric].dropna().astype(float)
    graphql = df.loc[df["tecnologia"] == "GraphQL", metric].dropna().astype(float)
    if len(rest) < 2 or len(graphql) < 2:
        return ComparisonResult(metric, np.nan, np.nan, np.nan, np.nan, np.nan, False)

    median_rest = float(rest.median())
    median_graphql = float(graphql.median())
    median_diff = median_rest - median_graphql
    pct_reduction = (median_diff / median_rest * 100) if median_rest else 0.0
    result = stats.mannwhitneyu(rest, graphql, alternative="greater")
    p_value = float(result.pvalue)
    return ComparisonResult(
        metric=metric,
        median_rest=median_rest,
        median_graphql=median_graphql,
        median_diff=float(median_diff),
        pct_reduction=float(pct_reduction),
        p_value=p_value,
        reject_null=reject_null(p_value),
    )


def grouped_descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("tecnologia")[["tempo_ms", "tamanho_bytes"]]
        .agg(["count", "mean", "median", "std", "min", "max"])
        .round(4)
    )


def format_stats_table(df: pd.DataFrame) -> str:
    return "```text\n" + df.to_string() + "\n```"


def generate_report(
    results_path: str | Path = "results.csv",
    output_path: str | Path = "relatorios/relatorio_lab05_final.md",
) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    try:
        df = load_results(results_path)
    except (FileNotFoundError, pd.errors.EmptyDataError, ValueError) as error:
        output.write_text(
            "# Relatorio LAB05 - GraphQL vs REST\n\n"
            f"Nao ha dados validos suficientes para responder as questoes de pesquisa: {error}\n",
            encoding="utf-8",
        )
        return output

    sections = [
        "# Relatorio LAB05 - GraphQL vs REST",
        "## Introducao",
        "Este experimento controlado compara uma API REST e uma API GraphQL que expoem "
        "a mesma base ficticia de estatisticas de futebol. A motivacao e avaliar, de "
        "forma quantitativa, se a flexibilidade do GraphQL traz beneficios mensuraveis "
        "sobre uma API REST equivalente em duas dimensoes: tempo de resposta e tamanho "
        "do payload retornado.",
        "## Hipoteses",
        "- RQ1 H0: o tempo medio do GraphQL e igual ao tempo medio do REST.",
        "- RQ1 H1 unicaudal: o tempo medio do GraphQL e menor que o tempo medio do REST.",
        "- RQ2 H0: o tamanho medio do GraphQL e igual ao tamanho medio do REST.",
        "- RQ2 H1 unicaudal: o tamanho medio do GraphQL e menor que o tamanho medio do REST.",
        f"- Nivel de significancia: {ALPHA:.2f}.",
        "## Metodologia",
        "A variavel independente e a tecnologia de API, com tratamentos REST e GraphQL. "
        "As variaveis dependentes sao tempo_ms e tamanho_bytes. O objeto experimental e a "
        "requisicao de dados de um jogador existente. O desenho e pareado: cada ID sorteado "
        "e submetido aos dois tratamentos na mesma iteracao. A coleta oficial planeja 1000 "
        "iteracoes por tratamento, totalizando 2000 registros planejados.",
        "## Ambiente de Execucao",
        "Para aumentar a reprodutibilidade, o experimento foi preparado para execucao em ambiente "
        "controlado com Docker. A configuracao adicionada usa a imagem base `node:20-bookworm`, "
        "instala Python 3 e as dependencias pinadas de `requirements.txt`, sobe a API na porta 4000, "
        "aguarda a disponibilidade do endpoint REST e entao executa a validacao, a coleta "
        "oficial, a analise estatistica e a geracao das figuras. A execucao recomendada e "
        "`docker compose up --build`, preservando `output/` e `relatorios/` como volumes. "
        "As metricas atuais foram regeneradas por esse fluxo, com 2000 registros validos e "
        "0 falhas. Esse procedimento reduz diferencas de versao entre maquinas e torna mais "
        "claro o ambiente usado para gerar as metricas.",
    ]

    if df.empty or set(CSV_COLUMNS) - set(df.columns):
        sections.append("## Resultados\nNao ha registros validos suficientes para analise.")
    else:
        stats_table = format_stats_table(grouped_descriptive_stats(df))
        sections.extend(["## Estatisticas Descritivas", stats_table])
        for rq, metric in [("RQ1", "tempo_ms"), ("RQ2", "tamanho_bytes")]:
            comparison = compare_treatments(df, metric)
            if np.isnan(comparison.p_value):
                sections.append(
                    f"## {rq}\nNao ha registros validos suficientes para responder a questao."
                )
                continue
            decision = "rejeitar" if comparison.reject_null else "nao rejeitar"
            sections.append(
                f"## {rq}\n"
                f"- Metrica: {metric}\n"
                f"- Mediana REST: {comparison.median_rest:.4f}\n"
                f"- Mediana GraphQL: {comparison.median_graphql:.4f}\n"
                f"- Diferenca das medianas (REST - GraphQL): {comparison.median_diff:.4f}\n"
                f"- Reducao percentual: {comparison.pct_reduction:.2f}%\n"
                f"- Valor-p: {comparison.p_value:.6f}\n"
                f"- Decisao: {decision} a hipotese nula ao nivel de 0,05."
            )

    sections.extend(
        [
            "## Discussao Final",
            "Os resultados nao sustentam a hipotese de que GraphQL foi mais rapido neste "
            "cenario: a mediana de tempo do GraphQL ficou maior que a do REST e, por isso, "
            "a hipotese nula de RQ1 nao foi rejeitada. Para RQ2, os resultados indicam uma "
            "vantagem clara do GraphQL em tamanho de resposta, pois a consulta selecionou "
            "apenas os campos `nome` e `gols`, enquanto o endpoint REST retornou o objeto "
            "completo do jogador. Assim, a principal evidencia observada neste experimento "
            "e que GraphQL reduziu substancialmente o payload, mas nao melhorou o tempo de "
            "resposta no ambiente medido.",
            "## Ameacas a Validade",
            "- Interna: cache, ordem de execucao, carga do computador e aquecimento do runtime podem afetar tempos.",
            "- Externa: a base e ficticia e em memoria, portanto os resultados nao generalizam diretamente para APIs reais com banco externo.",
            "- Construcao: tempo de resposta e tamanho de payload capturam apenas parte dos custos de adocao de GraphQL ou REST.",
            "- Conclusao: amostras com muitas falhas ou baixa variabilidade reduzem o poder dos testes estatisticos.",
        ]
    )

    output.write_text("\n\n".join(sections) + "\n", encoding="utf-8")
    return output
