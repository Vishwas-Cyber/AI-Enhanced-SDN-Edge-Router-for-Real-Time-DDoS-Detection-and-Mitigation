from __future__ import annotations
import json
from pathlib import Path
from typing import Mapping

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"configs/runtime_features.json"


def feature_names() -> list[str]:
    return json.loads(CONTRACT.read_text())["features"]


def vectorize(sample: Mapping[str, float]) -> list[float]:
    names=feature_names()
    missing=[name for name in names if name not in sample]
    if missing:
        raise ValueError(f"Missing runtime features: {missing}")
    return [float(sample[name]) for name in names]


def explain(sample: Mapping[str, float], probability: float | None = None) -> dict:
    values=vectorize(sample)
    threshold=float(json.loads(CONTRACT.read_text())["threshold"])
    return {
        "features": dict(zip(feature_names(), values)),
        "model_probability": probability,
        "decision": "attack" if probability is not None and probability >= threshold else "review",
        "threshold": threshold,
    }
