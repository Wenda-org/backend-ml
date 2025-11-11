"""
Train a simple baseline forecast model per province using scikit-learn.

Approach:
- Load `tourism_statistics` from DB (domestic_visitors + foreign_visitors -> total_visitors)
- Create features: year, month, month_sin, month_cos to capture seasonality
- Train per-province RandomForestRegressor on 2022-2023, validate on 2024
- Save models to `models/forecast_{province}.joblib`
- Save metrics to `models/metrics_{province}.json`

Usage:
    export DATABASE_URL="postgresql://..."
    python3 scripts/train_forecast_baseline.py

"""

import asyncio
import os
import json
from pathlib import Path
from typing import List

import asyncpg
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import joblib


MODEL_DIR = Path("models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def normalize_database_url(url: str) -> str:
    # adapt neon URL to asyncpg connect usage
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://")
    return url


async def fetch_data(database_url: str) -> pd.DataFrame:
    database_url = normalize_database_url(database_url)
    conn = await asyncpg.connect(database_url, ssl='require')

    rows = await conn.fetch(
        "SELECT province, month, year, domestic_visitors, foreign_visitors, occupancy_rate, avg_stay_days FROM tourism_statistics"
    )
    await conn.close()

    records = [dict(r) for r in rows]
    df = pd.DataFrame(records)
    # total visitors
    df['domestic_visitors'] = df['domestic_visitors'].fillna(0).astype(int)
    df['foreign_visitors'] = df['foreign_visitors'].fillna(0).astype(int)
    df['total_visitors'] = df['domestic_visitors'] + df['foreign_visitors']
    return df


def featurize(df: pd.DataFrame) -> pd.DataFrame:
    # Ensure types
    df['year'] = df['year'].astype(int)
    df['month'] = df['month'].astype(int)

    # cyclical month features
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)

    # Optionally add occupancy and avg_stay_days if present
    for col in ['occupancy_rate', 'avg_stay_days']:
        if col not in df.columns:
            df[col] = 0
        df[col] = df[col].fillna(0)

    return df


def train_and_save(df: pd.DataFrame, province: str):
    # Filter by province
    d = df[df['province'] == province].copy()
    if d.empty:
        print(f"[WARN] No data for province {province}")
        return None

    # Sort
    d = d.sort_values(['year', 'month'])

    # Features and target
    features = ['year', 'month_sin', 'month_cos', 'occupancy_rate', 'avg_stay_days']
    X = d[features]
    y = d['total_visitors']

    # Train on years 2022-2023, test on 2024 if available
    train_mask = d['year'] < 2024
    test_mask = d['year'] == 2024

    if train_mask.sum() < 6:
        print(f"[WARN] Not enough training data for {province} (found {train_mask.sum()} rows)")

    X_train = X[train_mask]
    y_train = y[train_mask]
    X_test = X[test_mask]
    y_test = y[test_mask]

    # Simple model: RandomForestRegressor
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    metrics = {}
    if len(X_test) > 0:
        preds = model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        # MAPE: avoid division by zero
        mape = np.mean(np.abs((y_test - preds) / np.where(y_test == 0, 1, y_test))) * 100
        metrics['mae'] = float(mae)
        metrics['mape'] = float(mape)
        metrics['test_samples'] = int(len(y_test))
    else:
        metrics['mae'] = None
        metrics['mape'] = None
        metrics['test_samples'] = 0

    # Save model and metrics
    model_path = MODEL_DIR / f"forecast_{province.replace(' ', '_')}.joblib"
    metrics_path = MODEL_DIR / f"metrics_{province.replace(' ', '_')}.json"
    joblib.dump(model, model_path)
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"Saved model for {province} -> {model_path} (metrics: {metrics})")
    return {'province': province, 'model_path': str(model_path), 'metrics': metrics}


async def main():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL not set")
        return

    df = await fetch_data(database_url)
    if df.empty:
        print("No tourism_statistics data found")
        return

    df = featurize(df)

    provinces = df['province'].unique().tolist()
    results = []
    for p in provinces:
        res = train_and_save(df, p)
        if res:
            results.append(res)

    # Summary
    summary_path = MODEL_DIR / "training_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Training complete. Summary written to {summary_path}")


if __name__ == '__main__':
    asyncio.run(main())
