# 📋 Estado Atual do Projeto Wenda ML Backend

**Data:** 4 de Novembro de 2025  
**Status:** ✅ Base de dados criada com sucesso | 🚧 Endpoints em desenvolvimento

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
  - `destinations` - Destinos turísticos
  - `tourism_statistics` - Estatísticas históricas de turismo
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

### 4. Scripts Utilitários
- ✅ `scripts/db-async-check.py` - Verifica conexão DB
- ✅ `scripts/check-tables-async.py` - Lista todas as tabelas
- ✅ `scripts/run_migrations.py` - Executa migrations (wrapper para alembic)

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

**Payloads exemplo:**
```json
// POST /api/users
{
  "name": "João Silva",
  "email": "joao@example.com",
  "password": "senha123",
  "role": "tourist",
  "country": "Angola"
}

// Response
{
  "id": "uuid-here",
  "name": "João Silva",
  "email": "joao@example.com",
  "role": "tourist",
  "country": "Angola",
  "created_at": "2025-11-04T15:30:00Z"
}
```

#### 1.2 CRUD Destinations
**Arquivo:** `app/api/destinations.py` (criar)

Endpoints a implementar:
- [ ] `GET /api/destinations` - Listar destinos (filtros: province, category)
- [ ] `POST /api/destinations` - Criar novo destino
- [ ] `GET /api/destinations/{id}` - Obter destino por ID
- [ ] `PUT /api/destinations/{id}` - Atualizar destino
- [ ] `DELETE /api/destinations/{id}` - Deletar destino

**Payloads exemplo:**
```json
// POST /api/destinations
{
  "name": "Fortaleza de São Miguel",
  "province": "Luanda",
  "description": "Fortaleza histórica do século XVII",
  "latitude": -8.810,
  "longitude": 13.234,
  "category": "culture",
  "images": ["url1.jpg", "url2.jpg"]
}
```

---

### FASE 2: Endpoints ML (Prioridade Média)

#### 2.1 Endpoint de Previsão
**Arquivo:** `app/api/ml.py` (criar)

- [ ] `POST /api/ml/forecast`
  - Input: `{province, month, year}`
  - Output: `{predicted_visitors, confidence_interval, model_version}`
  - Nota: Criar placeholder que retorna valores simulados (modelo real vem depois)

**Exemplo:**
```json
// POST /api/ml/forecast
{
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
  - Nota: Retornar perfis hardcoded inicialmente

**Exemplo:**
```json
// GET /api/ml/segments
{
  "segments": [
    {
      "segment_id": "relaxante_tradicional",
      "name": "Relaxante Tradicional",
      "description": "Procura descanso e tranquilidade",
      "typical_destinations": ["Benguela", "Lobito"],
      "avg_budget": "medium",
      "percentage": 35
    },
    {
      "segment_id": "aventureiro_explorador",
      "name": "Aventureiro Explorador",
      "description": "Busca experiências únicas",
      "typical_destinations": ["Namibe", "Kissama"],
      "avg_budget": "medium-high",
      "percentage": 25
    }
  ]
}
```

---

### FASE 3: Dados de Seed (Alta Prioridade)

**Arquivo:** `scripts/seed_data.py` (criar)

Criar script que popula o BD com dados de exemplo:

#### 3.1 Users (5-10 exemplos)
```python
users = [
    {"name": "João Silva", "email": "joao@example.com", "role": "tourist", "country": "Angola"},
    {"name": "Maria Santos", "email": "maria@example.com", "role": "tourist", "country": "Portugal"},
    {"name": "Admin User", "email": "admin@wenda.ao", "role": "admin", "country": "Angola"},
    # ... mais 2-7 users
]
```

#### 3.2 Destinations (20-30 destinos principais)
```python
destinations = [
    # Luanda
    {"name": "Fortaleza de São Miguel", "province": "Luanda", "category": "culture", ...},
    {"name": "Ilha do Mussulo", "province": "Luanda", "category": "beach", ...},
    {"name": "Miradouro da Lua", "province": "Luanda", "category": "nature", ...},
    
    # Benguela
    {"name": "Praia Morena", "province": "Benguela", "category": "beach", ...},
    {"name": "Baía Azul", "province": "Benguela", "category": "beach", ...},
    
    # Namibe
    {"name": "Deserto do Namibe", "province": "Namibe", "category": "nature", ...},
    
    # Huíla
    {"name": "Serra da Leba", "province": "Huila", "category": "nature", ...},
    {"name": "Fenda da Tundavala", "province": "Huila", "category": "nature", ...},
    
    # ... mais destinos
]
```

#### 3.3 Tourism Statistics (dados históricos simulados)
```python
# Gerar dados mensais para 2022-2024 para províncias principais
# Exemplo: Luanda sempre com mais visitantes, sazonalidade em Dezembro/Julho
```

**Comandos:**
```bash
# Executar seed
python3 scripts/seed_data.py

# Verificar dados inseridos
python3 scripts/check-tables-async.py
```

---

### FASE 4: Documentação (Prioridade Média)

#### 4.1 Atualizar README.md
- [ ] Seção "Rotas disponíveis" com todos os endpoints
- [ ] Exemplos de uso com `curl` ou `httpie`
- [ ] Quick start guide atualizado
- [ ] Nota sobre seed data

#### 4.2 Atualizar `docs/back_summary.md`
- [ ] Listar todas as rotas implementadas
- [ ] Payloads de request e response para cada endpoint
- [ ] Notas sobre autenticação (futuro)
- [ ] Roadmap de funcionalidades ML

---

### FASE 5: Testes (Prioridade Baixa - mas importante)

**Arquivo:** `tests/test_api.py` (criar estrutura)

- [ ] Setup pytest e pytest-asyncio
- [ ] Teste para `GET /` (health check)
- [ ] Teste para `POST /api/users` (criar user)
- [ ] Teste para `GET /api/users` (listar users)
- [ ] Teste para `GET /api/destinations` (listar destinos)
- [ ] Teste para `POST /api/ml/forecast` (validar payload)

**Exemplo de teste:**
```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/users", json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "senha123",
            "role": "tourist",
            "country": "Angola"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
```

---

## 🎯 Próximos Passos Imediatos (Ordem Sugerida)

1. **Criar endpoints CRUD para Users** (`app/api/users.py`)
2. **Criar script de seed** (`scripts/seed_data.py`)
3. **Popular BD com dados de exemplo**
4. **Criar endpoints CRUD para Destinations** (`app/api/destinations.py`)
5. **Criar placeholders ML endpoints** (`app/api/ml.py`)
6. **Testar todos os endpoints** (manual ou com Postman/Insomnia)
7. **Documentar no README** com exemplos de uso
8. **Setup de testes básicos**

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
