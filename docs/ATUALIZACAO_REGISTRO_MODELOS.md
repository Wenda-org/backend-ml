# 🔄 Atualização: Registro de Todos os Modelos ML

**Data:** 11 de Novembro de 2025  
**Issue:** `register_models.py` e `GET /api/ml/models` só tratavam de modelos forecast

---

## 🎯 Problema Identificado

Anteriormente:
- ❌ `scripts/register_models.py` só registrava modelos de **forecast**
- ❌ `GET /api/ml/models` só listava modelos de **forecast**
- ❌ Modelos de **clustering** e **recommender** não apareciam no registro

---

## ✅ Solução Implementada

### 1. **Atualizado `scripts/register_models.py`**

Agora o script registra **3 tipos de modelos**:

```python
# Antes (somente forecast)
SUMMARY_FILE = MODEL_DIR / "training_summary.json"

# Agora (todos os 3 tipos)
FORECAST_SUMMARY = MODEL_DIR / "training_summary.json"
CLUSTERING_METADATA = MODEL_DIR / "clustering_metadata.json"
RECOMMENDER_METADATA = MODEL_DIR / "recommender_metadata.json"
```

**Funções criadas:**
- `register_forecast_models(conn, summary)` - Registra 6 modelos de forecast (1 por província)
- `register_clustering_model(conn, metadata)` - Registra modelo K-Means
- `register_recommender_model(conn, metadata)` - Registra modelo content-based

**Output do script:**

```bash
📊 Registering Forecast models...
   ✅ Forecast Luanda: MAE=707.23, MAPE=4.85%
   ✅ Forecast Benguela: MAE=472.89, MAPE=8.23%
   ... (6 modelos)

🎯 Registering Clustering model...
   ✅ Clustering: 5 clusters, silhouette=0.357

💡 Registering Recommender model...
   ✅ Recommender: 23 destinations, content-based filtering

✅ Total: 8 new models registered in ml_models_registry

📋 All registered models (14):
   • recommender_content_based (v1.0.0-content) - TF-IDF + Cosine Similarity [active]
   • clustering_kmeans (v1.0.0-kmeans) - KMeans [active]
   • forecast_Luanda (v1.0.0-rf-trained) - RandomForestRegressor [active]
   ... (12 forecast models)
```

---

### 2. **Atualizado `GET /api/ml/models`**

Endpoint agora lista **todos os modelos** registrados no banco:

**Antes:**
```python
# Apenas forecast
forecast_service = get_forecast_service()
models = forecast_service.list_available_models()
```

**Agora:**
```python
# Busca TODOS os modelos do banco (forecast, clustering, recommender)
from app.models import MLModelsRegistry
from sqlalchemy import select

result = await db.execute(
    select(MLModelsRegistry).where(MLModelsRegistry.status == "active")
)
registered_models = result.scalars().all()
```

**Schema atualizado:**

```python
class ModelInfo(BaseModel):
    model_type: str      # forecast, clustering, recommender
    model_name: str
    version: str
    algorithm: str
    metrics: dict
    status: str
    trained_on: Optional[str] = None

class ModelsListResponse(BaseModel):
    models: List[ModelInfo]
    total_models: int
    by_type: dict = {}   # ← NOVO: contagem por tipo
```

**Exemplo de resposta:**

```json
{
  "models": [
    {
      "model_type": "forecast",
      "model_name": "forecast_Luanda",
      "version": "v1.0.0-rf-trained",
      "algorithm": "RandomForestRegressor",
      "metrics": {"mae": 707.23, "mape": 4.85, "test_samples": 12},
      "status": "active",
      "trained_on": "2025-11-11"
    },
    {
      "model_type": "clustering",
      "model_name": "clustering_kmeans",
      "version": "v1.0.0-kmeans",
      "algorithm": "KMeans",
      "metrics": {
        "n_clusters": 5,
        "n_samples": 500,
        "silhouette_score": 0.357
      },
      "status": "active",
      "trained_on": "2025-11-11"
    },
    {
      "model_type": "recommender",
      "model_name": "recommender_content_based",
      "version": "v1.0.0-content",
      "algorithm": "TF-IDF + Cosine Similarity",
      "metrics": {
        "n_destinations": 23,
        "feature_dim": 63,
        "similarity_metric": "cosine"
      },
      "status": "active",
      "trained_on": "2025-11-11"
    }
  ],
  "total_models": 14,
  "by_type": {
    "forecast": 12,
    "clustering": 1,
    "recommender": 1
  }
}
```

---

## 🧪 Como Testar

### 1. Registrar todos os modelos
```bash
python3 scripts/register_models.py
```

### 2. Listar via API
```bash
curl http://localhost:8000/api/ml/models | python3 -m json.tool
```

### 3. Ver resumo por tipo
```bash
curl -s http://localhost:8000/api/ml/models | \
  python3 -c "import sys, json; data=json.load(sys.stdin); \
  print(f\"Total: {data['total_models']}\"); \
  print(f\"By type: {data['by_type']}\")"
```

**Output esperado:**
```
Total: 14
By type: {'forecast': 12, 'clustering': 1, 'recommender': 1}
```

---

## 📊 Modelos Registrados

| Tipo | Quantidade | Modelos |
|------|-----------|---------|
| **Forecast** | 12 | 6 províncias × 2 versões (baseline + trained) |
| **Clustering** | 1 | K-Means (5 clusters) |
| **Recommender** | 1 | Content-Based (TF-IDF + Cosine) |
| **TOTAL** | **14** | Todos ativos no banco |

---

## 🔑 Pontos-Chave

1. ✅ **Todos os 3 modelos** agora são registrados no banco
2. ✅ **API unificada** para listar todos os modelos
3. ✅ **Métricas específicas** para cada tipo de modelo
4. ✅ **Versionamento** adequado (v1.0.0-*)
5. ✅ **Status tracking** (active/inactive)
6. ✅ **Contagem por tipo** no response

---

## 📝 Próximos Passos

- [ ] Adicionar endpoint para **desativar** modelos antigos
- [ ] Implementar **auto-cleanup** de versões duplicadas (v1.0.0-rf-baseline vs v1.0.0-rf-trained)
- [ ] Criar endpoint `GET /api/ml/models/{model_type}` para filtrar por tipo
- [ ] Dashboard de visualização de métricas de todos os modelos
