"""
Register trained models in ml_models_registry table.

This script reads the training_summary.json and registers each model
in the database for tracking and versioning.

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
SUMMARY_FILE = MODEL_DIR / "training_summary.json"


def normalize_database_url(url: str) -> str:
    """Adapt neon URL to asyncpg connect usage."""
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://")
    return url


async def register_models(database_url: str):
    """Register all trained models in the ml_models_registry table."""
    
    if not SUMMARY_FILE.exists():
        print(f"❌ Training summary not found: {SUMMARY_FILE}")
        print("   Run train_forecast_baseline.py first!")
        return
    
    with open(SUMMARY_FILE, 'r') as f:
        summary = json.load(f)
    
    if not summary:
        print("No models found in training summary")
        return
    
    database_url = normalize_database_url(database_url)
    conn = await asyncpg.connect(database_url, ssl='require')
    
    print(f"📝 Registering {len(summary)} models...")
    
    registered = 0
    for model_info in summary:
        province = model_info['province']
        model_path = model_info['model_path']
        metrics = model_info['metrics']
        
        # Generate a version string
        version = "v1.0.0-rf-baseline"
        
        # Check if model already registered
        existing = await conn.fetchrow(
            "SELECT id FROM ml_models_registry WHERE model_name = $1 AND version = $2",
            f"forecast_{province}",
            version
        )
        
        if existing:
            print(f"   ⏭️  Model for {province} already registered (id: {existing['id']})")
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
        print(f"   ✅ {province}: MAE={mae}, MAPE={mape}%")
    
    await conn.close()
    
    print(f"\n✅ Registered {registered} new models in ml_models_registry")
    if registered < len(summary):
        print(f"   ({len(summary) - registered} already existed)")


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
