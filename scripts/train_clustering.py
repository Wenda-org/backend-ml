"""
Train tourist clustering model using K-Means.

This script creates tourist segments based on behavioral patterns.
Since we have limited real user data, we generate synthetic data based on
the tourist profiles defined in docs/perfis-viajantes-wenda.md

Features used:
- Budget preference (low=1, medium=2, high=3)
- Trip duration (days)
- Activity preferences (beach, culture, nature, adventure, gastronomy)
- Travel frequency (trips per year)
- Group size (solo, couple, family, group)

Usage:
    export DATABASE_URL="postgresql://..."
    python3 scripts/train_clustering.py
"""

import asyncio
import os
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import joblib
import asyncpg


MODEL_DIR = Path("models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def normalize_database_url(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://")
    return url


async def fetch_real_users(database_url: str) -> pd.DataFrame:
    """Fetch real users from database (when available)."""
    database_url = normalize_database_url(database_url)
    conn = await asyncpg.connect(database_url, ssl='require')
    
    rows = await conn.fetch("SELECT id, name, email, role, country FROM users WHERE role = 'tourist'")
    await conn.close()
    
    return pd.DataFrame([dict(r) for r in rows])


def generate_synthetic_tourist_data(n_samples=500):
    """
    Generate synthetic tourist data based on documented profiles:
    1. Relaxante Tradicional (35%)
    2. Aventureiro Explorador (25%)
    3. Cultural Urbano (20%)
    4. Negócios & Lazer (15%)
    5. Ecoturista Consciente (5%)
    """
    np.random.seed(42)
    
    profiles = []
    
    # Profile 1: Relaxante Tradicional (35%)
    n1 = int(n_samples * 0.35)
    for _ in range(n1):
        profiles.append({
            'profile_type': 'relaxante_tradicional',
            'budget': np.random.choice([2, 3], p=[0.7, 0.3]),  # medium-high
            'trip_duration': np.random.normal(6, 1.5),  # 5-7 days
            'beach_preference': np.random.uniform(0.8, 1.0),
            'culture_preference': np.random.uniform(0.3, 0.6),
            'nature_preference': np.random.uniform(0.4, 0.7),
            'adventure_preference': np.random.uniform(0.1, 0.4),
            'gastronomy_preference': np.random.uniform(0.5, 0.8),
            'trips_per_year': np.random.choice([1, 2], p=[0.6, 0.4]),
            'group_size': np.random.choice([2, 3, 4], p=[0.5, 0.3, 0.2]),  # couple/family
        })
    
    # Profile 2: Aventureiro Explorador (25%)
    n2 = int(n_samples * 0.25)
    for _ in range(n2):
        profiles.append({
            'profile_type': 'aventureiro_explorador',
            'budget': np.random.choice([2, 3], p=[0.5, 0.5]),
            'trip_duration': np.random.normal(10, 2),  # 7-14 days
            'beach_preference': np.random.uniform(0.3, 0.6),
            'culture_preference': np.random.uniform(0.4, 0.7),
            'nature_preference': np.random.uniform(0.8, 1.0),
            'adventure_preference': np.random.uniform(0.8, 1.0),
            'gastronomy_preference': np.random.uniform(0.6, 0.9),
            'trips_per_year': np.random.choice([2, 3, 4], p=[0.5, 0.3, 0.2]),
            'group_size': np.random.choice([1, 2, 4], p=[0.3, 0.4, 0.3]),  # solo/couple/group
        })
    
    # Profile 3: Cultural Urbano (20%)
    n3 = int(n_samples * 0.20)
    for _ in range(n3):
        profiles.append({
            'profile_type': 'cultural_urbano',
            'budget': np.random.choice([2, 3], p=[0.6, 0.4]),
            'trip_duration': np.random.normal(5, 1),  # 3-5 days
            'beach_preference': np.random.uniform(0.2, 0.5),
            'culture_preference': np.random.uniform(0.8, 1.0),
            'nature_preference': np.random.uniform(0.3, 0.6),
            'adventure_preference': np.random.uniform(0.2, 0.5),
            'gastronomy_preference': np.random.uniform(0.7, 1.0),
            'trips_per_year': np.random.choice([2, 3, 4], p=[0.4, 0.4, 0.2]),
            'group_size': np.random.choice([1, 2], p=[0.4, 0.6]),  # solo/couple
        })
    
    # Profile 4: Negócios & Lazer (15%)
    n4 = int(n_samples * 0.15)
    for _ in range(n4):
        profiles.append({
            'profile_type': 'negocios_lazer',
            'budget': 3,  # high
            'trip_duration': np.random.normal(4, 1),  # 3-5 days
            'beach_preference': np.random.uniform(0.5, 0.8),
            'culture_preference': np.random.uniform(0.6, 0.9),
            'nature_preference': np.random.uniform(0.3, 0.6),
            'adventure_preference': np.random.uniform(0.2, 0.5),
            'gastronomy_preference': np.random.uniform(0.7, 1.0),
            'trips_per_year': np.random.choice([4, 6, 8], p=[0.5, 0.3, 0.2]),
            'group_size': np.random.choice([1, 2], p=[0.7, 0.3]),  # mostly solo
        })
    
    # Profile 5: Ecoturista Consciente (5%)
    n5 = n_samples - (n1 + n2 + n3 + n4)
    for _ in range(n5):
        profiles.append({
            'profile_type': 'ecoturista',
            'budget': np.random.choice([2, 3], p=[0.4, 0.6]),
            'trip_duration': np.random.normal(10, 2),  # 7-14 days
            'beach_preference': np.random.uniform(0.2, 0.5),
            'culture_preference': np.random.uniform(0.5, 0.8),
            'nature_preference': np.random.uniform(0.9, 1.0),
            'adventure_preference': np.random.uniform(0.7, 1.0),
            'gastronomy_preference': np.random.uniform(0.6, 0.9),
            'trips_per_year': np.random.choice([1, 2], p=[0.6, 0.4]),
            'group_size': np.random.choice([2, 4, 6], p=[0.3, 0.5, 0.2]),  # groups
        })
    
    df = pd.DataFrame(profiles)
    
    # Clip values
    df['trip_duration'] = df['trip_duration'].clip(lower=1)
    df['group_size'] = df['group_size'].clip(lower=1)
    
    return df


