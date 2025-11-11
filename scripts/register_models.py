"""
Register trained models in ml_models_registry table.

This script reads metadata from all trained models (forecast, clustering, recommender)
and registers them in the database for tracking and versioning.

Usage:
    export DATABASE_URL="postgresql://..."
    python3 scripts/register_models.py
"""

import asyncio
import os
import json
from pathlib import Path
from datetime import datetime
from uuid import uuid4

import asyncpg


MODEL_DIR = Path("models")
FORECAST_SUMMARY = MODEL_DIR / "training_summary.json"
CLUSTERING_METADATA = MODEL_DIR / "clustering_metadata.json"
RECOMMENDER_METADATA = MODEL_DIR / "recommender_metadata.json"


def normalize_database_url(url: str) -> str:
    """Adapt neon URL to asyncpg connect usage."""
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://")
    return url


async def register_forecast_models(conn, summary):
    """Register forecast models from training_summary.json"""
    registered = 0
    
    for model_info in summary:
        province = model_info['province']
        metrics = model_info['metrics']
        version = "v1.0.0-rf-trained"
        
        # Check if model already registered
        existing = await conn.fetchrow(
            "SELECT id FROM ml_models_registry WHERE model_name = $1 AND version = $2",
            f"forecast_{province}",
            version
        )
        
        if existing:
            print(f"   ⏭️  Forecast {province} already registered (id: {existing['id']})")
            continue
        
        # Insert into registry
        await conn.execute(
            """
            INSERT INTO ml_models_registry 
            (model_name, version, algorithm, metrics, status, trained_on, last_updated)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            f"forecast_{province}",
            version,
            "RandomForestRegressor",
            json.dumps(metrics),
            "active",
            datetime.utcnow().date(),
            datetime.utcnow()
        )
        
        registered += 1
        mae = metrics.get('mae', 'N/A')
        mape = metrics.get('mape', 'N/A')
        print(f"   ✅ Forecast {province}: MAE={mae}, MAPE={mape}%")
    
    return registered


async def register_clustering_model(conn, metadata):
    """Register clustering model from clustering_metadata.json"""
    version = "v1.0.0-kmeans"
    
    # Check if model already registered
    existing = await conn.fetchrow(
        "SELECT id FROM ml_models_registry WHERE model_name = $1 AND version = $2",
        "clustering_kmeans",
        version
    )
    
    if existing:
        print(f"   ⏭️  Clustering already registered (id: {existing['id']})")
        return 0
    
    # Extract metrics from metadata
    metrics = {
        "n_clusters": metadata.get("n_clusters"),
        "silhouette_score": metadata.get("silhouette_score"),
        "n_samples": metadata.get("n_samples"),
        "features": metadata.get("features")
    }
    
    # Insert into registry
    await conn.execute(
        """
        INSERT INTO ml_models_registry 
        (model_name, version, algorithm, metrics, status, trained_on, last_updated)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
        "clustering_kmeans",
        version,
        "KMeans",
        json.dumps(metrics),
        "active",
        datetime.utcnow().date(),
        datetime.utcnow()
    )
    
    print(f"   ✅ Clustering: {metadata['n_clusters']} clusters, silhouette={metadata.get('silhouette_score', 'N/A')}")
    return 1


async def register_recommender_model(conn, metadata):
    """Register recommender model from recommender_metadata.json"""
    version = "v1.0.0-content"
    
    # Check if model already registered
    existing = await conn.fetchrow(
        "SELECT id FROM ml_models_registry WHERE model_name = $1 AND version = $2",
        "recommender_content_based",
        version
    )
    
    if existing:
        print(f"   ⏭️  Recommender already registered (id: {existing['id']})")
        return 0
    
    # Extract metrics from metadata
    metrics = {
        "n_destinations": metadata.get("n_destinations"),
        "feature_dim": metadata.get("feature_dim"),
        "categories": metadata.get("categories", []),
        "provinces": metadata.get("provinces", []),
        "similarity_metric": "cosine"
    }
    
    # Insert into registry
    await conn.execute(
        """
        INSERT INTO ml_models_registry 
        (model_name, version, algorithm, metrics, status, trained_on, last_updated)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
        "recommender_content_based",
        version,
        "TF-IDF + Cosine",
        json.dumps(metrics),
        "active",
        datetime.utcnow().date(),
        datetime.utcnow()
    )
    
    print(f"   ✅ Recommender: {metadata['n_destinations']} destinations, content-based filtering")
    return 1


async def register_models(database_url: str):
    """Register all trained models in the ml_models_registry table."""
    
    database_url = normalize_database_url(database_url)
    conn = await asyncpg.connect(database_url, ssl='require')
    
    total_registered = 0
    
    # 1. Register Forecast Models
    if FORECAST_SUMMARY.exists():
        print(f"\n📊 Registering Forecast models...")
        with open(FORECAST_SUMMARY, 'r') as f:
            summary = json.load(f)
        total_registered += await register_forecast_models(conn, summary)
    else:
        print(f"⚠️  Forecast summary not found: {FORECAST_SUMMARY}")
    
    # 2. Register Clustering Model
    if CLUSTERING_METADATA.exists():
        print(f"\n🎯 Registering Clustering model...")
        with open(CLUSTERING_METADATA, 'r') as f:
            metadata = json.load(f)
        total_registered += await register_clustering_model(conn, metadata)
    else:
        print(f"⚠️  Clustering metadata not found: {CLUSTERING_METADATA}")
    
    # 3. Register Recommender Model
    if RECOMMENDER_METADATA.exists():
        print(f"\n💡 Registering Recommender model...")
        with open(RECOMMENDER_METADATA, 'r') as f:
            metadata = json.load(f)
        total_registered += await register_recommender_model(conn, metadata)
    else:
        print(f"⚠️  Recommender metadata not found: {RECOMMENDER_METADATA}")
    
    await conn.close()
    
    print(f"\n✅ Total: {total_registered} new models registered in ml_models_registry")
    
    # List all registered models
    conn = await asyncpg.connect(database_url, ssl='require')
    all_models = await conn.fetch(
        "SELECT model_name, version, algorithm, status FROM ml_models_registry ORDER BY last_updated DESC"
    )
    
    if all_models:
        print(f"\n📋 All registered models ({len(all_models)}):")
        for model in all_models:
            print(f"   • {model['model_name']} ({model['version']}) - {model['algorithm']} [{model['status']}]")
    
    await conn.close()


async def list_registered_models(database_url: str):
    """List all registered models from the database."""
    database_url = normalize_database_url(database_url)
    conn = await asyncpg.connect(database_url, ssl='require')
    
    rows = await conn.fetch(
        """
        SELECT model_name, version, algorithm, metrics, trained_on, status
        FROM ml_models_registry
        ORDER BY last_updated DESC
        """
    )
    
    await conn.close()
    
    if not rows:
        print("\nNo models registered yet")
        return
    
    print(f"\n📊 Registered Models ({len(rows)}):")
    print("=" * 80)
    for row in rows:
        status_icon = "🟢 ACTIVE" if row['status'] == 'active' else "⚪ INACTIVE"
        print(f"{status_icon} {row['model_name']} ({row['version']})")
        print(f"   Algorithm: {row['algorithm']}")
        print(f"   Trained: {row['trained_on']}")
        if row['metrics']:
            metrics = json.loads(row['metrics'])
            print(f"   Metrics: {metrics}")
        print()


async def main():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set")
        return
    
    print("🔧 MODEL REGISTRY - Wenda ML Backend")
    print("=" * 80)
    
    await register_models(database_url)
    await list_registered_models(database_url)


if __name__ == '__main__':
    asyncio.run(main())
