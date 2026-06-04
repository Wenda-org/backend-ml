from fastapi import Header, HTTPException, status
from app.core.config import settings

async def verify_ml_api_key(x_ml_api_key: str = Header(None, alias="X-ML-API-KEY")):
    """
    Security dependency to verify internal API key.
    Ensures only authorized internal components can make calls.
    """
    if not x_ml_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-ML-API-KEY header"
        )
    if x_ml_api_key != settings.ML_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid X-ML-API-KEY"
        )
    return x_ml_api_key
