# Sistema de Modelos ML - Wenda Backend

## 📋 Visão Geral

O backend ML da plataforma Wenda agora possui **modelos de Machine Learning reais** treinados e integrados na API. O sistema implementa previsão de visitantes por província usando Random Forest Regression.

---

## 🏗️ Arquitetura do Sistema ML

### Componentes Principais

```
backend-ml/
├── app/
│   ├── services/
│   │   └── forecast.py          # Serviço de carregamento e predição de modelos
│   └── api/
│       └── ml.py                 # Endpoints ML (forecast, recommend, segments, models)
├── scripts/
│   ├── train_forecast_baseline.py    # Pipeline de treinamento
│   ├── register_models.py            # Registro de modelos no BD
│   └── evaluate_models.py            # Avaliação de métricas
├── models/                       # Modelos treinados (*.joblib)
│   ├── forecast_Luanda.joblib
│   ├── forecast_Benguela.joblib
│   ├── metrics_*.json
│   └── training_summary.json
└── evaluation/                   # Relatórios de avaliação
    └── evaluation_*.json
```

---

## 🎯 Modelo de Previsão (Forecast)

### Tipo de Modelo
- **Algoritmo**: RandomForestRegressor (scikit-learn)
- **Granularidade**: Um modelo por província (6 modelos no total)
- **Objetivo**: Prever número total de visitantes (domésticos + estrangeiros) por mês/ano

### Features (Variáveis de Entrada)
1. **year** - Ano da previsão
2. **month_sin** - Componente seno do mês (sazonalidade cíclica)
3. **month_cos** - Componente cosseno do mês (sazonalidade cíclica)
4. **occupancy_rate** - Taxa de ocupação (opcional, default 0)
5. **avg_stay_days** - Média de dias de estadia (opcional, default 0)

### Target (Variável Alvo)
- **total_visitors** = domestic_visitors + foreign_visitors

### Treino/Teste
- **Dados de treino**: 2022-2023 (24 meses)
- **Dados de teste**: 2024 (12 meses)
- **Total de registros**: 216 (36 meses × 6 províncias)

---

## 📊 Performance dos Modelos

### Métricas por Província

| Província | MAE (visitantes) | MAPE (%) | Amostras Teste |
|-----------|------------------|----------|----------------|
| Luanda    | 707              | 4.8%     | 12             |
| Benguela  | 473              | 8.2%     | 12             |
| Huila     | 325              | 8.9%     | 12             |
| Namibe    | 139              | 7.8%     | 12             |
| Cunene    | 81               | 8.3%     | 12             |
| Malanje   | 210              | 8.6%     | 12             |

### Resumo Geral
- **MAE médio**: 322 visitantes
- **MAPE médio**: 7.8%
- **Modelos avaliados**: 6/6

> **Interpretação**: O modelo tem erro médio de ~8%, o que é aceitável para uma baseline inicial. Luanda tem melhor MAPE (4.8%) apesar de MAE maior devido ao volume absoluto ser maior.

---

## 🚀 Como Funciona no Projeto

### 1. Ciclo de Vida do Modelo

```
┌─────────────────┐
│  1. TREINAMENTO │  scripts/train_forecast_baseline.py
│  ├─ Fetch data  │  - Busca dados do BD
│  ├─ Feature eng │  - Cria features (sin/cos, etc)
│  ├─ Train RF    │  - Treina RandomForest por província
│  └─ Save model  │  - Salva em models/*.joblib
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  2. REGISTRO    │  scripts/register_models.py
│  ├─ Read summary│  - Lê training_summary.json
│  ├─ Insert DB   │  - Insere em ml_models_registry
│  └─ Log metrics │  - Registra MAE/MAPE/versão
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  3. AVALIAÇÃO   │  scripts/evaluate_models.py
│  ├─ Load models │  - Carrega modelos treinados
│  ├─ Predict 2024│  - Testa em holdout set
│  └─ Save report │  - Salva evaluation/*.json
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  4. INFERÊNCIA  │  app/services/forecast.py + app/api/ml.py
│  ├─ Load cached │  - Lazy loading com cache em memória
│  ├─ Predict     │  - Predição com intervalo de confiança
│  └─ Fallback    │  - Baseline se modelo não existe
└─────────────────┘
```

