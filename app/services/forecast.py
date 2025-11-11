"""
Forecast Service - Load and use trained forecasting models.

This module:
- Loads per-province forecast models from disk (lazy loading with cache)
- Provides prediction functions for the API
- Handles model fallback if a model is not available
"""

import os
from pathlib import Path
from typing import Optional, Dict, Tuple
import json
import numpy as np
import joblib
from datetime import datetime


MODEL_DIR = Path("models")


class ForecastService:
    """Singleton service to manage forecast models."""
    
    def __init__(self):
        self._models: Dict[str, any] = {}
        self._metrics: Dict[str, dict] = {}
        
    def _normalize_province(self, province: str) -> str:
        """Normalize province name to match file naming."""
        return province.replace(' ', '_')
    
    def _load_model(self, province: str) -> Optional[any]:
        """Load model from disk if not already cached."""
        normalized = self._normalize_province(province)
        
        if normalized in self._models:
            return self._models[normalized]
        
        model_path = MODEL_DIR / f"forecast_{normalized}.joblib"
        metrics_path = MODEL_DIR / f"metrics_{normalized}.json"
        
        if not model_path.exists():
            return None
        
        try:
            model = joblib.load(model_path)
            self._models[normalized] = model
            
            # Load metrics if available
            if metrics_path.exists():
                with open(metrics_path, 'r') as f:
                    self._metrics[normalized] = json.load(f)
            
            return model
        except Exception as e:
            print(f"Error loading model for {province}: {e}")
            return None
    
    def get_model_info(self, province: str) -> Optional[dict]:
        """Get model metadata and metrics."""
        normalized = self._normalize_province(province)
        model = self._load_model(province)
        
        if not model:
            return None
        
        return {
            'province': province,
            'model_path': str(MODEL_DIR / f"forecast_{normalized}.joblib"),
            'metrics': self._metrics.get(normalized, {}),
            'loaded': True
        }
    
    def list_available_models(self) -> list:
        """List all available trained models."""
        if not MODEL_DIR.exists():
            return []
        
        models = []
        for model_file in MODEL_DIR.glob("forecast_*.joblib"):
            province = model_file.stem.replace('forecast_', '').replace('_', ' ')
            info = self.get_model_info(province)
            if info:
                models.append(info)
        
        return models
    
    def predict(
        self, 
        province: str, 
        year: int, 
        month: int,
        occupancy_rate: float = 0.0,
        avg_stay_days: float = 0.0
    ) -> Optional[Dict]:
        """
        Predict visitors for a given province/month/year.
        
        Returns:
            dict with keys: predicted_visitors, confidence_interval (lower, upper)
            or None if model not available
        """
        model = self._load_model(province)
        
        if not model:
            return None
        
        # Prepare features (same as training)
        month_sin = np.sin(2 * np.pi * month / 12)
        month_cos = np.cos(2 * np.pi * month / 12)
        
        X = np.array([[year, month_sin, month_cos, occupancy_rate, avg_stay_days]])
        
        # Predict
        prediction = model.predict(X)[0]
        
        # Confidence interval estimation (simple approach using RF prediction variance)
        # For RandomForest, we can use individual tree predictions
        if hasattr(model, 'estimators_'):
            tree_predictions = np.array([tree.predict(X)[0] for tree in model.estimators_])
            std = np.std(tree_predictions)
            lower = max(0, prediction - 1.96 * std)
            upper = prediction + 1.96 * std
        else:
            # Fallback: use 20% margin
            margin = prediction * 0.2
            lower = max(0, prediction - margin)
            upper = prediction + margin
        
        return {
            'predicted_visitors': int(round(prediction)),
            'confidence_interval': {
                'lower': int(round(lower)),
                'upper': int(round(upper))
            }
        }


# Global singleton instance
_forecast_service = ForecastService()


def get_forecast_service() -> ForecastService:
    """Get the singleton forecast service instance."""
    return _forecast_service
