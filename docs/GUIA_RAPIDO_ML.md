# 🚀 IMPLEMENTAÇÃO COMPLETA - 3 Modelos ML em Produção

## 📊 VISÃO GERAL

O backend ML da Wenda possui **3 modelos de Machine Learning** totalmente implementados e integrados:

| Modelo | Tipo | Algoritmo | Status | Endpoint |
|--------|------|-----------|--------|----------|
| **Forecast** | Regressão | RandomForest | ✅ Produção | `POST /ml/forecast` |
| **Clustering** | Unsupervised | K-Means | ✅ Produção | `GET /ml/segments` |
| **Recommender** | Content-Based | TF-IDF + Cosine | ✅ Produção | `POST /ml/recommend` |

---

## ✅ MODELO 1: FORECAST (Previsão de Visitantes)

### Implementação

#### Criado: `app/services/forecast.py`
**O que faz**: Serviço que carrega e usa os modelos treinados

```python
class ForecastService:
    - _models: cache em memória (lazy loading)
    - predict() → retorna predição + intervalo de confiança
    - list_available_models() → lista todos os modelos
    - get_model_info() → métricas de um modelo específico
```

**Como funciona**:
1. Primeiro acesso: carrega modelo do disco (`models/*.joblib`)
2. Mantém em cache (memória) para chamadas futuras
3. Usa árvores do RandomForest para calcular intervalo de confiança
4. Se modelo não existe, retorna `None` (API faz fallback)

#### Atualizado: `app/api/ml.py`
**Mudanças no endpoint `/ml/forecast`**:

**ANTES (placeholder)**:
```python
# Calculava média histórica + sazonalidade hardcoded
predicted = avg_historical * growth_factor * seasonal_factor
model_version = "v0.1.0-baseline-avg"
```

**AGORA (modelo real)**:
```python
forecast_service = get_forecast_service()
prediction = forecast_service.predict(province, year, month)

if prediction:
    # USA MODELO TREINADO
    return predicted_visitors, confidence_interval
    model_version = "v1.0.0-rf-trained"  # ← INDICA MODELO REAL
else:
    # FALLBACK (modelo não existe)
    model_version = "v0.1.0-baseline-fallback"
```

**Resultado**: API agora usa modelos reais e indica qual método usou via `model_version`

**Performance**: MAPE médio de **7.8%** em 6 províncias

---

## ✅ MODELO 2: CLUSTERING (Segmentação de Turistas)

### Implementação

#### Criado: `scripts/train_clustering.py`
**O que faz**: Treina modelo K-Means para segmentar turistas

```python
# Gera 500 perfis sintéticos baseados nos 5 perfis documentados
# Features: budget, trip_duration, preferences (beach, culture, nature, etc)
# Treina K-Means com 5 clusters
# Analisa características de cada cluster
```

#### Criado: `app/services/clustering.py`
**O que faz**: Serviço que carrega modelo K-Means

```python
class ClusteringService:
    - get_segments() → lista todos os segmentos identificados
    - predict_segment(...) → prevê segmento de um usuário
    - get_model_info() → metadata do modelo
```

#### Atualizado: `app/api/ml.py`
**Endpoint `/ml/segments`**:

**ANTES (placeholder)**:
```python
# Segmentos hardcoded
segments = [
    TouristSegment(name="Relaxante Tradicional", percentage=35.0, ...),
    ...
]
model_version = "v0.1.0-clustering-placeholder"
```

**AGORA (modelo real)**:
```python
clustering_service = get_clustering_service()
segments_data = clustering_service.get_segments()

if segments_data:
    # USA CLUSTERS REAIS DO K-MEANS
    segments = [build_from_cluster_data(...)]
    model_version = "v1.0.0-kmeans-trained"  # ← MODELO REAL
else:
    # FALLBACK
    model_version = "v0.1.0-clustering-fallback"
```

**Resultado**: API retorna segmentos descobertos pelo K-Means

**Performance**: Silhouette score de **0.357** (aceitável para baseline)

### Segmentos Identificados