def train_clustering_model(df: pd.DataFrame, n_clusters=5):
    """Train K-Means clustering model."""
    
    # Select features for clustering
    feature_cols = [
        'budget', 'trip_duration', 'beach_preference', 'culture_preference',
        'nature_preference', 'adventure_preference', 'gastronomy_preference',
        'trips_per_year', 'group_size'
    ]
    
    X = df[feature_cols].values
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train K-Means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=20)
    labels = kmeans.fit_predict(X_scaled)
    
    # Calculate silhouette score (quality metric)
    silhouette = silhouette_score(X_scaled, labels)
    
    # Add cluster labels to dataframe
    df['cluster'] = labels
    
    return kmeans, scaler, silhouette, df


def analyze_clusters(df: pd.DataFrame):
    """Analyze and name clusters based on characteristics."""
    
    cluster_profiles = []
    
    for cluster_id in sorted(df['cluster'].unique()):
        cluster_data = df[df['cluster'] == cluster_id]
        
        profile = {
            'cluster_id': int(cluster_id),
            'size': len(cluster_data),
            'percentage': round(len(cluster_data) / len(df) * 100, 1),
            'characteristics': {
                'avg_budget': round(cluster_data['budget'].mean(), 2),
                'avg_trip_duration': round(cluster_data['trip_duration'].mean(), 1),
                'avg_group_size': round(cluster_data['group_size'].mean(), 1),
                'trips_per_year': round(cluster_data['trips_per_year'].mean(), 1),
                'preferences': {
                    'beach': round(cluster_data['beach_preference'].mean(), 2),
                    'culture': round(cluster_data['culture_preference'].mean(), 2),
                    'nature': round(cluster_data['nature_preference'].mean(), 2),
                    'adventure': round(cluster_data['adventure_preference'].mean(), 2),
                    'gastronomy': round(cluster_data['gastronomy_preference'].mean(), 2),
                }
            },
            'top_profile_types': cluster_data['profile_type'].value_counts().head(3).to_dict()
        }
        
        # Determine segment name based on dominant characteristics
        prefs = profile['characteristics']['preferences']
        top_pref = max(prefs, key=prefs.get)
        
        if top_pref == 'beach' and profile['characteristics']['avg_budget'] >= 2:
            name = "Relaxante Tradicional"
        elif top_pref == 'adventure' or top_pref == 'nature':
            name = "Aventureiro Explorador"
        elif top_pref == 'culture':
            name = "Cultural Urbano"
        elif profile['characteristics']['trips_per_year'] >= 4:
            name = "Negócios & Lazer"
        else:
            name = "Ecoturista Consciente"
        
        profile['name'] = name
        profile['description'] = generate_description(profile)
        
        cluster_profiles.append(profile)
    
    return cluster_profiles


