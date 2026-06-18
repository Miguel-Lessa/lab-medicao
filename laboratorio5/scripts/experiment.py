from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lab05.experiment import run_validation_then_official


if __name__ == "__main__":
    summary = run_validation_then_official(
        validation_output=ROOT / "output" / "validation_results.csv",
        official_output=ROOT / "output" / "results.csv",
    )
    print(f"Registros validos: {summary.successful_records}")
    print(f"Falhas: {len(summary.failures)}")
    print(f"Arquivo: {summary.output_path}")
