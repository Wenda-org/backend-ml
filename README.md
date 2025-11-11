# 🚀 Wenda ML Backend

> **Backend de Machine Learning** para o projeto Wenda — plataforma de turismo de Angola  
> API RESTful construída com **FastAPI** + **PostgreSQL** (NeonDB) + **Scikit-learn**

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![ML](https://img.shields.io/badge/ML-Scikit--learn-orange.svg)](https://scikit-learn.org/)

---

## 📋 Índice

1. [Visão Geral](#-visão-geral)
2. [Arquitetura](#-arquitetura)
3. [Modelos ML](#-modelos-ml-implementados)
4. [Estrutura do Projeto](#-estrutura-do-projeto)
5. [Setup & Instalação](#-setup--instalação)
6. [Endpoints da API](#-endpoints-da-api)
7. [Como Usar](#-como-usar)
8. [Documentação](#-documentação)
9. [Desenvolvimento](#-desenvolvimento)

---

## 🎯 Visão Geral

O **Wenda ML Backend** é o módulo de inteligência artificial do projeto Wenda, responsável por:

- 📊 **Previsão de Visitantes** — Forecasting para planejamento turístico
- 🎯 **Segmentação de Turistas** — Clustering de perfis de viajantes
- 💡 **Recomendação Inteligente** — Sistema de recomendação personalizada de destinos

### Tecnologias Principais

- **FastAPI** — Framework web moderno e rápido
- **PostgreSQL** — Banco de dados relacional (NeonDB em produção)
- **Scikit-learn** — Biblioteca de Machine Learning
- **SQLAlchemy** — ORM assíncrono
- **Alembic** — Gerenciamento de migrations

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                      MOBILE & WEB APPS                       │
│              (React Native + React/Next.js)                  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FASTAPI ML BACKEND                        │
├──────────────┬──────────────┬──────────────┬────────────────┤
│   Forecast   │  Clustering  │ Recommender  │  CRUD/Auth     │
│   Service    │   Service    │   Service    │   Endpoints    │
└──────┬───────┴──────┬───────┴──────┬───────┴────────┬───────┘
       │              │              │                │
       ▼              ▼              ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│                     TRAINED ML MODELS                        │
│  • RandomForest (6)  • K-Means (1)  • TF-IDF + Cosine (1)  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    POSTGRESQL DATABASE                       │
│   • users  • destinations  • tourism_statistics              │
│   • ml_models_registry  • ml_predictions  • recommendations │
└─────────────────────────────────────────────────────────────┘
```

### Fluxo de Dados

1. **Mobile/Web** faz request HTTP para `/api/ml/*`
2. **FastAPI** recebe e valida os dados (Pydantic schemas)
3. **Service Layer** processa a lógica de negócio
4. **ML Models** realizam inferência (predict/transform)
5. **Database** armazena resultados e logs
6. **Response** retorna JSON formatado ao cliente

---

## 🤖 Modelos ML Implementados

### 1. 📊 Forecast — Previsão de Visitantes

**Algoritmo:** RandomForest Regressor  
**Objetivo:** Prever número de visitantes futuros por província  
**Performance:** MAPE médio de **7.8%**

- **6 modelos** treinados (1 por província)
- Features: trend temporal, sazonalidade, ocupação hoteleira, rating
- Output: Previsão mensal com intervalo de confiança

**Arquivos:**
```
models/
  forecast_Luanda.joblib
  forecast_Benguela.joblib
  ... (6 modelos)
  training_summary.json
```

### 2. 🎯 Clustering — Segmentação de Turistas

**Algoritmo:** K-Means (5 clusters)  
**Objetivo:** Identificar perfis de viajantes  
**Performance:** Silhouette score de **0.357**

- **5 segmentos** identificados:
  1. Negócios & Lazer (15%)
  2. Aventureiro Explorador (30%)
  3. Relaxante Tradicional (35%)
  4. Cultural Urbano (20%)
- Features: budget, trip duration, preferences (beach, culture, nature, etc.)

**Arquivos:**
```
models/
  clustering_kmeans.joblib
  clustering_scaler.joblib
  clustering_metadata.json
```

### 3. 💡 Recommender — Sistema de Recomendação

**Algoritmo:** Content-Based Filtering (TF-IDF + Cosine Similarity)  
**Objetivo:** Recomendar destinos personalizados  
**Performance:** Similaridade média **>0.6**

- **23 destinos** na base de conhecimento
- Features: TF-IDF (descrição), categoria, província, rating
- Matriz de similaridade **23×23**

**Arquivos:**
```
models/
  recommender_similarity_matrix.npy
  recommender_features.npy
  recommender_tfidf.joblib
  recommender_scaler.joblib
  recommender_metadata.json
```

---

## 📁 Estrutura do Projeto

```
backend-ml/
├── app/                          # Código da aplicação
│   ├── main.py                   # Entry point FastAPI
│   ├── database.py               # Config SQLAlchemy + conexão DB
│   ├── models.py                 # SQLAlchemy models (User, Destination, etc.)
│   ├── api/                      # Endpoints da API
│   │   ├── routes.py             # Routes principais
│   │   ├── ml.py                 # Endpoints ML (forecast, recommend, segments)
│   │   ├── users.py              # CRUD Users
│   │   └── destinations.py       # CRUD Destinations
│   └── services/                 # Lógica de negócio
│       ├── forecast.py           # ForecastService (carregar modelo, prever)
│       ├── clustering.py         # ClusteringService (segmentar usuários)
│       └── recommender.py        # RecommenderService (recomendar destinos)
│
├── models/                       # Modelos ML treinados (.joblib, .npy)
│   ├── forecast_*.joblib         # 6 modelos RandomForest
│   ├── clustering_*.joblib       # K-Means + scaler
│   ├── recommender_*.joblib      # TF-IDF + similarity matrix
│   └── *.json                    # Metadata de cada modelo
│
├── scripts/                      # Scripts utilitários
│   ├── train_forecast.py         # Treina modelo de forecast
│   ├── train_clustering.py       # Treina modelo de clustering
│   ├── train_recommender.py      # Treina sistema de recomendação
│   ├── register_models.py        # Registra modelos no BD
│   ├── seed_data.py              # Popula BD com dados de exemplo
│   └── check-tables-async.py     # Verifica tabelas do BD
│
├── migrations/                   # Alembic migrations
│   └── versions/                 # Histórico de migrations
│
├── docs/                         # Documentação
│   ├── INTEGRACAO_MOBILE_WEB.md  # Como integrar no mobile/web
│   ├── GUIA_RAPIDO_ML.md         # Guia rápido dos modelos ML
│   ├── ESTADO_ATUAL.md           # Status atual do projeto
│   └── API.md                    # Documentação dos endpoints
│
├── .env.example                  # Variáveis de ambiente (template)
├── requirements.txt              # Dependências Python
├── Dockerfile                    # Container Docker
├── Makefile                      # Comandos úteis (dev, build, etc.)
└── README.md                     # Este arquivo
```

### 🔍 Onde Mexer em Cada Caso

| Você quer... | Arquivo a editar |
|--------------|------------------|
| **Adicionar endpoint** | `app/api/routes.py` ou `app/api/ml.py` |
| **Criar novo modelo SQLAlchemy** | `app/models.py` |
| **Modificar lógica ML** | `app/services/forecast.py` (ou clustering/recommender) |
| **Treinar novo modelo** | `scripts/train_*.py` |
| **Alterar schema do BD** | Criar migration: `alembic revision -m "desc"` |
| **Adicionar dependência** | `requirements.txt` + `pip install` |
| **Popular dados** | `scripts/seed_data.py` |
| **Configurar variáveis** | `.env` |

---

## 🚀 Setup & Instalação

### Pré-requisitos

- **Python 3.11+**
- **PostgreSQL** (ou acesso ao NeonDB)
- **Git**

### 1️⃣ Clone o Repositório

```bash
git clone https://github.com/Wenda-org/backend-ml.git
cd backend-ml
```

### 2️⃣ Configure Variáveis de Ambiente

```bash
cp .env.example .env
```

Edite `.env` e configure:

```bash
DATABASE_URL="postgresql+asyncpg://user:password@host:5432/wenda_db"
SECRET_KEY="sua-chave-secreta-aqui"
ENVIRONMENT="development"
```

> **Produção (NeonDB):**  
> `DATABASE_URL="postgresql+asyncpg://user:pass@ep-xxx.neon.tech/wenda?sslmode=require"`

### 3️⃣ Criar Ambiente Virtual & Instalar Dependências

```bash
# Usar Makefile (recomendado)
make install

# Ou manualmente
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 4️⃣ Executar Migrations

```bash
# Criar tabelas no banco
alembic upgrade head

# Ou usar script wrapper
python3 scripts/run_migrations.py
```

### 5️⃣ Popular Dados de Exemplo

```bash
export DATABASE_URL="postgresql+asyncpg://..."
python3 scripts/seed_data.py
```

**Dados inseridos:**
- 6 usuários (tourists, operators, admin)
- 23 destinos turísticos
- 2,172 registros de estatísticas (2022-2024)

### 6️⃣ Treinar Modelos ML

```bash
# Forecast
python3 scripts/train_forecast.py

# Clustering
python3 scripts/train_clustering.py

# Recommender
python3 scripts/train_recommender.py

# Registrar todos no BD
python3 scripts/register_models.py
```

### 7️⃣ Iniciar o Servidor

```bash
# Modo desenvolvimento (auto-reload)
make dev

# Ou manualmente
uvicorn app.main:app --reload --port 8000
```

🎉 **API rodando em:** `http://localhost:8000`  
📚 **Documentação interativa:** `http://localhost:8000/docs`

---

## 📡 Endpoints da API

### Base URL

- **Dev:** `http://localhost:8000`
- **Prod:** `https://api.wenda.ao`

### Endpoints Principais

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `GET` | `/` | Status da API | ❌ |
| `GET` | `/api/health` | Health check geral | ❌ |
| `GET` | `/api/ml/health` | Health check ML | ❌ |
| `POST` | `/api/ml/forecast` | Previsão de visitantes | ❌ |
| `GET` | `/api/ml/segments` | Segmentos de turistas | ❌ |
| `POST` | `/api/ml/recommend` | Recomendações personalizadas | ❌ |
| `GET` | `/api/ml/models` | Listar modelos ML | ❌ |
| `GET` | `/api/users` | Listar usuários | ✅ |
| `POST` | `/api/users` | Criar usuário | ❌ |
| `GET` | `/api/destinations` | Listar destinos | ❌ |
| `POST` | `/api/destinations` | Criar destino | ✅ |

> **Nota:** Endpoints marcados com ✅ requerem autenticação JWT (em desenvolvimento)

### 📊 Exemplo: Previsão de Visitantes

**Request:**
```bash
curl -X POST http://localhost:8000/api/ml/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "destination_id": "164a0127-06b4-47a1-b9c2-3475caa82305",
    "forecast_months": 12
  }'
```

**Response:**
```json
{
  "destination_id": "164a0127-06b4-47a1-b9c2-3475caa82305",
  "destination_name": "Fortaleza de São Miguel",
  "province": "Luanda",
  "forecast": [
    {
      "month": "2025-12",
      "predicted_visitors": 15234,
      "confidence_interval": {"min": 14102, "max": 16366}
    }
  ],
  "total_predicted": 189234,
  "model_version": "v1.0.0-rf-trained"
}
```

### 🎯 Exemplo: Segmentos de Turistas

**Request:**
```bash
curl http://localhost:8000/api/ml/segments
```

**Response:**
```json
{
  "segments": [
    {
      "id": 2,
      "name": "Relaxante Tradicional",
      "percentage": 35.0,
      "description": "Busca praias, descanso e boa gastronomia",
      "characteristics": {
        "budget_level": "medium",
        "avg_trip_duration": 6,
        "top_preferences": ["beach", "gastronomy"]
      }
    }
  ],
  "total_segments": 5,
  "model_version": "v1.0.0-kmeans"
}
```

### 💡 Exemplo: Recomendações

**Request:**
```bash
curl -X POST http://localhost:8000/api/ml/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-uuid",
    "preferences": {
      "categories": ["beach", "nature"],
      "provinces": ["Luanda"]
    },
    "limit": 5
  }'
```

**Response:**
```json
{
  "recommendations": [
    {
      "destination_id": "ecc5f3f9-0a61-4063-8e8c-094f79f5e2a8",
      "name": "Ilha do Mussulo",
      "province": "Luanda",
      "category": "beach",
      "rating_avg": 4.7,
      "score": 0.876,
      "reason": "Baseado em suas preferências de praia"
    }
  ],
  "total_recommendations": 5,
  "model_version": "v1.0.0-content"
}
```

---

## 💻 Como Usar

### Para Desenvolvedores Frontend

1. **Consulte a documentação de integração:**  
   📱 [`docs/INTEGRACAO_MOBILE_WEB.md`](docs/INTEGRACAO_MOBILE_WEB.md)

2. **Exemplos de código:**
   - React Native: Veja seção "Integração Mobile"
   - React/Next.js: Veja seção "Integração Web"

3. **Teste os endpoints:**  
   Use a documentação interativa em `http://localhost:8000/docs`

### Para Cientistas de Dados

1. **Treinar novos modelos:**
   ```bash
   cd scripts/
   python3 train_forecast.py      # Modifica forecast
   python3 train_clustering.py    # Modifica clustering
   python3 train_recommender.py   # Modifica recommender
   ```

2. **Registrar modelos atualizados:**
   ```bash
   python3 scripts/register_models.py
   ```

3. **Avaliar performance:**
   - Métricas salvas em `models/*_metadata.json`
   - Visualizar em `http://localhost:8000/api/ml/models`

### Para DevOps

1. **Build Docker:**
   ```bash
   make build
   docker run -p 8000:8000 --env-file .env wenda-ml-backend
   ```

2. **Deploy:**
   - Configure `DATABASE_URL` para NeonDB
   - Configure `SECRET_KEY` para produção
   - Use `ENVIRONMENT=production`

---

## 📚 Documentação

| Documento | Descrição |
|-----------|-----------|
| [`docs/INTEGRACAO_MOBILE_WEB.md`](docs/INTEGRACAO_MOBILE_WEB.md) | **Como integrar** no mobile e web |
| [`docs/GUIA_RAPIDO_ML.md`](docs/GUIA_RAPIDO_ML.md) | **Guia completo** dos modelos ML |
| [`docs/ESTADO_ATUAL.md`](docs/ESTADO_ATUAL.md) | **Status atual** do projeto |
| [`docs/RESUMO_CLUSTERING_RECOMMENDER.md`](docs/RESUMO_CLUSTERING_RECOMMENDER.md) | **Detalhes técnicos** clustering + recommender |
| [`/docs`](http://localhost:8000/docs) | **Swagger UI** (API interativa) |
| [`/redoc`](http://localhost:8000/redoc) | **ReDoc** (documentação alternativa) |

### Como Ver a Documentação Interativa

```bash
# Inicie o servidor
make dev

# Abra no navegador
http://localhost:8000/docs      # Swagger UI
http://localhost:8000/redoc     # ReDoc
```

**Swagger UI permite:**
- ✅ Testar endpoints diretamente
- ✅ Ver schemas de request/response
- ✅ Validar payloads
- ✅ Copiar exemplos de código

---

## 🛠️ Desenvolvimento

### Comandos Makefile

```bash
make install      # Instalar dependências
make dev          # Rodar em modo dev (auto-reload)
make test         # Executar testes (pytest)
make lint         # Lint com flake8/black
make format       # Formatar código (black)
make clean        # Limpar arquivos temporários
make build        # Build Docker image
make docker-run   # Rodar container
```

### Executar Testes

```bash
# Instalar dependências de teste
pip install pytest pytest-asyncio httpx

# Rodar todos os testes
pytest

# Rodar com coverage
pytest --cov=app tests/

# Rodar testes específicos
pytest tests/test_ml_endpoints.py
```

### Criar Nova Migration

```bash
# Edite app/models.py (adicione/modifique models)

# Gere migration
alembic revision --autogenerate -m "descrição da mudança"

# Aplique migration
alembic upgrade head
```

### Adicionar Novo Endpoint

1. **Crie/edite arquivo em `app/api/`:**
   ```python
   # app/api/my_endpoint.py
   from fastapi import APIRouter
   
   router = APIRouter()
   
   @router.get("/my-route")
   async def my_function():
       return {"message": "Hello"}
   ```

2. **Registre no `app/main.py`:**
   ```python
   from app.api.my_endpoint import router as my_router
   
   app.include_router(my_router, prefix="/api", tags=["my-tag"])
   ```

### Adicionar Novo Modelo ML

1. **Crie script de treinamento em `scripts/train_my_model.py`**
2. **Salve modelo em `models/my_model.joblib`**
3. **Crie service em `app/services/my_model.py`**
4. **Adicione endpoint em `app/api/ml.py`**
5. **Registre modelo:** `python3 scripts/register_models.py`

---

## 🧪 Testes

### Estrutura de Testes

```
tests/
├── test_api.py              # Testes de endpoints gerais
├── test_ml_endpoints.py     # Testes de endpoints ML
├── test_forecast_service.py # Testes do ForecastService
├── test_clustering_service.py
└── test_recommender_service.py
```

### Exemplo de Teste

```python
# tests/test_ml_endpoints.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_get_segments():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/ml/segments")
        assert response.status_code == 200
        data = response.json()
        assert "segments" in data
        assert data["total_segments"] == 5
```

---

## 📊 Monitoramento

### Métricas dos Modelos

```bash
# Ver todos os modelos registrados
curl http://localhost:8000/api/ml/models

# Health check ML
curl http://localhost:8000/api/ml/health
```

### Logs

```bash
# Ver logs em tempo real
tail -f logs/app.log

# Logs do uvicorn
uvicorn app.main:app --reload --log-level debug
```

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/minha-feature`
3. Commit: `git commit -m 'Adiciona minha feature'`
4. Push: `git push origin feature/minha-feature`
5. Abra um Pull Request

---

## 📝 Notas Importantes

### Modelos ML

- **Todos os modelos** são carregados **sob demanda** (lazy loading)
- **Cache em memória** para evitar recarregamentos
- **Fallback gracioso** se modelo não disponível
- **Versionamento** via `model_version` no response

### Performance

- Endpoints ML são **assíncronos**
- Conexões DB via **pool de conexões**
- Cache de **1h** para segmentos
- Cache de **30min** para recomendações

### Segurança

- ⚠️ **Auth JWT em desenvolvimento** (ainda não implementado)
- ⚠️ **CORS aberto** em dev (restrinja em prod)
- ✅ **Validação** via Pydantic schemas
- ✅ **SQL injection** prevenido via SQLAlchemy

---

## 🐛 Troubleshooting

### Erro: "DATABASE_URL not set"

```bash
export DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db"
# Ou adicione em .env
```

### Erro: "Model file not found"

```bash
# Treine os modelos
python3 scripts/train_forecast.py
python3 scripts/train_clustering.py
python3 scripts/train_recommender.py
```

### Erro: "Table does not exist"

```bash
# Execute migrations
alembic upgrade head
```

### Erro de Import

```bash
# Reinstale dependências
pip install -r requirements.txt --upgrade
```

---

## 📞 Suporte

- **Issues:** [GitHub Issues](https://github.com/Wenda-org/backend-ml/issues)
- **Email:** dev@wenda.ao
- **Docs:** [docs.wenda.ao](https://docs.wenda.ao)

---

## 📄 Licença

Este projeto é licenciado sob a [MIT License](LICENSE).

---

## ✨ Créditos

Desenvolvido pela equipe **Wenda** 🇦🇴

- **Backend ML:** [Time de Data Science]
- **Integração:** [Time de Desenvolvimento]
- **Design:** [Time de UX/UI]

---

**Última atualização:** 11 de Novembro de 2025  
**Versão:** v1.0.0
6. Cache de previsões frequentes

Licença & Contribuição
- Este repositório é a base inicial — sinta-se à vontade para abrir issues/PRs com melhorias.
