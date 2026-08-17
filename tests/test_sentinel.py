from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_original_files_are_present():
    for path in [
        "scripts/custom_topology.py",
        "preprocess_dataset.py",
        "notebooks/train_model.py",
        "src/controller/monitor.py",
    ]:
        assert (ROOT / path).exists(), path


def test_dashboard_is_present():
    assert (ROOT / "dashboard" / "app.py").exists()
