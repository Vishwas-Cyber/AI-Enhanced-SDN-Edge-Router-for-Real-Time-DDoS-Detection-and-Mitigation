import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_release_documents_exist():
    for name in ["PROJECT_STATUS.md","ARCHITECTURE.md","THREAT_MODEL.md","DEMO_SCRIPT.md"]:
        assert (ROOT/"docs"/name).exists()

def test_experiment_config_is_authorized_local_lab():
    text=(ROOT/"configs/experiment.yaml").read_text()
    assert "local-mininet-only" in text
    assert "openflow_version: '1.3'" in text
    assert "mitigation_priority: 500" in text

def test_gitignore_excludes_environment_and_secrets():
    text=(ROOT/".gitignore").read_text()
    assert ".venv/" in text
    assert "mininam-env/" in text
    assert ".streamlit/secrets.toml" in text
