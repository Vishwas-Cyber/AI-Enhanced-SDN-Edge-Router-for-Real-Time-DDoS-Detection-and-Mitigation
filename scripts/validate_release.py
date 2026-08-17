import json, sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
errors=[]
required=["README.md","requirements.txt","pyproject.toml","configs/topology.json","configs/experiment.yaml","configs/policy.yaml","configs/model_manifest.json","docs/PROJECT_STATUS.md","docs/ARCHITECTURE.md","docs/THREAT_MODEL.md","docs/DEMO_SCRIPT.md"]
for item in required:
    if not (root/item).exists(): errors.append(f"missing {item}")
try:
    topo=json.loads((root/"configs/topology.json").read_text())
    ids={n["id"] for n in topo["nodes"]}
    if not {"controller","switch","host"}.issubset({n["kind"] for n in topo["nodes"]}): errors.append("topology missing required kinds")
    if any(e["source"] not in ids or e["target"] not in ids or e["source"]==e["target"] for e in topo["links"]): errors.append("invalid topology link")
except Exception as exc: errors.append(f"topology invalid: {exc}")
try:
    manifest=json.loads((root/"configs/model_manifest.json").read_text())
    if manifest["features"] != ["pps","bps","packets","bytes","duration_sec"]: errors.append("model feature contract invalid")
except Exception as exc: errors.append(f"model manifest invalid: {exc}")
if errors:
    for e in errors: print(f"FAIL {e}")
    sys.exit(1)
print("RELEASE READY: artifacts, topology, policy, and model contract validated")