```
Cluster 0: Negócios & Lazer (15.0%)
  - Budget: 3.0/3 (high)
  - Avg trip: 4 days, Group: 1 person
  - Top prefs: gastronomy (0.83), culture (0.75)

Cluster 1: Aventureiro Explorador (18.4%)
  - Budget: 2.5/3
  - Avg trip: 10 days, Group: 2 people
  - Top prefs: nature (0.90), adventure (0.90)

Cluster 2: Relaxante Tradicional (35.0%)
  - Budget: 2.3/3
  - Avg trip: 6 days, Group: 3 people
  - Top prefs: beach (0.90), gastronomy (0.66)

Cluster 3: Aventureiro Explorador (11.6%)
  - Budget: 2.5/3
  - Avg trip: 10 days, Group: 4 people
  - Top prefs: nature (0.91), adventure (0.89)

Cluster 4: Cultural Urbano (20.0%)
  - Budget: 2.4/3
  - Avg trip: 5 days, Group: 2 people
  - Top prefs: culture (0.91), gastronomy (0.83)
```

---

## ✅ MODELO 3: RECOMMENDER (Sistema de Recomendação)

### Implementação

#### Criado: `scripts/train_recommender.py`
**O que faz**: Treina sistema de recomendação content-based

```python
# Busca 23 destinos do banco
# Cria features: TF-IDF (descrição) + One-Hot (categoria/província) + Rating
# Calcula matriz de similaridade cosine (23x23)
# Salva modelo e metadata
```

**Features usadas**:
- **TF-IDF** (peso 0.4): texto da descrição + categoria + província
- **Category** (peso 0.3): one-hot encoding (culture, beach, nature)
- **Province** (peso 0.2): one-hot encoding (9 províncias)
- **Rating** (peso 0.1): normalizado 0-1

#### Criado: `app/services/recommender.py`
**O que faz**: Serviço que fornece recomendações

```python
class RecommenderService:
    - recommend_similar(destination_id) → destinos similares
    - recommend_by_preferences(categories, provinces) → filtro + score
    - recommend_hybrid(...) → combina similaridade + filtros
```

#### Atualizado: `app/api/ml.py`
**Endpoint `/ml/recommend`**:

**ANTES (placeholder)**:
```python
# Query simples no BD + ordenação por rating
query = select(Destination).order_by(rating.desc())
model_version = "v0.1.0-content-filter"
```

**AGORA (modelo real)**:
```python
recommender_service = get_recommender_service()
recommendations = recommender_service.recommend_by_preferences(
    categories=request.preferences.categories,
    provinces=request.preferences.provinces
)

if recommendations:
    # USA CONTENT-BASED FILTERING
    model_version = "v1.0.0-content-based-trained"  # ← MODELO REAL
else:
    # FALLBACK
    model_version = "v0.1.0-content-filter-fallback"
```

**Resultado**: API recomenda baseado em similaridade de conteúdo

**Performance**: Similaridade média entre destinos similares **>0.6**

### Exemplos de Similaridade

```
Ilha do Mussulo (beach)
  → Baía de Luanda (beach) - Score: 0.778
  → Praia Morena (beach) - Score: 0.610

Fortaleza de São Miguel (culture)
  → Museu Nacional de Antropologia (culture) - Score: 0.709
  → Igreja da Nossa Senhora do Pópulo (culture) - Score: 0.657

Miradouro da Lua (nature)
  → Pedras Negras de Pungo Andongo (nature) - Score: 0.750
  → Serra da Leba (nature) - Score: 0.476
```

---

## 📁 ARQUIVOS DE MODELOS GERADOS

Todos os modelos são salvos em `models/`:

### Forecast (6 províncias)
```
models/
  forecast_Luanda.joblib         # RandomForest treinado
  forecast_Benguela.joblib
  forecast_Huila.joblib
  ...
  training_summary.json          # Métricas consolidadas
```

### Clustering
```
models/
  clustering_kmeans.joblib       # Modelo K-Means
  clustering_scaler.joblib       # StandardScaler
  clustering_metadata.json       # Info sobre clusters
```

