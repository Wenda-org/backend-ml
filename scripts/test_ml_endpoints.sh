#!/bin/bash
# Script para testar endpoints ML

BASE_URL="http://localhost:8000"

echo "=========================================="
echo "🧪 Testando Endpoints ML - Wenda Backend"
echo "=========================================="
echo ""

# 1. Health check geral
echo "1️⃣  GET / (Health check geral)"
curl -s "$BASE_URL/" | python3 -m json.tool
echo ""
echo ""

# 2. Health check do módulo ML
echo "2️⃣  GET /api/ml/health"
curl -s "$BASE_URL/api/ml/health" | python3 -m json.tool
echo ""
echo ""

# 3. Forecast - Previsão de visitantes
echo "3️⃣  POST /api/ml/forecast (Previsão para Luanda em Dez/2025)"
curl -s -X POST "$BASE_URL/api/ml/forecast" \
  -H "Content-Type: application/json" \
  -d '{
    "province": "Luanda",
    "month": 12,
    "year": 2025
  }' | python3 -m json.tool
echo ""
echo ""

# 4. Forecast - Namibe em Julho
echo "4️⃣  POST /api/ml/forecast (Previsão para Namibe em Jul/2026)"
curl -s -X POST "$BASE_URL/api/ml/forecast" \
  -H "Content-Type: application/json" \
  -d '{
    "province": "Namibe",
    "month": 7,
    "year": 2026
  }' | python3 -m json.tool
echo ""
echo ""

# 5. Recommend - Recomendações de praias
echo "5️⃣  POST /api/ml/recommend (Recomendações - categoria: beach)"
curl -s -X POST "$BASE_URL/api/ml/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "preferences": {
      "categories": ["beach"],
      "budget": "medium"
    },
    "limit": 5
  }' | python3 -m json.tool
echo ""
echo ""

# 6. Recommend - Natureza + Cultura
echo "6️⃣  POST /api/ml/recommend (Recomendações - natureza e cultura)"
curl -s -X POST "$BASE_URL/api/ml/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "preferences": {
      "categories": ["nature", "culture"],
      "provinces": ["Huila", "Luanda"]
    },
    "limit": 5
  }' | python3 -m json.tool
echo ""
echo ""

# 7. Segments - Perfis de turistas
echo "7️⃣  GET /api/ml/segments (Perfis de turistas)"
curl -s "$BASE_URL/api/ml/segments" | python3 -m json.tool
echo ""
echo ""

echo "=========================================="
echo "✅ Testes completos!"
echo "=========================================="
