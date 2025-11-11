# 📋 Estado Atual do Projeto Wenda ML Backend

**Data:** 15 de Janeiro de 2025  
**Status:** ✅ 3 Modelos ML em Produção | 🚧 Endpoints CRUD em desenvolvimento

---

## ✅ O que já está feito

### 1. Estrutura do Projeto
- ✅ FastAPI configurado (`app/main.py`, `app/api/routes.py`)
- ✅ SQLAlchemy com suporte async (asyncpg)
- ✅ Dockerfile criado e funcional
- ✅ Makefile com targets úteis (venv, install, build, start)
- ✅ `.gitignore` configurado
- ✅ `.env` com DATABASE_URL do NeonDB

### 2. Base de Dados
- ✅ **7 tabelas criadas no NeonDB:**
  - `users` - Utilizadores (turistas, operadores, admins)
  - `destinations` - Destinos turísticos (23 destinos cadastrados)
  - `tourism_statistics` - Estatísticas históricas de turismo (2,172 registros)
  - `ml_models_registry` - Registo de modelos ML
  - `ml_predictions` - Previsões geradas pelos modelos
  - `recommendations_log` - Log de recomendações servidas
  - `alembic_version` - Controle de migrations

- ✅ **Alembic configurado:**
  - Migration inicial aplicada (`d88ab493f030`)
  - Suporte para asyncpg (ajustado para remover parâmetros incompatíveis)
  - Script de validação: `scripts/check-tables-async.py`

### 3. Modelos SQLAlchemy
Definidos em `app/models.py`:
- `User` (id UUID, name, email, password_hash, role, country)
- `Destination` (id UUID, name, province, description, lat/long, category, rating, images)
- `TourismStatistics` (province, month, year, visitors, occupancy)
- `MLModelsRegistry` (model_name, version, algorithm, metrics, status)
- `MLPredictions` (model_name, province, month, year, predicted_visitors)
- `RecommendationsLog` (user_id, destination_id, score, model_version)

### 4. **🎯 MODELOS DE MACHINE LEARNING (COMPLETO)**

#### 4.1 Forecast - Previsão de Visitantes
**Status:** ✅ Em Produção  
**Algoritmo:** RandomForest Regression  
**Performance:** MAPE médio de **7.8%** em 6 províncias  
**Endpoint:** `POST /api/ml/forecast`

**Arquivos:**
- `scripts/train_forecast.py` - Script de treinamento
- `app/services/forecast.py` - Service layer
- `models/forecast_*.joblib` - 6 modelos treinados (1 por província)
- `models/training_summary.json` - Métricas consolidadas

**Features usadas:**
- Trend (crescimento temporal)
- Sazonalidade (sin/cos de mês)
- Ocupação hoteleira
- Rating do destino
- Lag features (visitantes mês anterior)

#### 4.2 Clustering - Segmentação de Turistas
**Status:** ✅ Em Produção  
**Algoritmo:** K-Means (5 clusters)  
**Performance:** Silhouette score de **0.357**  
**Endpoint:** `GET /api/ml/segments`

**Arquivos:**
- `scripts/train_clustering.py` - Script de treinamento
- `app/services/clustering.py` - Service layer
- `models/clustering_kmeans.joblib` - Modelo K-Means
- `models/clustering_scaler.joblib` - StandardScaler
- `models/clustering_metadata.json` - Info sobre clusters

**Features usadas:**
- Budget level (1-3)
- Trip duration (dias)
- Preferences: beach, culture, nature, adventure, gastronomy
- Trips per year
- Group size

**Segmentos identificados:**
1. **Negócios & Lazer** (15%) - Budget alto, trips curtas, gastronomy+culture
2. **Aventureiro Explorador** (30%) - Budget médio, trips longas, nature+adventure
3. **Relaxante Tradicional** (35%) - Budget médio, trips médias, beach+gastronomy
4. **Cultural Urbano** (20%) - Budget médio, trips médias, culture+gastronomy

#### 4.3 Recommender - Sistema de Recomendação
**Status:** ✅ Em Produção  
**Algoritmo:** Content-Based Filtering (TF-IDF + Cosine Similarity)  
**Performance:** Similaridade média **>0.6** entre destinos similares  
**Endpoint:** `POST /api/ml/recommend`

**Arquivos:**
- `scripts/train_recommender.py` - Script de treinamento
- `app/services/recommender.py` - Service layer
- `models/recommender_similarity_matrix.npy` - Matriz 23x23
- `models/recommender_features.npy` - Features normalizadas
- `models/recommender_tfidf.joblib` - TF-IDF vectorizer
- `models/recommender_scaler.joblib` - Feature scaler
- `models/recommender_metadata.json` - Info sobre destinos

