"""Prepara a base CEAP para uso no dashboard interativo."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "data" / "raw"
OUTPUT_DIR = ROOT_DIR / "output"
OUTPUT_FILE = OUTPUT_DIR / "despesas_ceap_tratadas.csv"


COLUMN_MAP = {
    "txNomeParlamentar": "deputado",
    "ideCadastro": "id_deputado",
    "sgUF": "uf",
    "sgPartido": "partido",
    "txtDescricao": "tipo_despesa",
    "txtFornecedor": "fornecedor",
    "txtCNPJCPF": "cnpj_cpf_fornecedor",
    "datEmissao": "data_emissao",
    "vlrDocumento": "valor_documento",
    "vlrGlosa": "valor_glosa",
    "vlrLiquido": "valor_liquido",
    "numAno": "ano",
    "numMes": "mes",
}

TEXT_COLUMNS = ["deputado", "uf", "partido", "tipo_despesa", "fornecedor"]
VALUE_COLUMNS = ["valor_documento", "valor_glosa", "valor_liquido"]


def sniff_separator(path: Path) -> str:
    sample = path.read_text(encoding="utf-8-sig", errors="ignore")[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=";,")
        return dialect.delimiter
    except csv.Error:
        return ";"


def read_raw_csv(path: Path) -> pd.DataFrame:
    sep = sniff_separator(path)
    return pd.read_csv(
        path,
        sep=sep,
        encoding="utf-8-sig",
        dtype=str,
        low_memory=False,
    )


def parse_decimal(series: pd.Series) -> pd.Series:
    normalized = series.fillna("0").astype(str).str.strip()
    uses_comma_decimal = normalized.str.contains(",", regex=False)
    normalized = normalized.mask(
        uses_comma_decimal,
        normalized.str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
    )
    return pd.to_numeric(normalized, errors="coerce").fillna(0.0)


def clean_frame(frame: pd.DataFrame) -> pd.DataFrame:
    available = {source: target for source, target in COLUMN_MAP.items() if source in frame.columns}
    frame = frame.rename(columns=available)

    missing = sorted(set(COLUMN_MAP.values()) - set(frame.columns))
    if missing:
        raise RuntimeError(f"Colunas obrigatorias ausentes: {', '.join(missing)}")

    frame = frame[list(COLUMN_MAP.values())].copy()

    for column in TEXT_COLUMNS:
        frame[column] = (
            frame[column]
            .fillna("Nao informado")
            .astype(str)
            .str.strip()
            .replace("", "Nao informado")
        )

    for column in VALUE_COLUMNS:
        frame[column] = parse_decimal(frame[column])

    frame["ano"] = pd.to_numeric(frame["ano"], errors="coerce").astype("Int64")
    frame["mes"] = pd.to_numeric(frame["mes"], errors="coerce").astype("Int64")
    frame["data_referencia"] = pd.to_datetime(
        {
            "year": pd.to_numeric(frame["ano"], errors="coerce"),
            "month": pd.to_numeric(frame["mes"], errors="coerce"),
            "day": 1,
        },
        errors="coerce",
    )
    frame["data_emissao"] = pd.to_datetime(frame["data_emissao"], errors="coerce", dayfirst=False)
    frame["data_emissao"] = frame["data_emissao"].fillna(frame["data_referencia"])
    frame["ano_mes"] = frame["data_referencia"].dt.to_period("M").astype(str)
    frame.loc[frame["ano_mes"] == "NaT", "ano_mes"] = "Sem data"

    frame["tipo_despesa"] = frame["tipo_despesa"].str.replace(r"\s+", " ", regex=True)
    frame["fornecedor"] = frame["fornecedor"].str.replace(r"\s+", " ", regex=True)
    frame["valor_liquido"] = frame["valor_liquido"].clip(lower=0)

    return frame


def prepare(input_dir: Path = RAW_DIR, output_file: Path = OUTPUT_FILE) -> pd.DataFrame:
    csv_files = sorted(input_dir.glob("Ano-*.csv"))
    if not csv_files:
        raise RuntimeError(
            f"Nenhum CSV encontrado em {input_dir}. Rode scripts/coleta_ceap.py primeiro."
        )

    frames = [read_raw_csv(path) for path in csv_files]
    combined = pd.concat(frames, ignore_index=True)
    cleaned = clean_frame(combined)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(output_file, index=False, encoding="utf-8")

    print(f"[ok] {len(cleaned):,} registros salvos em {output_file}".replace(",", "."))
    print(f"[ok] valor liquido total: R$ {cleaned['valor_liquido'].sum():,.2f}")
    return cleaned


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepara os dados CEAP para o dashboard.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=RAW_DIR,
        help="Diretorio com os CSVs brutos Ano-*.csv.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_FILE,
        help="Arquivo CSV tratado de saida.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    prepare(args.input_dir, args.output)


if __name__ == "__main__":
    main()
