# 🤖 Guia de Treinamento e Registro dos Modelos ML

## 📋 Índice
1. [Pré-requisitos](#pré-requisitos)
2. [Visão Geral dos Modelos](#visão-geral-dos-modelos)
3. [Comando Rápido (Tudo de uma vez)](#comando-rápido)
4. [Comandos Individuais](#comandos-individuais)
5. [Verificação e Testes](#verificação-e-testes)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Pré-requisitos

### 1. Verificar ambiente
```bash
# Verificar se está no diretório correto
pwd  # Deve estar em: /home/rsambing/Projects/Wenda/backend-ml

# Verificar se .env existe
cat .env | grep DATABASE_URL
```

### 2. Verificar tabelas do banco
```bash
# Verificar se tabelas ML existem
python3 scripts/check-ml-tables.py

# Contar registros
python3 scripts/count_records.py

# Ver estatísticas
python3 scripts/view_database_stats.py
```

### 3. Verificar dados necessários

Para treinar os modelos, você precisa ter:
- ✅ **Destinations** (mínimo 10-20 destinos) → para recomendações
- ✅ **Tourism Statistics** (dados históricos) → para previsão e clustering
- ⚠️ Se não tiver dados, use: `python3 scripts/populate_database.py`

---

## 🎯 Visão Geral dos Modelos

### 1. 🎯 Modelo de Recomendações (Content-Based)
- **Script**: `train_recommender.py`
- **Entrada**: Tabela `destinations`
- **Algoritmo**: TF-IDF + Cosine Similarity
- **Saída**: 
  - `recommender_similarity_matrix.npy`
  - `recommender_features.npy`
  - `recommender_tfidf.joblib`
  - `recommender_scaler.joblib`
  - `recommender_metadata.json`

### 2. 👥 Modelo de Clustering (Perfis de Viajantes)
- **Script**: `train_clustering.py`
- **Entrada**: Tabela `tourism_statistics`
- **Algoritmo**: K-Means Clustering
- **Saída**:
  - `clustering_model.joblib`
  - `clustering_scaler.joblib`
  - `clustering_metadata.json`

### 3. 📈 Modelo de Previsão (Forecast)
- **Script**: `train_forecast_baseline.py`
- **Entrada**: Tabela `tourism_statistics`
- **Algoritmo**: Random Forest Regressor (por província)
- **Saída**:
  - `forecast_Luanda.joblib`
  - `forecast_Benguela.joblib`
  - ... (um por província)
  - `training_summary.json`

---

## 🚀 Comando Rápido

### Opção 1: Script Automatizado (RECOMENDADO)

```bash
# Dar permissão de execução
chmod +x scripts/train_and_register_all.sh

# Executar tudo de uma vez
bash scripts/train_and_register_all.sh
```

Este script irá:
1. ✅ Verificar dados no banco
2. ✅ Treinar os 3 modelos
3. ✅ Registrar no banco de dados
4. ✅ Testar endpoints

---

## 📝 Comandos Individuais

### Etapa 1: Treinar Cada Modelo

#### 1.1 Modelo de Recomendações
```bash
python3 scripts/train_recommender.py
```

**Saída esperada:**
```
🚀 Training Content-Based Recommendation Model
═══════════════════════════════════════════════

📊 Fetching destinations from database...
✅ Loaded 35 destinations

🔧 Creating content features...
   • Text features (TF-IDF): 500 dimensions
   • Category features: 4 categories
   • Province features: 13 provinces
   • Rating features: normalized

✅ Combined features: 35 destinations × 518 features

🧮 Computing similarity matrix...
✅ Similarity matrix computed: (35, 35)

💾 Saving model artifacts...
✅ Model saved to models/

🎉 Training complete!
```

#### 1.2 Modelo de Clustering
```bash
python3 scripts/train_clustering.py
```

**Saída esperada:**
```
🚀 Training Tourist Segmentation Model (Clustering)
════════════════════════════════════════════════════

📊 Fetching tourism statistics...
✅ Loaded 120 records

🔧 Feature engineering...
✅ Created features: (120, 8)

🧮 Training K-Means clustering...
✅ Identified 3 tourist segments

💾 Saving model...
✅ Model saved!
```

#### 1.3 Modelo de Previsão
```bash
python3 scripts/train_forecast_baseline.py
```

**Saída esperada:**
```
🚀 Training Tourism Forecast Models
════════════════════════════════════

📊 Loading data...
✅ Loaded 120 records from 13 provinces

🎯 Training models by province...
   ✓ Luanda: R²=0.85, MAE=125.3
   ✓ Benguela: R²=0.82, MAE=98.7
   ...

💾 Saving models...
✅ 13 models saved!
```

---

### Etapa 2: Registrar Modelos no Banco

```bash
python3 scripts/register_models.py
```

**Saída esperada:**
```
🚀 Registering Trained Models in Database
══════════════════════════════════════════

📊 Connecting to database...
✅ Connected!

📝 Registering models...
   ✅ Registered: forecast_Luanda (v1.0.0)
   ✅ Registered: forecast_Benguela (v1.0.0)
   ...
   ✅ Registered: clustering_kmeans (v1.0.0)
   ✅ Registered: recommender_content (v1.0.0)

💾 Total registered: 15 models

🎉 All models registered successfully!
```

**O que este script faz:**
- Lê os arquivos de metadata dos modelos
- Insere registros na tabela `ml_models_registry`
- Armazena métricas, versão, algoritmo, data de treinamento

---

## ✅ Verificação e Testes

### 1. Verificar arquivos criados
```bash
# Listar modelos salvos
ls -lh models/

# Ver conteúdo dos metadados
cat models/recommender_metadata.json | jq '.'
cat models/clustering_metadata.json | jq '.'
cat models/training_summary.json | jq '.'
```

### 2. Verificar registros no banco
```bash
# Script Python
python3 -c "
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def check():
    load_dotenv()
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    models = await conn.fetch('SELECT * FROM ml_models_registry ORDER BY last_updated DESC')
    
    print(f'\n📊 Modelos registrados: {len(models)}\n')
    for m in models:
        print(f'  • {m[\"model_name\"]} v{m[\"version\"]} - {m[\"status\"]}')
    
    await conn.close()

asyncio.run(check())
"
```

### 3. Testar via API

#### Iniciar servidor
```bash
uvicorn app.main:app --reload
```

#### Testar endpoints (em outro terminal)
```bash
# Listar modelos disponíveis
curl http://localhost:8000/api/ml/models | jq '.'

# Testar recomendações
curl -X POST http://localhost:8000/api/ml/recommend-by-preferences \
  -H "Content-Type: application/json" \
  -d '{
    "preferences": {
      "categories": ["natural"],
      "provinces": ["Luanda"]
    },
    "limit": 5
  }' | jq '.'

# Testar previsão
curl -X POST http://localhost:8000/api/ml/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "province": "Luanda",
    "month": 12,
    "year": 2025
  }' | jq '.'

# Testar segmentação
curl -X POST http://localhost:8000/api/ml/segment-tourist \
  -H "Content-Type: application/json" \
  -d '{
    "user_behavior": {
      "avg_budget": 5000,
      "preferred_season": "summer",
      "travel_frequency": 3
    }
  }' | jq '.'
```

#### Ou usar o script de teste
```bash
bash scripts/test_trained_models.sh
```

---

## 🔧 Troubleshooting

### ❌ Erro: "No data found in tourism_statistics"

**Problema**: Tabela vazia  
**Solução**:
```bash
# Popular banco com dados de exemplo
python3 scripts/populate_database.py
```

---

### ❌ Erro: "Table 'destinations' does not exist"

**Problema**: Tabelas ML não existem  
**Solução**:
```bash
# Verificar tabelas
python3 scripts/check-ml-tables.py

# Se faltarem tabelas, adicione no backend CRUD usando o schema Prisma
# Ver: COPIAR-COLAR-PRISMA.md
```

---

### ❌ Erro: "Module 'sklearn' not found"

**Problema**: Dependências não instaladas  
**Solução**:
```bash
# Instalar dependências
pip install -r requirements.txt

# Ou instalar manualmente
pip install scikit-learn pandas numpy joblib
```

---

### ❌ Erro: "asyncpg.exceptions.InvalidPasswordError"

**Problema**: DATABASE_URL incorreta  
**Solução**:
```bash
# Verificar .env
cat .env | grep DATABASE_URL

# Testar conexão
python3 scripts/check-tables.py
```

---

### ⚠️ Aviso: "Low number of destinations (< 10)"

**Problema**: Poucos dados para treinar  
**Solução**:
```bash
# Adicionar mais destinos
python3 scripts/populate_database.py
```

---

### ❌ Erro ao registrar: "duplicate key value violates unique constraint"

**Problema**: Modelo já está registrado  
**Solução**:
```bash
# Deletar registros antigos primeiro
python3 -c "
import asyncio, asyncpg, os
from dotenv import load_dotenv

async def clean():
    load_dotenv()
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    await conn.execute('DELETE FROM ml_models_registry')
    print('✅ Registros deletados')
    await conn.close()

asyncio.run(clean())
"

# Depois registrar novamente
python3 scripts/register_models.py
```

---

## 📊 Estrutura de Arquivos após Treinamento

```
backend-ml/
├── models/
│   ├── recommender_similarity_matrix.npy
│   ├── recommender_features.npy
│   ├── recommender_tfidf.joblib
│   ├── recommender_scaler.joblib
│   ├── recommender_metadata.json
│   ├── clustering_model.joblib
│   ├── clustering_scaler.joblib
│   ├── clustering_metadata.json
│   ├── forecast_Luanda.joblib
│   ├── forecast_Benguela.joblib
│   ├── forecast_Namibe.joblib
│   └── training_summary.json
└── ...
```

---

## 🎯 Resumo dos Comandos

```bash
# OPÇÃO 1: Tudo de uma vez (RECOMENDADO)
bash scripts/train_and_register_all.sh

# OPÇÃO 2: Passo a passo
python3 scripts/train_recommender.py
python3 scripts/train_clustering.py
python3 scripts/train_forecast_baseline.py
python3 scripts/register_models.py

# Testar
uvicorn app.main:app --reload
bash scripts/test_trained_models.sh
```

---

## 📚 Documentação Adicional

- **Arquitetura ML**: Ver `docs/ml-architecture.md`
- **API Endpoints**: http://localhost:8000/docs
- **Schema do Banco**: `docs/db.txt`
- **Adaptações**: `ADAPTACOES-FEITAS.md`
