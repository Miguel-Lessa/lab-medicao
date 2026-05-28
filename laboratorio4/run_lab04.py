#!/usr/bin/env python3
"""Executa o pipeline do Laboratorio 04 em sequencia (coleta -> tratamento -> figuras -> dashboard)."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parent
SCRIPTS = LAB_DIR / "scripts"
OUTPUT_CSV = LAB_DIR / "output" / "despesas_ceap_tratadas.csv"
DEFAULT_YEARS = "2020 2021 2022 2023 2024 2025"


def repo_venv_python() -> Path:
    if sys.platform == "win32":
        return REPO_ROOT / ".venv" / "Scripts" / "python.exe"
    return REPO_ROOT / ".venv" / "bin" / "python"


def run_step(label: str, command: list[str], cwd: Path) -> None:
    print(f"\n>> {label}")
    print("   ", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pipeline completo do Laboratorio 04 (CEAP)."
    )
    parser.add_argument(
        "--anos",
        nargs="+",
        type=int,
        default=[2020, 2021, 2022, 2023, 2024, 2025],
        help="Anos para coleta da CEAP.",
    )
    parser.add_argument(
        "--skip-coleta",
        action="store_true",
        help="Pula download dos CSVs (use se data/raw ja estiver preenchido).",
    )
    parser.add_argument(
        "--skip-figuras",
        action="store_true",
        help="Nao exporta PNGs em relatorios/figuras/.",
    )
    parser.add_argument(
        "--skip-dashboard",
        action="store_true",
        help="Nao inicia o Streamlit ao final.",
    )
    parser.add_argument(
        "--force-coleta",
        action="store_true",
        help="Rebaixa os ZIPs mesmo se o CSV do ano ja existir.",
    )
    parser.add_argument(
        "--python",
        type=Path,
        default=None,
        help="Interpretador Python (padrao: o mesmo que executou este script).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    python = args.python or Path(sys.executable)

    if not python.exists():
        venv_py = repo_venv_python()
        if venv_py.exists():
            python = venv_py
        else:
            print(
                "Erro: ambiente virtual nao encontrado. Rode antes:\n"
                "  Windows:  laboratorio4\\setup_and_run.ps1\n"
                "  Linux:    ./laboratorio4/setup_and_run.sh"
            )
            sys.exit(1)

    os.chdir(REPO_ROOT)
    print(f"Raiz do repositorio: {REPO_ROOT}")
    print(f"Python: {python}")

    if not args.skip_coleta:
        cmd = [str(python), str(SCRIPTS / "coleta_ceap.py"), "--anos", *map(str, args.anos)]
        if args.force_coleta:
            cmd.append("--force")
        run_step("Coleta CEAP", cmd, REPO_ROOT)
    else:
        print("\n>> Coleta CEAP (pulada)")

    run_step(
        "Tratamento dos dados",
        [str(python), str(SCRIPTS / "prepara_dados.py")],
        REPO_ROOT,
    )

    if not OUTPUT_CSV.exists():
        print(f"Erro: arquivo nao gerado: {OUTPUT_CSV}")
        sys.exit(1)

    if not args.skip_figuras:
        run_step(
            "Exportacao das figuras do relatorio",
            [str(python), str(SCRIPTS / "exportar_figuras_relatorio.py")],
            REPO_ROOT,
        )
    else:
        print("\n>> Exportacao de figuras (pulada)")

    if args.skip_dashboard:
        print("\nPipeline concluido (sem dashboard).")
        print(f"Base tratada: {OUTPUT_CSV}")
        return

    print("\n>> Dashboard Streamlit")
    print("   URL: http://localhost:8501")
    print("   Na primeira vez, se pedir Email:, pressione Enter.")
    print("   Encerrar: Ctrl+C\n")
    run_step(
        "Dashboard",
        [
            str(python),
            "-m",
            "streamlit",
            "run",
            str(LAB_DIR / "app" / "dashboard.py"),
            "--server.headless",
            "false",
        ],
        REPO_ROOT,
    )


if __name__ == "__main__":
    main()
