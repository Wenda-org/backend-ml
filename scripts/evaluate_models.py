"""
Evaluate trained forecast models.

This script:
- Loads each trained model
- Tests on 2024 data (holdout set)
- Calculates MAE, MAPE, and other metrics
- Generates evaluation report

Usage:
    export DATABASE_URL="postgresql://..."
    python3 scripts/evaluate_models.py
"""

import asyncio
import os
import json
from pathlib import Path
from typing import Dict, List

import asyncpg
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib


MODEL_DIR = Path("models")
EVAL_DIR = Path("evaluation")
EVAL_DIR.mkdir(parents=True, exist_ok=True)


def normalize_database_url(url: str) -> str:
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
    df['domestic_visitors'] = df['domestic_visitors'].fillna(0).astype(int)
    df['foreign_visitors'] = df['foreign_visitors'].fillna(0).astype(int)
    df['total_visitors'] = df['domestic_visitors'] + df['foreign_visitors']
    return df


def featurize(df: pd.DataFrame) -> pd.DataFrame:
    df['year'] = df['year'].astype(int)
    df['month'] = df['month'].astype(int)
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    
    for col in ['occupancy_rate', 'avg_stay_days']:
        if col not in df.columns:
            df[col] = 0
        df[col] = df[col].fillna(0)
    
    return df


def calculate_mape(y_true, y_pred):
    """Calculate MAPE avoiding division by zero."""
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    mask = y_true != 0
    if not mask.any():
        return 0.0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100


def evaluate_province(df: pd.DataFrame, province: str) -> Dict:
    """Evaluate model for a single province."""
    
    # Filter by province
    d = df[df['province'] == province].copy()
    if d.empty:
        return None
    
    # Sort
    d = d.sort_values(['year', 'month'])
    
    # Features
    features = ['year', 'month_sin', 'month_cos', 'occupancy_rate', 'avg_stay_days']
    
    # Split train/test
    train_mask = d['year'] < 2024
    test_mask = d['year'] == 2024
    
    X_train = d[train_mask][features]
    y_train = d[train_mask]['total_visitors']
    X_test = d[test_mask][features]
    y_test = d[test_mask]['total_visitors']
    
    if len(X_test) == 0:
        return {
            'province': province,
            'status': 'no_test_data',
            'test_samples': 0
        }
    
    # Load model
    model_path = MODEL_DIR / f"forecast_{province.replace(' ', '_')}.joblib"
    if not model_path.exists():
        return {
            'province': province,
            'status': 'no_model',
            'test_samples': len(X_test)
        }
    
    model = joblib.load(model_path)
    
    # Predict
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mape = calculate_mape(y_test, y_pred)
    
    # Additional metrics
    mean_actual = y_test.mean()
    mean_predicted = y_pred.mean()
    
    # Per-month breakdown
    monthly_errors = []
    for i, (actual, pred) in enumerate(zip(y_test, y_pred)):
        month = d[test_mask].iloc[i]['month']
        year = d[test_mask].iloc[i]['year']
        error_pct = abs((actual - pred) / actual * 100) if actual != 0 else 0
        monthly_errors.append({
            'month': int(month),
            'year': int(year),
            'actual': int(actual),
            'predicted': int(pred),
            'error': int(abs(actual - pred)),
            'error_pct': float(error_pct)
        })
    
    return {
        'province': province,
        'status': 'evaluated',
        'test_samples': int(len(X_test)),
        'train_samples': int(len(X_train)),
        'metrics': {
            'mae': float(mae),
            'rmse': float(rmse),
            'mape': float(mape),
            'mean_actual': float(mean_actual),
            'mean_predicted': float(mean_predicted)
        },
        'monthly_breakdown': monthly_errors
    }


async def main():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set")
        return
    
    print("📊 MODEL EVALUATION - Wenda ML Backend")
    print("=" * 80)
    
    # Fetch data
    print("📥 Loading data from database...")
    df = await fetch_data(database_url)
    if df.empty:
        print("❌ No data found")
        return
    
    df = featurize(df)
    provinces = df['province'].unique().tolist()
    
    print(f"✅ Loaded {len(df)} records for {len(provinces)} provinces")
    print()
    
    # Evaluate each province
    results = []
    for province in provinces:
        result = evaluate_province(df, province)
        if result:
            results.append(result)
            
            if result['status'] == 'evaluated':
                metrics = result['metrics']
                print(f"✅ {province}:")
                print(f"   Samples: {result['train_samples']} train, {result['test_samples']} test")
                print(f"   MAE: {metrics['mae']:.0f} visitors")
                print(f"   RMSE: {metrics['rmse']:.0f} visitors")
                print(f"   MAPE: {metrics['mape']:.1f}%")
                print(f"   Mean Actual: {metrics['mean_actual']:.0f}, Mean Predicted: {metrics['mean_predicted']:.0f}")
                print()
            else:
                print(f"⚠️  {province}: {result['status']}")
                print()
    
    # Save results
    eval_file = EVAL_DIR / f"evaluation_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(eval_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Evaluation results saved to: {eval_file}")
    
    # Summary statistics
    evaluated = [r for r in results if r['status'] == 'evaluated']
    if evaluated:
        print()
        print("=" * 80)
        print("📈 OVERALL SUMMARY")
        print("=" * 80)
        avg_mae = np.mean([r['metrics']['mae'] for r in evaluated])
        avg_mape = np.mean([r['metrics']['mape'] for r in evaluated])
        print(f"Average MAE across provinces: {avg_mae:.0f} visitors")
        print(f"Average MAPE across provinces: {avg_mape:.1f}%")
        print(f"Models evaluated: {len(evaluated)}/{len(provinces)}")


if __name__ == '__main__':
    asyncio.run(main())
