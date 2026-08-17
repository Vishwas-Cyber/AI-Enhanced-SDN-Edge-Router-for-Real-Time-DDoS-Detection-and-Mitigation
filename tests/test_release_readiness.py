import json
from pathlib import Path
from src.model_contract import decision, validate_sample
ROOT=Path(__file__).resolve().parents[1]

def test_manifest_features():
    data=json.loads((ROOT/"configs/model_manifest.json").read_text())
    assert data["features"]==["pps","bps","packets","bytes","duration_sec"]

def test_sample_contract():
    sample={"pps":1,"bps":2,"packets":3,"bytes":4,"duration_sec":5}
    assert validate_sample(sample)==[1,2,3,4,5]
    assert decision(sample,0.9)["detection_mode"]=="ml"
