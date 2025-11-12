"""
Train content-based recommendation model using TF-IDF + Cosine Similarity.

This script creates a recommender system based on destination features:
- Category (beach, culture, nature, adventure, gastronomy)
- Province
- Description (text features via TF-IDF)
- Rating

The model can recommend similar destinations or personalized recommendations
based on user preferences.

Usage:
    export DATABASE_URL="postgresql://..."
    python3 scripts/train_recommender.py
"""

import asyncio
import os
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import joblib
import asyncpg


MODEL_DIR = Path("models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def normalize_database_url(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://")
    return url


async def fetch_destinations(database_url: str) -> pd.DataFrame:
    """Fetch all destinations from database."""
    database_url = normalize_database_url(database_url)
    conn = await asyncpg.connect(database_url, ssl='require')
    
    rows = await conn.fetch(
        """
        SELECT d.id, d.name, d.province, c.slug as category, d.description, 
               CAST(d.rating AS FLOAT) as rating
        FROM destinations d
        LEFT JOIN categories c ON d.category_id = c.id
        WHERE d.is_active = true AND d.deleted_at IS NULL
        """
    )
    await conn.close()
    
    records = [dict(r) for r in rows]
    df = pd.DataFrame(records)
    
    # Check if we have data
    if df.empty:
        print("⚠️  WARNING: No destinations found in database!")
        print("    Please populate the database with destinations first.")
        print("    Run: python scripts/populate_database.py")
        return df
    
    # Convert UUID to string
    df['id'] = df['id'].astype(str)
    
    # Fill missing values
    df['description'] = df['description'].fillna('')
    df['rating'] = df['rating'].fillna(3.5)
    df['category'] = df['category'].fillna('other')
    
    return df


def create_content_features(df: pd.DataFrame):
    """
    Create content-based features for destinations.
    
    Features:
    1. TF-IDF on description text
    2. One-hot encoded category
    3. One-hot encoded province
    4. Normalized rating
    """
    
    # 1. TF-IDF on descriptions
    tfidf = TfidfVectorizer(
        max_features=50,  # Limit features for small dataset
        stop_words='english',
        ngram_range=(1, 2)  # Unigrams and bigrams
    )
    
    # Create combined text: description + category + province (for better similarity)
    df['combined_text'] = (
        df['description'] + ' ' +
        df['category'] + ' ' +
        df['category'] + ' ' +  # Weight category more
        df['province']
    )
    
    tfidf_matrix = tfidf.fit_transform(df['combined_text'])
    
    # 2. Category one-hot encoding (manual for better control)
    categories = df['category'].unique()
    category_features = np.zeros((len(df), len(categories)))
    for i, cat in enumerate(categories):
        category_features[:, i] = (df['category'] == cat).astype(int)
    
    # 3. Province one-hot encoding
    provinces = df['province'].unique()
    province_features = np.zeros((len(df), len(provinces)))
    for i, prov in enumerate(provinces):
        province_features[:, i] = (df['province'] == prov).astype(int)
    
    # 4. Normalized rating
    scaler = MinMaxScaler()
    rating_features = scaler.fit_transform(df[['rating']])
    
    # Combine all features
    # Weight: TF-IDF (0.4) + Category (0.3) + Province (0.2) + Rating (0.1)
    tfidf_dense = tfidf_matrix.toarray()
    
    # Normalize TF-IDF to 0-1 range for weighting
    if tfidf_dense.max() > 0:
        tfidf_normalized = tfidf_dense / tfidf_dense.max()
    else:
        tfidf_normalized = tfidf_dense
    
    combined_features = np.hstack([
        tfidf_normalized * 0.4,
        category_features * 0.3,
        province_features * 0.2,
        rating_features * 0.1
    ])
    
    return combined_features, tfidf, scaler, list(categories), list(provinces)


def compute_similarity_matrix(features: np.ndarray):
    """Compute cosine similarity matrix between all destinations."""
    return cosine_similarity(features)


def get_top_similar_destinations(
    similarity_matrix: np.ndarray,
    destination_idx: int,
    n_recommendations: int = 5
):
    """Get top N similar destinations for a given destination."""
    # Get similarity scores for this destination
    sim_scores = similarity_matrix[destination_idx]
    
    # Sort by similarity (excluding self)
    similar_indices = np.argsort(sim_scores)[::-1]
    
    # Remove self (index 0 will be the destination itself with score 1.0)
    similar_indices = [idx for idx in similar_indices if idx != destination_idx]
    
    # Get top N
    top_indices = similar_indices[:n_recommendations]
    top_scores = sim_scores[top_indices]
    
    return list(zip(top_indices, top_scores))


