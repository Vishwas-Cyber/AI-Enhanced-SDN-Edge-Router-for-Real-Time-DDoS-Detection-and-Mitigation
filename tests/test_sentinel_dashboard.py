import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_topology_has_symbols_and_links():
    data=json.loads((ROOT/"configs/topology.json").read_text())
    kinds={node["kind"] for node in data["nodes"]}
    assert {"controller","switch","host"}.issubset(kinds)
    ids={node["id"] for node in data["nodes"]}
    assert data["links"]
    assert all(link["source"] in ids and link["target"] in ids for link in data["links"])

def test_dashboard_exists():
    assert (ROOT/"dashboard/app.py").exists()