def generate_description(profile: dict) -> str:
    """Generate natural language description of cluster."""
    chars = profile['characteristics']
    budget_map = {1: 'low', 2: 'medium', 3: 'high'}
    budget = budget_map.get(round(chars['avg_budget']), 'medium')
    
    prefs = chars['preferences']
    top_prefs = sorted(prefs.items(), key=lambda x: x[1], reverse=True)[:2]
    pref_str = f"{top_prefs[0][0]} and {top_prefs[1][0]}"
    
    return (f"Travelers with {budget} budget, typically staying {chars['avg_trip_duration']:.0f} days. "
            f"Strong preference for {pref_str}. "
            f"Travel {chars['trips_per_year']:.0f} times per year in groups of {chars['avg_group_size']:.0f}.")


async def main():
    print("🎯 CLUSTERING DE TURISTAS - Wenda ML Backend")
    print("=" * 80)
    
    # Generate synthetic data
    print("\n📊 Generating synthetic tourist data...")
    df = generate_synthetic_tourist_data(n_samples=500)
    print(f"✅ Generated {len(df)} synthetic tourist profiles")
    
    # Train clustering model
    print("\n🔧 Training K-Means clustering model...")
    n_clusters = 5  # Based on our documented profiles
    kmeans, scaler, silhouette, df_with_clusters = train_clustering_model(df, n_clusters)
    print(f"✅ Model trained with {n_clusters} clusters")
    print(f"   Silhouette score: {silhouette:.3f} (quality metric: >0.5 is good)")
    
    # Analyze clusters
    print("\n📈 Analyzing clusters...")
    cluster_profiles = analyze_clusters(df_with_clusters)
    
    # Display results
    print("\n" + "=" * 80)
    print("CLUSTER PROFILES")
    print("=" * 80)
    for profile in cluster_profiles:
        print(f"\n🏷️  Cluster {profile['cluster_id']}: {profile['name']}")
        print(f"   Size: {profile['size']} tourists ({profile['percentage']}%)")
        print(f"   Budget: {profile['characteristics']['avg_budget']:.1f}/3")
        print(f"   Avg trip: {profile['characteristics']['avg_trip_duration']:.0f} days")
        print(f"   Group size: {profile['characteristics']['avg_group_size']:.0f} people")
        print(f"   Frequency: {profile['characteristics']['trips_per_year']:.1f} trips/year")
        print(f"   Top preferences:")
        for pref, score in profile['characteristics']['preferences'].items():
            print(f"      {pref}: {score:.2f}")
    
    # Save model and metadata
    print("\n💾 Saving model and metadata...")
    
    model_path = MODEL_DIR / "clustering_kmeans.joblib"
    scaler_path = MODEL_DIR / "clustering_scaler.joblib"
    metadata_path = MODEL_DIR / "clustering_metadata.json"
    
    joblib.dump(kmeans, model_path)
    joblib.dump(scaler, scaler_path)
    
    metadata = {
        'n_clusters': n_clusters,
        'silhouette_score': float(silhouette),
        'n_samples': len(df),
        'feature_cols': [
            'budget', 'trip_duration', 'beach_preference', 'culture_preference',
            'nature_preference', 'adventure_preference', 'gastronomy_preference',
            'trips_per_year', 'group_size'
        ],
        'cluster_profiles': cluster_profiles
    }
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"   ✅ Model: {model_path}")
    print(f"   ✅ Scaler: {scaler_path}")
    print(f"   ✅ Metadata: {metadata_path}")
    
    print("\n✅ Clustering model training complete!")


if __name__ == '__main__':
    asyncio.run(main())
