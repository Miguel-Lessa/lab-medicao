import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent


def run_step(script_name: str) -> None:
    script_path = PROJECT_DIR / "scripts" / script_name
    print(f"\nExecutando: {script_path.name}")
    subprocess.run([sys.executable, str(script_path)], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Executa o pipeline completo: coleta -> analise -> PDF opcional."
    )
    parser.add_argument(
        "--sem-pdf",
        action="store_true",
        help="Executa apenas coleta e analise (sem gerar PDF).",
    )
    args = parser.parse_args()

    run_step("coleta_sprint2.py")
    run_step("analise_sprint3.py")

    if not args.sem_pdf:
        run_step("gerar_pdf_relatorio.py")

    print("\nPipeline concluido.")


if __name__ == "__main__":
    main()
