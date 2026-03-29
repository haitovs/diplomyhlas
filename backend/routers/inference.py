"""
Model info and one-shot prediction endpoint.
"""

from fastapi import APIRouter
from src.inference.realtime import RealtimePredictor

router = APIRouter()

_predictor = RealtimePredictor()


@router.get("/model")
def model_info():
    return _predictor.get_model_info()


@router.post("/predict")
def predict(flow: dict):
    return _predictor.predict(flow)