**Features usadas:**
- TF-IDF (peso 0.4): descrição + categoria + província
- Category one-hot (peso 0.3): beach, culture, nature, etc.
- Province one-hot (peso 0.2): 9 províncias
- Rating normalizado (peso 0.1)

**Métodos de recomendação:**
- `recommend_similar(destination_id)` - Destinos similares por conteúdo
- `recommend_by_preferences(categories, provinces)` - Filtros + scoring
- `recommend_hybrid()` - Combina ambos os métodos

### 5. Scripts Utilitários
- ✅ `scripts/db-async-check.py` - Verifica conexão DB
- ✅ `scripts/check-tables-async.py` - Lista todas as tabelas
- ✅ `scripts/run_migrations.py` - Executa migrations (wrapper para alembic)
- ✅ `scripts/train_forecast.py` - Treina modelo de forecast
- ✅ `scripts/train_clustering.py` - Treina modelo de clustering
- ✅ `scripts/train_recommender.py` - Treina sistema de recomendação

---

## 🚧 O que falta fazer (Checklist Priorizada)

### FASE 1: Endpoints CRUD Básicos (Alta Prioridade)

#### 1.1 CRUD Users
**Arquivo:** `app/api/users.py` (criar)

Endpoints a implementar:
- [ ] `GET /api/users` - Listar todos os users (com paginação)
- [ ] `POST /api/users` - Criar novo user
- [ ] `GET /api/users/{id}` - Obter user por ID
- [ ] `PUT /api/users/{id}` - Atualizar user
- [ ] `DELETE /api/users/{id}` - Deletar user

#### 1.2 CRUD Destinations
**Arquivo:** `app/api/destinations.py` (criar)

Endpoints a implementar:
- [ ] `GET /api/destinations` - Listar destinos (filtros: province, category)
- [ ] `POST /api/destinations` - Criar novo destino
- [ ] `GET /api/destinations/{id}` - Obter destino por ID
- [ ] `PUT /api/destinations/{id}` - Atualizar destino
- [ ] `DELETE /api/destinations/{id}` - Deletar destino

---

### FASE 2: Melhorias nos Modelos ML (Prioridade Média)

#### 2.1 Testes Automatizados
- [ ] Criar `tests/test_forecast.py` - Testes para serviço de forecast
- [ ] Criar `tests/test_clustering.py` - Testes para serviço de clustering
- [ ] Criar `tests/test_recommender.py` - Testes para serviço de recomendação
- [ ] Criar `tests/test_ml_endpoints.py` - Testes end-to-end dos endpoints ML

#### 2.2 Monitoramento e Logging
- [ ] Adicionar logging estruturado em todos os services
- [ ] Criar endpoint `GET /api/ml/health` - Status de todos os modelos
- [ ] Implementar drift detection para forecast model
- [ ] Criar dashboard simples de métricas (visits, predictions, recommendations)

#### 2.3 Refinamento de Modelos
- [ ] **Clustering**: Re-treinar com dados reais quando >100 usuários
- [ ] **Recommender**: Adicionar collaborative filtering quando houver logs de interação
- [ ] **Forecast**: Adicionar features sazonais (feriados, eventos especiais)
- [ ] Implementar auto-retraining periódico (weekly/monthly)

---

### FASE 3: Features Avançadas (Prioridade Baixa)

#### 3.1 Sistema de Feedback
- [ ] Endpoint para capturar feedback de recomendações
- [ ] Armazenar cliques/visitas/bookings em `recommendations_log`
- [ ] Usar logs para retreinar modelos

#### 3.2 Análise de Sentimento
- [ ] Criar modelo de sentiment analysis para reviews
- [ ] Integrar sentiment scores em recomendações
- [ ] Endpoint `POST /api/ml/analyze-sentiment`

#### 3.3 Infraestrutura
- [ ] Deploy em Docker container
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Configurar ambiente de staging
- [ ] Documentação Swagger/OpenAPI completa

---
  "province": "Luanda",
  "month": 12,
  "year": 2025
}

// Response (placeholder)
{
  "province": "Luanda",
  "month": 12,
  "year": 2025,
  "predicted_visitors": 15420,
  "confidence_interval": {"lower": 14000, "upper": 17000},
  "model_version": "v0.1.0-placeholder",
  "generated_at": "2025-11-04T15:30:00Z"
}
```

#### 2.2 Endpoint de Recomendação
- [ ] `POST /api/ml/recommend`
  - Input: `{user_id, preferences: {category, budget, duration}}`
  - Output: `[{destination_id, score, reason}]`
  - Nota: Placeholder baseado em filtros simples

**Exemplo:**
```json
// POST /api/ml/recommend
{
  "user_id": "uuid-here",
  "preferences": {
    "categories": ["culture", "beach"],
    "budget": "medium",
    "duration_days": 5
  }
}