def recommend_by_preferences(
    df: pd.DataFrame,
    features: np.ndarray,
    categories: list,
    provinces: list,
    user_preferences: dict
):
    """
    Recommend destinations based on user preferences.
    
    Args:
        user_preferences: dict with keys like:
            - categories: list of preferred categories
            - provinces: list of preferred provinces
            - min_rating: minimum rating
    """
    # Filter by preferences
    mask = np.ones(len(df), dtype=bool)
    
    if 'categories' in user_preferences and user_preferences['categories']:
        cat_mask = df['category'].isin(user_preferences['categories'])
        mask &= cat_mask
    
    if 'provinces' in user_preferences and user_preferences['provinces']:
        prov_mask = df['province'].isin(user_preferences['provinces'])
        mask &= prov_mask
    
    if 'min_rating' in user_preferences:
        rating_mask = df['rating'] >= user_preferences['min_rating']
        mask &= rating_mask
    
    # Get filtered destinations
    filtered_df = df[mask]
    
    if len(filtered_df) == 0:
        return []
    
    # Sort by rating (descending)
    filtered_df = filtered_df.sort_values('rating', ascending=False)
    
    return filtered_df.head(10).index.tolist()


async def main():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        database_url = "postgresql://neondb_owner:npg_3aSeQW0qTPju@ep-cold-king-adyr1oj3-pooler.c-2.us-east-1.aws.neon.tech/neondb"
    
    print("🎯 SISTEMA DE RECOMENDAÇÃO - Wenda ML Backend")
    print("=" * 80)
    
    # Fetch destinations
    print("\n📥 Loading destinations from database...")
    df = await fetch_destinations(database_url)
    
    if df.empty:
        print("\n❌ TRAINING ABORTED: No destinations found in database")
        print("\n💡 Next steps:")
        print("   1. Populate database: python scripts/populate_database.py")
        print("   2. Try again: python scripts/train_recommender.py")
        return
    
    print(f"✅ Loaded {len(df)} destinations")
    
    # Create content features
    print("\n🔧 Creating content-based features...")
    features, tfidf, scaler, categories, provinces = create_content_features(df)
    print(f"✅ Created feature matrix: {features.shape}")
    print(f"   Categories: {categories}")
    print(f"   Provinces: {provinces}")
    
    # Compute similarity matrix
    print("\n📊 Computing destination similarity matrix...")
    similarity_matrix = compute_similarity_matrix(features)
    print(f"✅ Similarity matrix: {similarity_matrix.shape}")
    
    # Test: Get similar destinations for first few destinations
    print("\n" + "=" * 80)
    print("SAMPLE RECOMMENDATIONS (Similar Destinations)")
    print("=" * 80)
    for i in range(min(3, len(df))):
        dest_name = df.iloc[i]['name']
        dest_category = df.iloc[i]['category']
        
        similar = get_top_similar_destinations(similarity_matrix, i, n_recommendations=3)
        
        print(f"\n📍 {dest_name} ({dest_category})")
        print(f"   Similar destinations:")
        for idx, score in similar:
            similar_name = df.iloc[idx]['name']
            similar_cat = df.iloc[idx]['category']
            print(f"      - {similar_name} ({similar_cat}) - Score: {score:.3f}")
    
    # Save model components
    print("\n💾 Saving model components...")
    
    # Save artifacts
    np.save(MODEL_DIR / "recommender_similarity_matrix.npy", similarity_matrix)
    np.save(MODEL_DIR / "recommender_features.npy", features)
    joblib.dump(tfidf, MODEL_DIR / "recommender_tfidf.joblib")
    joblib.dump(scaler, MODEL_DIR / "recommender_scaler.joblib")
    
    # Save metadata including destination index
    metadata = {
        'n_destinations': len(df),
        'feature_dim': features.shape[1],
        'categories': categories,
        'provinces': provinces,
        'destinations': df[['id', 'name', 'province', 'category', 'rating']].to_dict('records')
    }
    
    with open(MODEL_DIR / "recommender_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"   ✅ Similarity matrix: {MODEL_DIR / 'recommender_similarity_matrix.npy'}")
    print(f"   ✅ Features: {MODEL_DIR / 'recommender_features.npy'}")
    print(f"   ✅ TF-IDF vectorizer: {MODEL_DIR / 'recommender_tfidf.joblib'}")
    print(f"   ✅ Scaler: {MODEL_DIR / 'recommender_scaler.joblib'}")
    print(f"   ✅ Metadata: {MODEL_DIR / 'recommender_metadata.json'}")
    
    print("\n✅ Recommendation model training complete!")
    print(f"\n📊 Model can recommend from {len(df)} destinations")
    print(f"   Categories covered: {', '.join(categories)}")
    print(f"   Provinces covered: {', '.join(provinces)}")


if __name__ == '__main__':
    asyncio.run(main())