### 2. Serviço de Forecast (`app/services/forecast.py`)

**Classe Principal**: `ForecastService`

```python
class ForecastService:
    def predict(province, year, month, occupancy_rate=0, avg_stay_days=0):
        """
        Retorna:
        {
            'predicted_visitors': int,
            'confidence_interval': {
                'lower': int,
                'upper': int
            }
        }
        """
```

**Características**:
- ✅ **Singleton**: Uma única instância global
- ✅ **Lazy Loading**: Modelos carregados apenas quando necessário
- ✅ **Cache em memória**: Modelos ficam em cache após primeiro uso
- ✅ **Intervalo de confiança**: Calculado via std dos estimadores (árvores) do RF
- ✅ **Graceful degradation**: Retorna `None` se modelo não existe (fallback no endpoint)

### 3. Endpoint de Forecast (`POST /api/ml/forecast`)

**Request**:
```json
{
  "province": "Luanda",
  "month": 12,
  "year": 2025
}
```

**Response (com modelo treinado)**:
```json
{
  "province": "Luanda",
  "month": 12,
  "year": 2025,
  "predicted_visitors": 11205,
  "confidence_interval": {
    "lower": 9764,
    "upper": 12646
  },
  "model_version": "v1.0.0-rf-trained",
  "generated_at": "2025-11-11T12:47:55.584890"
}
```

**Lógica**:
1. Validar província (deve estar em lista válida)
2. Tentar carregar modelo treinado via `ForecastService`
3. **Se modelo existe**: usar predição real → `model_version: "v1.0.0-rf-trained"`
4. **Se modelo não existe**: fallback para baseline (média histórica + sazonalidade) → `model_version: "v0.1.0-baseline-fallback"`

### 4. Endpoint de Modelos (`GET /api/ml/models`)

**Response**:
```json
{
  "models": [
    {
      "province": "Luanda",
      "model_path": "models/forecast_Luanda.joblib",
      "metrics": {
        "mae": 707.23,
        "mape": 4.85,
        "test_samples": 12
      },
      "loaded": true
    },
    ...
  ],
  "total_models": 6,
  "generated_at": "2025-11-11T12:46:57.855371"
}
```

**Uso**: Lista todos os modelos disponíveis com métricas para monitoramento.

---

## 🛠️ Como Usar

### 1. Treinar Modelos

```bash
export DATABASE_URL="postgresql://..."
python3 scripts/train_forecast_baseline.py
```

**Output**:
- Modelos salvos em `models/forecast_*.joblib`
- Métricas em `models/metrics_*.json`
- Resumo em `models/training_summary.json`

### 2. Registrar Modelos no BD

```bash
export DATABASE_URL="postgresql://..."
python3 scripts/register_models.py
```

**Output**:
- Insere registros em `ml_models_registry`
- Lista modelos registrados com métricas

### 3. Avaliar Modelos

```bash
export DATABASE_URL="postgresql://..."
python3 scripts/evaluate_models.py
```

**Output**:
- Relatório detalhado por província
- Breakdown mensal de erros
- Métricas agregadas (MAE/MAPE/RMSE)
- Salvo em `evaluation/evaluation_*.json`

### 4. Consultar API

```bash
# Health check (mostra quantos modelos estão disponíveis)
curl http://localhost:8000/api/ml/health

# Listar modelos disponíveis
curl http://localhost:8000/api/ml/models

# Fazer previsão
curl -X POST http://localhost:8000/api/ml/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "province": "Luanda",
    "month": 12,
    "year": 2025
  }'
```

---

## ⏱️ Quando Usar Cada Componente

### Scripts de Treino
**Quando**: 
- Novos dados históricos disponíveis
- Melhorias no algoritmo ou features
- Re-treino periódico (mensal/trimestral)

