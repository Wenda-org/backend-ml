#!/bin/bash

# Test ML endpoints with trained models

BASE_URL="http://localhost:8000/api/ml"

echo "🧪 TESTING ML ENDPOINTS WITH TRAINED MODELS"
echo "=========================================="
echo ""

# Test 1: Health check
echo "1️⃣  Testing health endpoint..."
curl -s -X GET "${BASE_URL}/health" | jq '.'
echo ""

# Test 2: List available models
echo "2️⃣  Listing available models..."
curl -s -X GET "${BASE_URL}/models" | jq '.'
echo ""

# Test 3: Forecast with trained model (Luanda)
echo "3️⃣  Testing forecast for Luanda (should use trained model)..."
curl -s -X POST "${BASE_URL}/forecast" \
  -H "Content-Type: application/json" \
  -d '{
    "province": "Luanda",
    "month": 12,
    "year": 2025
  }' | jq '.'
echo ""

# Test 4: Forecast for another province (Benguela)
echo "4️⃣  Testing forecast for Benguela..."
curl -s -X POST "${BASE_URL}/forecast" \
  -H "Content-Type: application/json" \
  -d '{
    "province": "Benguela",
    "month": 6,
    "year": 2026
  }' | jq '.'
echo ""

# Test 5: Compare with fallback (if model was not available)
echo "5️⃣  Testing forecast - check model_version in response..."
echo "    - v1.0.0-rf-trained = using trained RandomForest model"
echo "    - v0.1.0-baseline-fallback = using fallback (no model found)"
echo ""

echo "✅ Test completed!"
