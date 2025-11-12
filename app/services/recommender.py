"""
Recommender Service - Load and use trained recommendation model.

This module:
- Loads content-based recommendation model from disk
- Provides similar destination recommendations
- Provides personalized recommendations based on user preferences
"""

import json
from pathlib import Path
from typing import Optional, List, Dict
import numpy as np
import joblib


MODEL_DIR = Path("models")


class RecommenderService:
    """Singleton service to manage recommendation model."""
    
    def __init__(self):
        self._similarity_matrix: Optional[np.ndarray] = None
        self._features: Optional[np.ndarray] = None
        self._tfidf: Optional[any] = None
        self._scaler: Optional[any] = None
        self._metadata: Optional[dict] = None
        self._loaded = False
        
    def _load_model(self):
        """Load model from disk if not already loaded."""
        if self._loaded:
            return
        
        sim_path = MODEL_DIR / "recommender_similarity_matrix.npy"
        features_path = MODEL_DIR / "recommender_features.npy"
        tfidf_path = MODEL_DIR / "recommender_tfidf.joblib"
        scaler_path = MODEL_DIR / "recommender_scaler.joblib"
        metadata_path = MODEL_DIR / "recommender_metadata.json"
        
        if not sim_path.exists() or not metadata_path.exists():
            print("Recommendation model not found. Run train_recommender.py first.")
            return
        
        try:
            self._similarity_matrix = np.load(sim_path)
            self._features = np.load(features_path)
            self._tfidf = joblib.load(tfidf_path)
            self._scaler = joblib.load(scaler_path)
            
            with open(metadata_path, 'r') as f:
                self._metadata = json.load(f)
            
            self._loaded = True
        except Exception as e:
            print(f"Error loading recommendation model: {e}")
    
    def get_model_info(self) -> Optional[Dict]:
        """Get recommendation model metadata."""
        self._load_model()
        
        if not self._loaded or not self._metadata:
            return None
        
        return {
            'n_destinations': self._metadata.get('n_destinations'),
            'feature_dim': self._metadata.get('feature_dim'),
            'categories': self._metadata.get('categories'),
            'provinces': self._metadata.get('provinces'),
            'loaded': True
        }
    
    def _get_destination_index(self, destination_id: str) -> Optional[int]:
        """Get array index for a destination ID."""
        if not self._metadata:
            return None
        
        destinations = self._metadata.get('destinations', [])
        for idx, dest in enumerate(destinations):
            if dest['id'] == destination_id:
                return idx
        return None
    
    def recommend_similar(
        self,
        destination_id: str,
        n_recommendations: int = 10
    ) -> Optional[List[Dict]]:
        """
        Recommend destinations similar to a given destination.
        
        Args:
            destination_id: UUID of the destination
            n_recommendations: number of recommendations to return
            
        Returns:
            List of recommended destinations with similarity scores
        """
        self._load_model()
        
        if not self._loaded or self._similarity_matrix is None:
            return None
        
        # Get index of the destination
        dest_idx = self._get_destination_index(destination_id)
        if dest_idx is None:
            return None
        
        # Get similarity scores
        sim_scores = self._similarity_matrix[dest_idx]
        
        # Sort by similarity (excluding self)
        similar_indices = np.argsort(sim_scores)[::-1]
        similar_indices = [idx for idx in similar_indices if idx != dest_idx]
        
        # Get top N
        top_indices = similar_indices[:n_recommendations]
        
        # Build recommendations
        recommendations = []
        destinations = self._metadata.get('destinations', [])
        
        for idx in top_indices:
            if idx < len(destinations):
                dest = destinations[idx]
                recommendations.append({
                    'destination_id': dest['id'],
                    'name': dest['name'],
                    'province': dest['province'],
                    'category': dest.get('category', dest.get('category_id')),
                    'rating': dest.get('rating', dest.get('rating_avg')),
                    'similarity_score': float(sim_scores[idx])
                })
        
        return recommendations
    
    def recommend_by_preferences(
        self,
        categories: Optional[List[str]] = None,
        provinces: Optional[List[str]] = None,
        min_rating: Optional[float] = None,
        n_recommendations: int = 10
    ) -> Optional[List[Dict]]:
        """
        Recommend destinations based on user preferences.
        
        Args:
            categories: list of preferred categories
            provinces: list of preferred provinces
            min_rating: minimum rating threshold
            n_recommendations: number of recommendations
            
        Returns:
            List of recommended destinations with scores
        """
        self._load_model()
        
        if not self._loaded or not self._metadata:
            return None
        
        destinations = self._metadata.get('destinations', [])
        
        # Filter by preferences
        filtered = []
        for dest in destinations:
            # Check category (support both old and new field names)
            dest_category = dest.get('category', dest.get('category_id'))
            if categories and dest_category not in categories:
                continue
            
            # Check province
            if provinces and dest['province'] not in provinces:
                continue
            
            # Check rating (support both old and new field names)
            dest_rating = dest.get('rating', dest.get('rating_avg', 0))
            if min_rating and dest_rating < min_rating:
                continue
            
            filtered.append(dest)
        
        # Sort by rating (descending)
        filtered.sort(key=lambda x: x.get('rating', x.get('rating_avg', 0)), reverse=True)
        
        # Take top N
        top_recommendations = filtered[:n_recommendations]
        
        # Calculate scores (normalized rating)
        max_rating = 5.0
        recommendations = []
        for dest in top_recommendations:
            dest_rating = dest.get('rating', dest.get('rating_avg', 3.5))
            score = dest_rating / max_rating
            recommendations.append({
                'destination_id': dest['id'],
                'name': dest['name'],
                'province': dest['province'],
                'category': dest.get('category', dest.get('category_id')),
                'rating': dest_rating,
                'score': round(score, 2)
            })
        
        return recommendations
    
    def recommend_hybrid(
        self,
        categories: Optional[List[str]] = None,
        provinces: Optional[List[str]] = None,
        similar_to: Optional[str] = None,
        n_recommendations: int = 10
    ) -> Optional[List[Dict]]:
        """
        Hybrid recommendation: combines content-based and preference filtering.
        
        If similar_to is provided, finds similar destinations within the filtered set.
        Otherwise, returns top-rated destinations in the filtered set.
        """
        self._load_model()
        
        if not self._loaded:
            return None
        
        # First filter by preferences
        filtered = self.recommend_by_preferences(
            categories=categories,
            provinces=provinces,
            min_rating=None,  # No rating filter for hybrid
            n_recommendations=50  # Get larger set for similarity filtering
        )
        
        if not filtered:
            return None
        
        # If similar_to provided, re-rank by similarity
        if similar_to:
            dest_idx = self._get_destination_index(similar_to)
            if dest_idx is not None and self._similarity_matrix is not None:
                sim_scores = self._similarity_matrix[dest_idx]
                
                # Add similarity scores to filtered results
                for rec in filtered:
                    rec_idx = self._get_destination_index(rec['destination_id'])
                    if rec_idx is not None:
                        rec['similarity_score'] = float(sim_scores[rec_idx])
                    else:
                        rec['similarity_score'] = 0.0
                
                # Sort by similarity
                filtered.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        
        return filtered[:n_recommendations]


# Global singleton instance
_recommender_service = RecommenderService()


def get_recommender_service() -> RecommenderService:
    """Get the singleton recommender service instance."""
    return _recommender_service
