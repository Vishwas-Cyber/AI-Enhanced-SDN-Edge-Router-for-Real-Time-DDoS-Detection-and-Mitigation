from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"configs/model_manifest.json"


def manifest():
    return json.loads(MANIFEST.read_text())


def validate_sample(sample):
    names=manifest()["features"]
    missing=[x for x in names if x not in sample]
    if missing: raise ValueError(f"Missing model features: {missing}")
    return [float(sample[x]) for x in names]


def decision(sample, probability=None):
    cfg=manifest(); validate_sample(sample)
    return {
        "decision": "attack" if probability is not None and probability >= cfg["threshold"] else "review",
        "model_probability": probability,
        "model_version": cfg["model_version"],
        "decision_threshold": cfg["threshold"],
        "detection_mode": "ml" if probability is not None else "rule_based"
    }