### Recommender
```
models/
  recommender_similarity_matrix.npy   # Matriz 23x23 cosine similarity
  recommender_features.npy            # Features normalizadas
  recommender_tfidf.joblib            # TF-IDF vectorizer
  recommender_scaler.joblib           # Feature scaler
  recommender_metadata.json           # Info sobre destinos/features
```

---

## 🧪 COMO TESTAR OS MODELOS

### 1. Forecast
```bash
curl -X POST http://localhost:8000/api/ml/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "destination_id": 1,
    "forecast_months": 12
  }'
```

Resposta esperada:
```json
{
  "destination_id": 1,
  "forecast": [
    {"month": "2024-02", "predicted_visitors": 4534.2, "confidence_min": 4200, "confidence_max": 4868},
    ...
  ],
  "model_version": "v1.0.0-rf-trained"
}
```

### 2. Clustering
```bash
curl http://localhost:8000/api/ml/segments
```

Resposta esperada:
```json
{
  "segments": [
    {
      "id": 0,
      "name": "Negócios & Lazer",
      "percentage": 15.0,
      "description": "Viajantes de negócios que combinam trabalho com lazer",
      "characteristics": {
        "budget_level": "high",
        "avg_trip_duration": 4,
        "top_preferences": ["gastronomy", "culture"]
      }
    },
    ...
  ],
  "model_version": "v1.0.0-kmeans-trained",
  "total_segments": 5
}
```

### 3. Recommender
```bash
curl -X POST http://localhost:8000/api/ml/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "preferences": {
      "categories": ["beach", "nature"],
      "provinces": ["Luanda", "Benguela"]
    },
    "limit": 5
  }'
```

Resposta esperada:
```json
{
  "recommendations": [
    {
      "destination_id": 4,
      "name": "Ilha do Mussulo",
      "score": 0.876,
      "reason": "beach preference match"
    },
    ...
  ],
  "model_version": "v1.0.0-content-based-trained"
}
```

---

## 🔄 PRÓXIMOS PASSOS (MELHORIAS FUTURAS)

### Curto Prazo
- [ ] Coletar logs de interações reais dos usuários
- [ ] Implementar testes automatizados end-to-end
- [ ] Adicionar monitoramento de performance (drift detection)
- [ ] A/B testing entre modelo atual e variações

### Médio Prazo
- [ ] **Clustering**: Re-treinar com dados reais quando tiver >100 usuários
- [ ] **Recommender**: Evoluir para Collaborative Filtering com dados de interação
- [ ] **Forecast**: Adicionar features sazonais (feriados, eventos)
- [ ] Implementar modelo de sentiment analysis em reviews

### Longo Prazo
- [ ] Sistema de ensemble para combinar múltiplos modelos
- [ ] Auto-tuning de hiperparâmetros
- [ ] Deploy em infraestrutura escalável (Docker + K8s)
- [ ] Dashboard de monitoramento ML (MLflow ou similar)

## 📊 SUMÁRIO TÉCNICO

| Aspecto | Forecast | Clustering | Recommender |
|---------|----------|------------|-------------|
| **Algoritmo** | RandomForest | K-Means | TF-IDF + Cosine |
| **Performance** | MAPE 7.8% | Silhouette 0.357 | Sim >0.6 |
| **Dados** | 2,172 registros | 500 sintéticos | 23 destinos |
| **Features** | 7 (trend, sazonais) | 8 (budget, prefs) | 63 (texto + cat) |
| **Status** | ✅ Produção | ✅ Produção | ✅ Produção |
| **Fallback** | Baseline médias | Profiles estáticos | Rating sort |

---

## 📚 DOCUMENTAÇÃO ADICIONAL

- **Resumo Clustering + Recommender**: `docs/RESUMO_CLUSTERING_RECOMMENDER.md`
- **Perfis de Turistas**: `docs/perfis-viajantes-wenda.md`
- **Estratégia de Dados**: `docs/estrategia-dados-wenda.md`

---
**O que faz**: Registra modelos treinados na tabela `ml_models_registry`

**Fluxo**:
1. Lê `models/training_summary.json` (criado no treino)
2. Para cada modelo:
   - Checa se já existe (por `model_name` + `version`)
   - Se não existe: insere registro com métricas
