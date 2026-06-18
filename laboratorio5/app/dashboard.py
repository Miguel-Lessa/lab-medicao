from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lab05.dashboard import render_dashboard


def main():
    result = render_dashboard(ROOT / "output" / "results.csv", ROOT / "output" / "figures")
    print(result["message"])
    if result["status"] == "ok":
        print(result["stats"])
        for path in result["saved_files"].values():
            print(path)


if __name__ == "__main__":
    main()
