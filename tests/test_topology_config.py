import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_topology_config_is_valid():
    data=json.loads((ROOT/"configs/topology.json").read_text())
    nodes={node["id"] for node in data["nodes"]}
    assert nodes
    for link in data["links"]:
        assert link["source"] in nodes
        assert link["target"] in nodes
        assert link["source"] != link["target"]
