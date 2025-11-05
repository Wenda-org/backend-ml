from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any

from app.core.config import settings
from app.api import ml

router = APIRouter()

# Incluir rotas de ML
router.include_router(ml.router)


class HealthResp(BaseModel):
    status: str


@router.get("/health", response_model=HealthResp)
async def health():
    return {"status": "ok"}


class PredictRequest(BaseModel):
    features: Dict[str, Any]


class PredictResponse(BaseModel):
    prediction: Dict[str, Any]


@router.post("/predict", response_model=PredictResponse)
async def predict(payload: PredictRequest):
    """Endpoint de inferência (placeholder).
    Espera um objeto `features` com chaves/valores que representam as features do modelo.
    """
    from app.services.predict import predict_from_features

    result = await predict_from_features(payload.features)
    return {"prediction": result}