3. Lista todos os modelos registrados

**Schema da tabela `ml_models_registry`**:
```sql
id              SERIAL PRIMARY KEY
model_name      VARCHAR(100)  -- Ex: "forecast_Luanda"
version         VARCHAR(20)   -- Ex: "v1.0.0-rf-baseline"
algorithm       VARCHAR(100)  -- Ex: "RandomForestRegressor"
metrics         JSONB         -- {"mae": 707.23, "mape": 4.85, ...}
status          VARCHAR(20)   -- "active" ou "inactive"
trained_on      DATE          -- Data do treino
last_updated    TIMESTAMP     -- Última atualização
```

**Output do script**:
```
📝 Registering 6 models...
   ✅ Luanda: MAE=707.23, MAPE=4.85%
   ✅ Benguela: MAE=472.89, MAPE=8.23%
   ...
✅ Registered 6 new models in ml_models_registry
```

**Para que serve**: Auditoria, versionamento, histórico de modelos

---

### **Passo 4: Endpoint para Listar Modelos** ✅

#### Novo endpoint: `GET /api/ml/models`

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
  "generated_at": "2025-11-11T12:50:50.412478"
}
```

**Para que serve**:
- Frontend pode exibir quais províncias têm modelo treinado
- Dashboard de monitoramento de modelos
- Validar que modelos estão carregados e disponíveis

#### Atualizado: `GET /api/ml/health`

**ANTES**:
```json
{
  "status": "healthy",
  "model_status": "placeholder - using baseline algorithms"
}
```

**AGORA**:
```json
{
  "status": "healthy",
  "trained_models": 6,  // ← NOVO
  "model_status": "trained models available"  // ← ATUALIZADO
}
```

---

## 🎯 COMO TUDO FUNCIONA JUNTO

### Fluxo End-to-End de uma Previsão

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CLIENTE FAZ REQUEST                                      │
│    POST /api/ml/forecast                                    │
│    {"province": "Luanda", "month": 12, "year": 2025}        │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. ENDPOINT (app/api/ml.py)                                 │
│    - Valida província                                       │
│    - Chama forecast_service.predict()                       │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. FORECAST SERVICE (app/services/forecast.py)              │
│    - Verifica cache: modelo já carregado?                   │
│      ├─ SIM → usa modelo em memória                         │
│      └─ NÃO → carrega de models/forecast_Luanda.joblib      │
│    - Cria features: [year, month_sin, month_cos, ...]       │
│    - model.predict(X)                                       │
│    - Calcula intervalo confiança (std das árvores RF)       │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. RETORNA PREDIÇÃO                                         │
│    {                                                        │
│      "predicted_visitors": 11205,                           │
│      "confidence_interval": {                               │
│        "lower": 9764,                                       │
│        "upper": 12646                                       │
│      },                                                     │
│      "model_version": "v1.0.0-rf-trained"  ← MODELO REAL!   │
│    }                                                        │
└─────────────────────────────────────────────────────────────┘
```

### Fluxo com Fallback (modelo não existe)

```
Cliente → POST /forecast {"province": "NovaProvíncia", ...}
                │
                ▼
       forecast_service.predict()
                │
                ├─ Tenta carregar modelo
                ├─ models/forecast_NovaProvíncia.joblib NÃO EXISTE
                └─ Retorna None
                │
                ▼
       Endpoint usa FALLBACK:
                │
                ├─ Busca média histórica no BD
                ├─ Aplica sazonalidade hardcoded
                └─ Retorna com model_version: "v0.1.0-baseline-fallback"
```

**Vantagem**: API **sempre responde**, mesmo sem modelo específico

---

## 🧪 QUANDO USAR CADA COMPONENTE

### 1. **Scripts de Treino** (`scripts/train_forecast_baseline.py`)
**Quando**:
- ✅ Novos dados históricos disponíveis (>10% de crescimento no dataset)
- ✅ Melhorias no algoritmo ou features
- ✅ Re-treino periódico (mensal/trimestral)

**Não usar quando**:
- ❌ Apenas para testar API (modelos já existem)
- ❌ Dados não mudaram significativamente

