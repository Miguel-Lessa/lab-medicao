from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lab05.analysis import generate_report


if __name__ == "__main__":
    report = generate_report(ROOT / "output" / "results.csv", ROOT / "relatorios" / "relatorio_lab05_final.md")
    print(report)