// Response (placeholder - filtro por categoria)
{
  "recommendations": [
    {
      "destination_id": "uuid-dest-1",
      "name": "Fortaleza de São Miguel",
      "score": 0.92,
      "reason": "Matches your interest in culture"
    },
    {
      "destination_id": "uuid-dest-2",
      "name": "Praia Morena",
      "score": 0.88,
      "reason": "Popular beach destination"
    }
  ],
  "model_version": "v0.1.0-placeholder"
}
```

#### 2.3 Endpoint de Segmentação
- [ ] `GET /api/ml/segments`
  - Output: Lista de clusters/perfis (dados agregados)
## 🎯 Resumo de Performance dos Modelos

| Modelo | Métrica Principal | Valor | Interpretação |
|--------|------------------|-------|---------------|
| **Forecast** | MAPE Médio | 7.8% | Excelente (< 10%) |
| **Clustering** | Silhouette Score | 0.357 | Aceitável (baseline) |
| **Recommender** | Avg Similarity | >0.6 | Bom (destinos similares) |

### Detalhamento por Modelo

**Forecast (por província)**:
- Luanda: MAPE 4.85% (melhor)
- Benguela: MAPE 8.23%
- Huíla: MAPE 9.56%
- Namibe: MAPE 7.14%
- Bié: MAPE 10.12%
- Cunene: MAPE 6.89%

**Clustering (distribuição)**:
- Relaxante Tradicional: 35% (maior grupo)
- Aventureiro Explorador: 30% (combinando 2 clusters)
- Cultural Urbano: 20%
- Negócios & Lazer: 15%

**Recommender (exemplos de similaridade)**:
- Praias (beach): 0.6 - 0.8 entre si
- Cultura (culture): 0.65 - 0.71 entre si
- Natureza (nature): 0.48 - 0.75 entre si

---

## 🎯 Próximos Passos Imediatos (Ordem Sugerida)

### Curto Prazo (1-2 semanas)
1. **Implementar testes automatizados** para os 3 modelos ML
2. **Criar endpoints CRUD** para Users e Destinations
3. **Adicionar logging estruturado** em todos os services
4. **Documentação Swagger/OpenAPI** completa

### Médio Prazo (1 mês)
1. **Monitoramento de drift** para modelo de forecast
2. **Coletar logs de interação** dos usuários (cliques, bookings)
3. **Re-treinar clustering** com dados reais quando >100 usuários
4. **A/B testing** para validar recomendações

### Longo Prazo (3-6 meses)
1. **Collaborative Filtering** para recommender (quando houver dados de interação)
2. **Sentiment Analysis** em reviews
3. **Auto-retraining** periódico dos modelos
4. **Deploy em produção** com Docker + CI/CD

---

---

## 📝 Notas Técnicas Importantes

### Configuração Atual
- **Python:** 3.11
- **Framework:** FastAPI 0.99.0
- **ORM:** SQLAlchemy 2.0.23 (async)
- **DB Driver:** asyncpg 0.28.0 (para app) + psycopg 3.1.8 (opcional)
- **Migrations:** Alembic 1.11.1
- **Database:** NeonDB (Postgres cloud)

### DATABASE_URL
```
postgresql://neondb_owner:npg_3aSeQW0qTPju@ep-cold-king-adyr1oj3-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

### Ajustes Feitos para Alembic + AsyncPG
- Removido parâmetro `channel_binding` (não suportado por asyncpg)
- Convertido `sslmode=require` para `ssl=require`
- Configurado `alembic/env.py` para usar async engine

---

## 🚀 Como Executar Agora

```bash
# 1. Ativar venv
source .venv/bin/activate

# 2. Instalar dependências (se ainda não fez)
pip install -r requirements.txt

# 3. Verificar que DB tem as tabelas
python3 scripts/check-tables-async.py

# 4. Iniciar servidor FastAPI
make start
# ou
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. Testar
curl http://localhost:8000/
curl http://localhost:8000/api/health

# 6. Ver documentação automática
# Abrir no browser: http://localhost:8000/docs
```

---

## 💡 Dicas para Desenvolvimento

1. **Use o FastAPI docs:** Acesse `/docs` para ver a API interativa
2. **Migrations:** Sempre que alterar models, rode:
   ```bash
   export DATABASE_URL="..." && alembic revision --autogenerate -m "descrição"
   export DATABASE_URL="..." && alembic upgrade head
   ```
3. **Seed data:** Rode apenas uma vez para popular BD inicial
4. **Testes:** Use pytest com `pytest -v` para ver detalhes

---

**Próximo passo recomendado:** Começar pela implementação do CRUD de Users (tarefa 4 da checklist).
