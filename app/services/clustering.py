"""
Clustering Service - Load and use trained tourist segmentation model.

This module:
- Loads K-Means clustering model from disk
- Provides segment information from metadata
- Can predict segment for new user based on preferences
"""

import json
from pathlib import Path
from typing import Optional, List, Dict
import numpy as np
import joblib


MODEL_DIR = Path("models")


class ClusteringService:
    """Singleton service to manage clustering model."""
    
    def __init__(self):
        self._model: Optional[any] = None
        self._scaler: Optional[any] = None
        self._metadata: Optional[dict] = None
        self._loaded = False
        
    def _load_model(self):
        """Load model from disk if not already loaded."""
        if self._loaded:
            return
        
        model_path = MODEL_DIR / "clustering_kmeans.joblib"
        scaler_path = MODEL_DIR / "clustering_scaler.joblib"
        metadata_path = MODEL_DIR / "clustering_metadata.json"
        
        if not model_path.exists() or not metadata_path.exists():
            print("Clustering model not found. Run train_clustering.py first.")
            return
        
        try:
            self._model = joblib.load(model_path)
            self._scaler = joblib.load(scaler_path)
            
            with open(metadata_path, 'r') as f:
                self._metadata = json.load(f)
            
            self._loaded = True
        except Exception as e:
            print(f"Error loading clustering model: {e}")
    
    def get_segments(self) -> Optional[List[Dict]]:
        """Get all tourist segments with their profiles."""
        self._load_model()
        
        if not self._loaded or not self._metadata:
            return None
        
        return self._metadata.get('cluster_profiles', [])
    
    def get_model_info(self) -> Optional[Dict]:
        """Get clustering model metadata."""
        self._load_model()
        
        if not self._loaded or not self._metadata:
            return None
        
        return {
            'n_clusters': self._metadata.get('n_clusters'),
            'silhouette_score': self._metadata.get('silhouette_score'),
            'n_samples': self._metadata.get('n_samples'),
            'loaded': True
        }
    
    def predict_segment(
        self,
        budget: int = 2,  # 1=low, 2=medium, 3=high
        trip_duration: float = 7.0,
        beach_pref: float = 0.5,
        culture_pref: float = 0.5,
        nature_pref: float = 0.5,
        adventure_pref: float = 0.5,
        gastronomy_pref: float = 0.5,
        trips_per_year: int = 2,
        group_size: int = 2
    ) -> Optional[Dict]:
        """
        Predict which segment a user belongs to based on preferences.
        
        Args:
            budget: 1 (low), 2 (medium), or 3 (high)
            trip_duration: average days per trip
            beach_pref: preference for beach destinations (0-1)
            culture_pref: preference for cultural destinations (0-1)
            nature_pref: preference for nature/ecotourism (0-1)
            adventure_pref: preference for adventure activities (0-1)
            gastronomy_pref: preference for gastronomy experiences (0-1)
            trips_per_year: number of trips per year
            group_size: typical group size
            
        Returns:
            Dictionary with segment information
        """
        self._load_model()
        
        if not self._loaded or self._model is None:
            return None
        
        # Prepare features (same order as training)
        features = np.array([[
            budget, trip_duration, beach_pref, culture_pref,
            nature_pref, adventure_pref, gastronomy_pref,
            trips_per_year, group_size
        ]])
        
        # Scale features
        features_scaled = self._scaler.transform(features)
        
        # Predict cluster
        cluster_id = int(self._model.predict(features_scaled)[0])
        
        # Get cluster profile
        cluster_profiles = self._metadata.get('cluster_profiles', [])
        segment = next((p for p in cluster_profiles if p['cluster_id'] == cluster_id), None)
        
        if not segment:
            return None
        
        # Calculate similarity/confidence (distance to cluster center)
        distance = float(np.linalg.norm(features_scaled - self._model.cluster_centers_[cluster_id]))
        confidence = max(0, 1 - (distance / 3))  # Normalize to 0-1
        
        return {
            'segment': segment,
            'confidence': round(confidence, 2)
        }


# Global singleton instance
_clustering_service = ClusteringService()


def get_clustering_service() -> ClusteringService:
    """Get the singleton clustering service instance."""
    return _clustering_service