**Frequência sugerida**: **Mensal** ou quando acumular novos dados

---

### 2. **Registro de Modelos** (`scripts/register_models.py`)
**Quando**:
- ✅ **Sempre** após treinar novos modelos
- ✅ Para auditoria e versionamento
- ✅ Antes de deploy em produção

**Não usar quando**:
- ❌ Modelos já estão registrados (script detecta e pula)

**Frequência**: **Após cada treino**

---

### 3. **Avaliação** (`scripts/evaluate_models.py`)
**Quando**:
- ✅ Após treino (validar performance)
- ✅ Periodicamente (detectar drift - performance degrada?)
- ✅ Antes de deploy em produção
- ✅ Para comparar versões de modelos

**Não usar quando**:
- ❌ Apenas para consultar métricas (use GET /api/ml/models)

**Frequência**: **Após cada treino + monitoramento mensal**

---

### 4. **API de Inferência** (`POST /api/ml/forecast`)
**Quando**:
- ✅ **Sempre** que precisar de previsões
- ✅ Frontend renderizando cards de destinos
- ✅ Dashboards analytics
- ✅ Planejamento de viagens (usuário seleciona destino + data)

**Não usar quando**:
- ❌ Para treino (use scripts offline)
- ❌ Para análise histórica massiva (consulte BD direto)

**Frequência**: **Tempo real** (milhares de chamadas por dia em produção)

---

### 5. **Listagem de Modelos** (`GET /api/ml/models`)
**Quando**:
- ✅ Frontend precisa saber quais províncias têm modelo
- ✅ Dashboard de monitoramento ML
- ✅ Health checks de infraestrutura

**Não usar quando**:
- ❌ Para fazer previsões (use `/forecast`)

**Frequência**: **Sob demanda** (carregamento de página, dashboards)

---

## 📊 MÉTRICAS DE SUCESSO

### Performance Atual (Baseline)
| Métrica | Valor | Interpretação |
|---------|-------|---------------|
| MAPE médio | **7.8%** | ⭐⭐⭐⭐ Bom para baseline |
| Melhor província | Luanda (4.8%) | ⭐⭐⭐⭐⭐ Excelente |
| Pior província | Huila (8.9%) | ⭐⭐⭐⭐ Bom |
| Modelos treinados | 6/6 províncias | ✅ Cobertura total |

### Benchmark da Indústria
- **MAPE < 10%**: Bom para previsão de turismo
- **MAPE 5-8%**: Muito bom (nosso caso!)
- **MAPE < 5%**: Excelente (Luanda alcançou!)

---

## 🎓 EXEMPLO DE USO NO FRONTEND

### Caso 1: Card de Destino com Previsão

```javascript
// Frontend: Componente de Destino
async function fetchForecast(province, month, year) {
  const response = await fetch('/api/ml/forecast', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ province, month, year })
  });
  return await response.json();
}

// Uso
const forecast = await fetchForecast('Luanda', 12, 2025);

// Renderizar
<Card>
  <h3>Luanda em Dezembro 2025</h3>
  <p>Visitantes esperados: 
    <strong>{forecast.predicted_visitors.toLocaleString()}</strong>
  </p>
  <small>
    Intervalo: {forecast.confidence_interval.lower} - {forecast.confidence_interval.upper}
  </small>
  <Badge>{forecast.model_version}</Badge>
</Card>
```

### Caso 2: Dashboard de Modelos (Admin)

```javascript
// Listar modelos disponíveis
const { models } = await fetch('/api/ml/models').then(r => r.json());

// Renderizar tabela
<Table>
  <thead>
    <tr><th>Província</th><th>MAE</th><th>MAPE</th><th>Status</th></tr>
  </thead>
  <tbody>
    {models.map(m => (
      <tr key={m.province}>
        <td>{m.province}</td>
        <td>{m.metrics.mae.toFixed(0)}</td>
        <td>{m.metrics.mape.toFixed(1)}%</td>
        <td>{m.loaded ? '✅' : '❌'}</td>
      </tr>
    ))}
  </tbody>
</Table>
```

---

## 🔧 TROUBLESHOOTING

