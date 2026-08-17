from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {"validate", "dashboard", "events"}:
        print("Usage: python sentinel_cli.py validate|dashboard|events")
        return 2
    command = sys.argv[1]
    if command == "validate":
        files = [
            ("controller", "src/controller/monitor.py"),
            ("topology", "scripts/custom_topology.py"),
            ("preprocessing", "preprocess_dataset.py"),
            ("training", "notebooks/train_model.py"),
        ]
        ok = True
        for name, relative in files:
            exists = (ROOT / relative).exists()
            print(("✓" if exists else "✗"), name, relative)
            ok = ok and exists
        return 0 if ok else 1
    if command == "dashboard":
        return subprocess.call([
            sys.executable, "-m", "streamlit", "run", "dashboard/app.py"
        ], cwd=ROOT)
    path = ROOT / "results" / "events.jsonl"
    print(path.read_text() if path.exists() else f"No events file: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
