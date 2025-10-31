import asyncio
from typing import Dict, Any

try:
    import joblib
except Exception:
    joblib = None

from app.core.config import settings


_MODEL = None


async def _load_model():
    global _MODEL
    if _MODEL is None:
        # Placeholder: if you use joblib, load the model here
        if joblib:
            try:
                _MODEL = joblib.load(settings.MODEL_PATH)
            except Exception:
                _MODEL = None
        else:
            _MODEL = None

    return _MODEL


async def predict_from_features(features: Dict[str, Any]) -> Dict[str, Any]:
    """Inferência mínima. Atualmente devolve um placeholder.

    Substituir pela lógica de preprocess -> modelo -> postprocess.
    """
    model = await _load_model()
    await asyncio.sleep(0)  # yield control

    if model is None:
        # return a deterministic placeholder while model is not available
        return {"placeholder": True, "raw_features": features}

    # Exemplo (depende do formato do modelo):
    try:
        X = [list(features.values())]
        y = model.predict(X)
        return {"prediction": y[0]}
    except Exception as e:
        return {"error": str(e)}