**Frequência sugerida**: Mensal ou quando acumular >10% novos dados

### Registro de Modelos
**Quando**:
- Após cada treino bem-sucedido
- Para versionamento e auditoria

### Avaliação
**Quando**:
- Após treino (para validar performance)
- Periodicamente (monitorar drift)
- Antes de deploy em produção

### API de Inferência
**Quando**:
- Sempre que frontend/outro backend precisar de previsões
- Em tempo real durante navegação do usuário
- Para dashboards e analytics

---

## 🔄 Fluxo de Integração com Frontend

```
Frontend (React/Next.js)
    │
    ├─ User selects província + mês/ano
    │
    ▼
POST /api/ml/forecast
    │
    ├─ Backend ML (FastAPI)
    │   ├─ Load model (cache)
    │   ├─ Predict
    │   └─ Return JSON
    │
    ▼
Frontend recebe:
    ├─ predicted_visitors
    ├─ confidence_interval
    └─ Renderiza gráfico/cards
```

**Exemplo de uso no frontend**:
```javascript
// Fetch forecast
const response = await fetch('/api/ml/forecast', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    province: 'Luanda',
    month: 12,
    year: 2025
  })
});

const forecast = await response.json();

// Renderizar
<div>
  <h3>Previsão para {forecast.province} - {forecast.month}/{forecast.year}</h3>
  <p>Visitantes esperados: {forecast.predicted_visitors.toLocaleString()}</p>
  <p>Intervalo: {forecast.confidence_interval.lower} - {forecast.confidence_interval.upper}</p>
  <small>Modelo: {forecast.model_version}</small>
</div>
```

---

## 🎓 Decisões Técnicas

### Por que RandomForest?
1. ✅ **Robusto**: Funciona bem com poucos dados (36 meses)
2. ✅ **Não-linear**: Captura padrões complexos sem tunning excessivo
3. ✅ **Intervalo de confiança**: Árvores individuais permitem estimar variância
4. ✅ **Baseline sólido**: Boa performance out-of-the-box

### Por que features cíclicas (sin/cos)?
- Meses são cíclicos (dezembro → janeiro)
- Sin/cos capturam essa continuidade (month=12 ≈ month=1)
- Melhor que one-hot encoding para sazonalidade

### Por que um modelo por província?
- **Prós**: Padrões regionais específicos, tunning independente
- **Contras**: Mais modelos para gerenciar
- **Alternativa futura**: Modelo único com province como feature categórica

---

## 🚀 Próximos Passos (Melhorias Futuras)

### Curto Prazo
- [ ] Adicionar lags (visitantes mês anterior) como feature
- [ ] Feature de feriados/eventos especiais
- [ ] Tuning de hiperparâmetros (GridSearch)
- [ ] CI/CD para re-treino automático

### Médio Prazo
- [ ] Testar modelos alternativos (XGBoost, LightGBM)
- [ ] Implementar Prophet para séries temporais clássicas
- [ ] Modelos por destino (granularidade mais fina)
- [ ] A/B testing de modelos

### Longo Prazo
- [ ] Deep Learning (LSTM/Transformer) para padrões complexos
- [ ] Multi-step forecasting (horizon >1 mês)
- [ ] Ensemble de modelos
- [ ] Auto-ML para otimização contínua

---

## 📚 Referências

- **scikit-learn RandomForest**: https://scikit-learn.org/stable/modules/ensemble.html#forest
- **Time Series Features**: https://www.kaggle.com/c/store-sales-time-series-forecasting
- **Cyclical Encoding**: https://ianlondon.github.io/blog/encoding-cyclical-features-24hour-time/

---

## 📞 Suporte

Para dúvidas ou problemas com os modelos:
1. Verificar logs do servidor (`uvicorn` output)
2. Checar `evaluation/*.json` para métricas atualizadas
3. Validar que modelos existem em `models/` e estão registrados no BD
4. Consultar endpoint `/api/ml/health` para status
