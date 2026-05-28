"""Coleta arquivos anuais da CEAP disponibilizados pela Camara dos Deputados."""

from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import BadZipFile, ZipFile

import requests


BASE_URL = "http://www.camara.leg.br/cotas/Ano-{ano}.csv.zip"
ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "data" / "raw"
DEFAULT_YEARS = [2020, 2021, 2022, 2023, 2024, 2025]


def download_year(ano: int, force: bool = False) -> Path:
    """Baixa e extrai o CSV da CEAP para um ano."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    zip_path = RAW_DIR / f"Ano-{ano}.csv.zip"
    csv_path = RAW_DIR / f"Ano-{ano}.csv"

    if csv_path.exists() and not force:
        print(f"[ok] {csv_path} ja existe; use --force para baixar novamente.")
        return csv_path

    url = BASE_URL.format(ano=ano)
    print(f"[download] {url}")
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    zip_path.write_bytes(response.content)

    try:
        with ZipFile(zip_path) as archive:
            csv_members = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if not csv_members:
                raise RuntimeError(f"Nenhum CSV encontrado em {zip_path}.")

            member = csv_members[0]
            with archive.open(member) as source, csv_path.open("wb") as target:
                target.write(source.read())
    except BadZipFile as exc:
        raise RuntimeError(f"Arquivo baixado nao e um ZIP valido: {zip_path}") from exc

    print(f"[ok] extraido em {csv_path}")
    return csv_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Baixa os CSVs anuais da CEAP.")
    parser.add_argument(
        "--anos",
        nargs="+",
        type=int,
        default=DEFAULT_YEARS,
        help="Anos que devem ser baixados. Padrao: 2020 2021 2022 2023 2024 2025.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Baixa novamente mesmo se o CSV ja existir.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    for ano in args.anos:
        download_year(ano, force=args.force)


if __name__ == "__main__":
    main()
