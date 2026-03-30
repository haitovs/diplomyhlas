"""
Model info and one-shot prediction endpoint.
"""

import sys
from pathlib import Path
from fastapi import APIRouter

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.inference.realtime import RealtimePredictor

router = APIRouter()

_predictor = RealtimePredictor(model_path=str(PROJECT_ROOT / "models"))


@router.get("/model")
def model_info():
    return _predictor.get_model_info()


@router.post("/predict")
def predict(flow: dict):
    return _predictor.predict(flow)