### Problema: API retorna `model_version: "v0.1.0-baseline-fallback"`
**Causa**: Modelo não encontrado para a província  
**Solução**:
1. Verificar se arquivo existe: `ls models/forecast_{Provincia}.joblib`
2. Se não existe: rodar `python3 scripts/train_forecast_baseline.py`
3. Reiniciar servidor para limpar cache

### Problema: Previsões muito diferentes do esperado
**Causa**: Possível drift nos dados ou modelo desatualizado  
**Solução**:
1. Rodar `python3 scripts/evaluate_models.py` para ver métricas atuais
2. Se MAPE > 15%: retreinar modelos com dados atualizados
3. Comparar distribuição de dados treino vs produção

### Problema: Endpoint `/ml/models` retorna lista vazia
**Causa**: Pasta `models/` vazia ou modelos não foram treinados  
**Solução**:
1. Rodar `python3 scripts/train_forecast_baseline.py`
2. Verificar que arquivos foram criados: `ls models/`
3. Reiniciar servidor

---

## 📚 ARQUIVOS CRIADOS/MODIFICADOS

### Novos Arquivos
- ✅ `app/services/forecast.py` - Serviço de inferência
- ✅ `scripts/register_models.py` - Registro no BD
- ✅ `scripts/evaluate_models.py` - Avaliação de métricas
- ✅ `scripts/test_trained_models.sh` - Testes automatizados
- ✅ `docs/MODELOS_ML.md` - Documentação técnica completa
- ✅ `docs/RESUMO_MODELOS_ML.md` - Resumo executivo
- ✅ `docs/GUIA_RAPIDO_ML.md` - Este guia

### Arquivos Modificados
- ✅ `app/api/ml.py` - Integração com ForecastService + novo endpoint `/models`
- ✅ `app/main.py` - (sem mudanças, já incluía o router)

### Arquivos Gerados (em runtime)
- `models/forecast_*.joblib` - Modelos treinados
- `models/metrics_*.json` - Métricas por província
- `models/training_summary.json` - Resumo do treino
- `evaluation/evaluation_*.json` - Relatórios de avaliação

---

## ✅ CHECKLIST DE VALIDAÇÃO

Para confirmar que tudo está funcionando:

```bash
# 1. Modelos treinados existem?
ls models/forecast_*.joblib
# Esperado: 6 arquivos

# 2. Modelos registrados no BD?
python3 scripts/register_models.py
# Esperado: "6 models registered" ou "already existed"

# 3. API responde com modelos treinados?
curl http://localhost:8000/api/ml/health | jq '.trained_models'
# Esperado: 6

# 4. Listagem de modelos funciona?
curl http://localhost:8000/api/ml/models | jq '.total_models'
# Esperado: 6

# 5. Forecast usa modelo real?
curl -X POST http://localhost:8000/api/ml/forecast \
  -H "Content-Type: application/json" \
  -d '{"province": "Luanda", "month": 12, "year": 2025}' \
  | jq '.model_version'
# Esperado: "v1.0.0-rf-trained"

# 6. Métricas estão boas?
python3 scripts/evaluate_models.py
# Esperado: MAPE médio < 10%
```

Se todos passarem: **✅ Sistema 100% funcional!**

---

## 🎯 RESUMO EXECUTIVO

### O que foi implementado
1. ✅ Serviço de inferência com cache e lazy loading
2. ✅ Integração dos modelos reais na API
3. ✅ Sistema de registro e versionamento de modelos
4. ✅ Endpoint para listar modelos disponíveis
5. ✅ Fallback automático se modelo não existe
6. ✅ Scripts de avaliação e testes

### Qualidade
- **MAPE médio**: 7.8% (⭐⭐⭐⭐ Bom)
- **Cobertura**: 6/6 províncias
- **Resiliência**: Fallback funcional

### Pronto para
- ✅ Integração com frontend
- ✅ Deploy em produção
- ✅ Monitoramento contínuo
- ✅ Evolução incremental (adicionar features/modelos)

---

**Próximo passo sugerido**: Integrar com frontend para exibir previsões nos cards de destinos!
