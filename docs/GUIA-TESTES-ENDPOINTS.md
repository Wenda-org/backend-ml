# 📚 Guia Completo de Testes - Endpoints ML Wenda

> **Documentação dos Endpoints de Machine Learning do Backend Wenda**  
> Versão: 1.0.0 | Data: 12 de Novembro de 2025

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Configuração Inicial](#configuração-inicial)
3. [Endpoints Disponíveis](#endpoints-disponíveis)
   - [Health Check](#1-health-check)
   - [Listar Modelos](#2-listar-modelos)
   - [Previsão de Visitantes](#3-previsão-de-visitantes-forecast)
   - [Recomendações Personalizadas](#4-recomendações-personalizadas)
   - [Segmentos de Turistas](#5-segmentos-de-turistas-clustering)
4. [Conceitos de Machine Learning](#conceitos-de-machine-learning)
5. [Exemplos de Testes Completos](#exemplos-de-testes-completos)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

O **Wenda ML Backend** oferece APIs de Machine Learning para:
- 📊 **Previsão de demanda turística** (Forecasting)
- 🎯 **Recomendações personalizadas** (Content-Based Filtering)
- 👥 **Segmentação de perfis** (Clustering)

**Base URL**: `http://localhost:8000/api/ml`

---

## ⚙️ Configuração Inicial

### 1. Iniciar o Servidor

```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Iniciar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Ou em background
uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/uvicorn.log 2>&1 &
```

### 2. Verificar Status

```bash
curl http://localhost:8000/
```

**Resposta esperada:**
```json
{
  "service": "wenda-ml-backend",
  "status": "ok"
}
```

### 3. Acessar Documentação Interativa

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📡 Endpoints Disponíveis

---

### 1. Health Check

**Verifica o status do serviço e disponibilidade dos modelos ML.**

#### 📍 Endpoint
```
GET /api/ml/health
```

#### 🎯 Propósito
Monitoramento de saúde do serviço, útil para:
- Health checks de infraestrutura (Kubernetes, Docker)
- Validação de modelos carregados
- Status operacional do sistema

#### 📥 Parâmetros
Nenhum

#### 📤 Resposta

```json
{
  "status": "healthy",
  "module": "ml",
  "endpoints": ["forecast", "recommend", "segments", "models"],
  "trained_models": 19,
  "model_status": "trained models available",
  "timestamp": "2025-11-12T17:47:26.596592"
}
```

#### 🧪 Teste

```bash
curl -s http://localhost:8000/api/ml/health | python3 -m json.tool
```

#### ✅ Validações
- `status` deve ser "healthy"
- `trained_models` > 0 indica modelos disponíveis
- `endpoints` lista todos os endpoints funcionais

---

### 2. Listar Modelos

**Lista todos os modelos ML registrados no sistema com suas métricas.**

#### 📍 Endpoint
```
GET /api/ml/models
```

#### 🎯 Propósito
Auditoria e monitoramento dos modelos:
- Versões ativas de cada modelo
- Métricas de performance (MAE, MAPE, Silhouette Score)
- Algoritmos utilizados
- Data de treinamento

#### 📥 Parâmetros
Nenhum

#### 📤 Resposta

```json
{
  "models": [
    {
      "model_type": "forecast",
      "model_name": "forecast_Luanda",
      "version": "v1.0.0-rf-trained",
      "algorithm": "RandomForestRegressor",
      "metrics": {
        "mae": 10688.03,
        "mape": 228.02,
        "test_samples": 12
      },
      "status": "active",
      "trained_on": "2025-11-12"
    }
  ],
  "total_models": 20,
  "by_type": {
    "forecast": 18,
    "clustering": 1,
    "recommender": 1
  },
  "generated_at": "2025-11-12T17:28:12.447411"
}
```

#### 🧪 Teste

```bash
curl -s "http://localhost:8000/api/ml/models" | python3 -m json.tool | head -50
```

#### 📊 Métricas Explicadas

| Métrica | Descrição | Ideal |
|---------|-----------|-------|
| **MAE** | Mean Absolute Error - Erro médio absoluto | Quanto menor, melhor |
| **MAPE** | Mean Absolute Percentage Error - Erro percentual | < 20% é excelente |
| **test_samples** | Número de amostras de teste | Quanto mais, melhor |
| **silhouette_score** | Qualidade dos clusters (clustering) | 0.5-1.0 é bom |

---

### 3. Previsão de Visitantes (Forecast)

**Prevê o número de visitantes para uma província em um mês/ano específico.**

#### 📍 Endpoint
```
POST /api/ml/forecast
```

#### 🎯 Propósito
**Forecasting de séries temporais** para planejamento turístico:
- Estimativa de demanda futura
- Planejamento de capacidade hoteleira
- Alocação de recursos turísticos
- Identificação de alta/baixa temporada

#### 🤖 Conceitos de ML

**Algoritmo**: Random Forest Regressor

**Como funciona:**
1. **Características temporais**: Mês, ano, tendências históricas
2. **Sazonalidade**: Padrões que se repetem (verão, inverno, feriados)
3. **Ensemble Learning**: Combina múltiplas árvores de decisão para maior precisão
4. **Intervalo de Confiança**: Margem de erro da previsão (lower/upper bounds)

**Vantagens:**
- ✅ Captura relações não-lineares complexas
- ✅ Robusto a outliers
- ✅ Não requer normalização de dados
- ✅ Fornece estimativas de incerteza

#### 📥 Request Body

```json
{
  "province": "Luanda",
  "month": 12,
  "year": 2025
}
```

**Parâmetros:**
- `province` (string, obrigatório): Nome da província
  - Válidos: Luanda, Benguela, Huíla, Namibe, Malanje, Huambo
- `month` (int, obrigatório): Mês (1-12)
- `year` (int, obrigatório): Ano (2024-2030)

#### 📤 Resposta

```json
{
  "province": "Luanda",
  "month": 12,
  "year": 2025,
  "predicted_visitors": 5555,
  "confidence_interval": {
    "lower": 0,
    "upper": 15447
  },
  "model_version": "v1.0.0-rf-trained",
  "generated_at": "2025-11-12T17:28:12.610566"
}
```

**Campos de Resposta:**
- `predicted_visitors`: Previsão central (valor mais provável)
- `confidence_interval`: 
  - `lower`: Limite inferior (cenário pessimista)
  - `upper`: Limite superior (cenário otimista)
- `model_version`: Versão do modelo usado (para auditoria)

#### 🧪 Testes

**Teste 1: Luanda - Alta Temporada**
```bash
curl -s -X POST "http://localhost:8000/api/ml/forecast" \
  -H "Content-Type: application/json" \
  -d '{
    "province": "Luanda",
    "month": 12,
    "year": 2025
  }' | python3 -m json.tool
```

**Teste 2: Benguela - Meia Temporada**
```bash
curl -s -X POST "http://localhost:8000/api/ml/forecast" \
  -H "Content-Type: application/json" \
  -d '{
    "province": "Benguela",
    "month": 6,
    "year": 2026
  }' | python3 -m json.tool
```

**Teste 3: Huíla - Planejamento Anual**
```bash
curl -s -X POST "http://localhost:8000/api/ml/forecast" \
  -H "Content-Type: application/json" \
  -d '{
    "province": "Huíla",
    "month": 3,
    "year": 2026
  }' | python3 -m json.tool
```

#### ⚠️ Erros Possíveis

```json
{
  "detail": "Província inválida. Use uma de: Luanda, Benguela, Huila, Namibe, Cunene, Malanje"
}
```

---

### 4. Recomendações Personalizadas

**Sugere destinos turísticos baseado em preferências do usuário.**

#### 📍 Endpoint
```
POST /api/ml/recommend
```

#### 🎯 Propósito
**Sistema de Recomendação Content-Based** para:
- Personalização da experiência do usuário
- Descoberta de novos destinos
- Matching entre preferências e características dos destinos
- Aumento de engajamento e conversões

#### 🤖 Conceitos de ML

**Algoritmo**: Content-Based Filtering com TF-IDF + Cosine Similarity

**Como funciona:**
1. **TF-IDF (Term Frequency-Inverse Document Frequency)**
   - Analisa descrições dos destinos
   - Extrai palavras-chave importantes
   - Cria "impressão digital" textual de cada destino

2. **Feature Engineering**
   - Categoria (praia, cultura, natureza)
   - Província (localização)
   - Rating (qualidade)
   - Descrição (características únicas)

3. **Cosine Similarity**
   - Mede similaridade entre destinos (0-1)
   - 1.0 = idênticos, 0.0 = completamente diferentes
   - Considera múltiplas dimensões simultaneamente

4. **Scoring Algorithm**
   ```
   Score = (similaridade × 0.6) + (rating_normalizado × 0.3) + (preferência_match × 0.1)
   ```

**Vantagens:**
- ✅ Não precisa de dados de outros usuários (cold start problem)
- ✅ Transparente - pode explicar por que recomendou
- ✅ Personalização baseada em conteúdo real
- ✅ Escala bem com muitos itens

#### 📥 Request Body

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "preferences": {
    "categories": ["beach", "nature"],
    "budget": "medium",
    "provinces": ["Luanda", "Benguela"]
  },
  "limit": 5
}
```

**Parâmetros:**
- `user_id` (UUID, opcional): ID do usuário (para logging)
- `preferences` (object, obrigatório):
  - `categories` (array, opcional): ["beach", "culture", "nature", "adventure", "gastronomy"]
  - `budget` (string, opcional): "low", "medium", "high"
  - `provinces` (array, opcional): Lista de províncias preferidas
- `limit` (int, opcional): Número de recomendações (1-50, padrão: 10)

#### 📤 Resposta

```json
{
  "recommendations": [
    {
      "destination_id": "130ff0c2-51c9-4a57-94de-69825f589436",
      "name": "Praia Morena",
      "province": "Benguela",
      "category": "beach",
      "description": "",
      "rating": 4.8,
      "score": 0.96,
      "reason": "Matches your interest in beach | Highly rated destination | Located in Benguela"
    }
  ],
  "model_version": "v1.0.0-content-based-trained",
  "generated_at": "2025-11-12T17:50:19.209270"
}
```

**Campos de Resposta:**
- `score`: Relevância (0-1, quanto maior melhor)
- `reason`: Explicação legível da recomendação
- `rating`: Avaliação dos usuários (0-5 estrelas)

#### 🧪 Testes

**Teste 1: Preferências Específicas (Praia + Natureza)**
```bash
curl -s -X POST "http://localhost:8000/api/ml/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "preferences": {
      "categories": ["beach", "nature"],
      "provinces": ["Luanda", "Benguela"]
    },
    "limit": 5
  }' | python3 -m json.tool
```

**Teste 2: Top Destinos (Sem Filtros)**
```bash
curl -s -X POST "http://localhost:8000/api/ml/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "preferences": {},
    "limit": 10
  }' | python3 -m json.tool
```

**Teste 3: Aventura em Províncias Remotas**
```bash
curl -s -X POST "http://localhost:8000/api/ml/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "preferences": {
      "categories": ["adventure", "nature"],
      "provinces": ["Namibe", "Cunene"]
    },
    "limit": 3
  }' | python3 -m json.tool
```

**Teste 4: Cultura e Gastronomia Urbana**
```bash
curl -s -X POST "http://localhost:8000/api/ml/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "preferences": {
      "categories": ["culture", "gastronomy"],
      "budget": "high",
      "provinces": ["Luanda"]
    },
    "limit": 5
  }' | python3 -m json.tool
```

---

### 5. Segmentos de Turistas (Clustering)

**Identifica perfis/clusters de turistas com comportamentos similares.**

#### 📍 Endpoint
```
GET /api/ml/segments
```

#### 🎯 Propósito
**Segmentação de Mercado** para:
- Identificação de personas de turistas
- Estratégias de marketing direcionadas
- Desenvolvimento de pacotes personalizados
- Compreensão do público-alvo

#### 🤖 Conceitos de ML

**Algoritmo**: K-Means Clustering

**Como funciona:**
1. **Feature Engineering**
   - Orçamento médio (low/medium/high)
   - Duração média de viagem (dias)
   - Tamanho do grupo (pessoas)
   - Frequência de viagens (vezes/ano)
   - Preferências (beach, culture, nature, adventure, gastronomy)

2. **Normalização**
   - StandardScaler: Todas as features na mesma escala
   - Evita que features com valores maiores dominem

3. **K-Means Algorithm**
   - Agrupa turistas em K=5 clusters
   - Minimiza distância intra-cluster
   - Maximiza distância inter-cluster

4. **Qualidade: Silhouette Score**
   - Mede coesão e separação dos clusters
   - -1 = péssimo, 0 = neutro, 1 = perfeito
   - > 0.5 = boa qualidade

**Clusters Identificados:**
1. **Negócios & Lazer** (15%): Alta renda, viagens curtas frequentes, gastronômico
2. **Aventureiro Explorador** (18.4%): Longa duração, natureza e aventura, média renda
3. **Relaxante Tradicional** (35%): Família, praia, média renda, baixa frequência
4. **Cultural Urbano** (20%): Cultura e gastronomia, cidades, média frequência
5. **Explorador de Longo Prazo** (11.6%): Aventura, grupos grandes, planejamento extenso

#### 📥 Parâmetros
Nenhum

#### 📤 Resposta

```json
{
  "segments": [
    {
      "segment_id": "cluster_0",
      "name": "Negócios & Lazer",
      "description": "Travelers with high budget, typically staying 4 days. Strong preference for gastronomy and culture. Travel 6 times per year in groups of 1.",
      "typical_destinations": ["Luanda", "Benguela", "Lunda Norte"],
      "avg_budget": "high",
      "percentage": 15.0,
      "characteristics": [
        "Budget: high",
        "Avg trip: 4 days",
        "Group size: 1 people",
        "Travels 5.5 times/year",
        "Top preferences: gastronomy, culture"
      ]
    }
  ],
  "total_segments": 5,
  "model_version": "v1.0.0-kmeans",
  "generated_at": "2025-11-12T17:47:41.284078"
}
```

**Campos de Resposta:**
- `segment_id`: Identificador único do cluster
- `name`: Nome descritivo do perfil
- `description`: Características principais
- `typical_destinations`: Destinos preferidos deste segmento
- `avg_budget`: Faixa de orçamento
- `percentage`: % do total de turistas neste segmento
- `characteristics`: Lista detalhada de atributos

#### 🧪 Teste

```bash
curl -s "http://localhost:8000/api/ml/segments" | python3 -m json.tool
```

#### 📊 Uso Prático dos Segmentos

**Marketing Direcionado:**
```bash
# Identificar segmento
curl -s "http://localhost:8000/api/ml/segments" | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
for seg in data['segments']:
    if seg['name'] == 'Aventureiro Explorador':
        print(f\"Destinos para anunciar: {', '.join(seg['typical_destinations'])}\")
        print(f\"Budget médio: {seg['avg_budget']}\")
"
```

---

## 🧠 Conceitos de Machine Learning

### 1. Supervised Learning (Forecast)

**Definição**: Aprende com dados históricos rotulados para prever valores futuros.

**No Wenda:**
- **Entrada**: Província, mês, ano, dados históricos
- **Saída**: Número de visitantes previsto
- **Aprendizado**: Padrões sazonais, tendências, eventos históricos

**Métricas de Avaliação:**
- **MAE**: Erro médio em número de visitantes
- **MAPE**: Erro percentual (mais interpretável)

---

### 2. Content-Based Filtering (Recommend)

**Definição**: Recomenda itens similares aos que o usuário gosta, baseado em características.

**No Wenda:**
- **Entrada**: Preferências do usuário (categorias, localização)
- **Saída**: Destinos ranqueados por relevância
- **Aprendizado**: Similaridade entre descrições e características

**Técnicas:**
- **TF-IDF**: Vetorização de texto
- **Cosine Similarity**: Medida de similaridade
- **Feature Scaling**: Normalização de ratings

---

### 3. Unsupervised Learning (Clustering)

**Definição**: Descobre padrões e grupos naturais em dados não rotulados.

**No Wenda:**
- **Entrada**: Comportamentos de turistas (orçamento, preferências, frequência)
- **Saída**: 5 clusters/personas distintos
- **Aprendizado**: Agrupamento por similaridade comportamental

**Técnicas:**
- **K-Means**: Algoritmo de clustering por centroides
- **Silhouette Score**: Métrica de qualidade dos clusters
- **StandardScaler**: Normalização de features

---

## 🧪 Exemplos de Testes Completos

### Script de Teste Automatizado

Crie um arquivo `test_all_endpoints.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:8000/api/ml"

echo "═══════════════════════════════════════════════════════════════"
echo "🧪 TESTANDO TODOS OS ENDPOINTS - WENDA ML"
echo "═══════════════════════════════════════════════════════════════"

# 1. Health Check
echo ""
echo "1️⃣  HEALTH CHECK"
curl -s "${BASE_URL}/health" | python3 -m json.tool | head -10

# 2. Listar Modelos
echo ""
echo "2️⃣  LISTAR MODELOS"
curl -s "${BASE_URL}/models" | python3 -m json.tool | head -30

# 3. Forecast - Luanda
echo ""
echo "3️⃣  FORECAST - LUANDA"
curl -s -X POST "${BASE_URL}/forecast" \
  -H "Content-Type: application/json" \
  -d '{"province": "Luanda", "month": 12, "year": 2025}' | python3 -m json.tool

# 4. Forecast - Benguela
echo ""
echo "4️⃣  FORECAST - BENGUELA"
curl -s -X POST "${BASE_URL}/forecast" \
  -H "Content-Type: application/json" \
  -d '{"province": "Benguela", "month": 6, "year": 2026}' | python3 -m json.tool

# 5. Recomendações com Filtros
echo ""
echo "5️⃣  RECOMENDAÇÕES - COM FILTROS"
curl -s -X POST "${BASE_URL}/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "preferences": {
      "categories": ["beach", "nature"],
      "provinces": ["Luanda", "Benguela"]
    },
    "limit": 3
  }' | python3 -m json.tool

# 6. Recomendações sem Filtros
echo ""
echo "6️⃣  RECOMENDAÇÕES - TOP DESTINOS"
curl -s -X POST "${BASE_URL}/recommend" \
  -H "Content-Type: application/json" \
  -d '{"preferences": {}, "limit": 5}' | python3 -m json.tool

# 7. Segmentos
echo ""
echo "7️⃣  SEGMENTOS DE TURISTAS"
curl -s "${BASE_URL}/segments" | python3 -m json.tool | head -40

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ TESTES CONCLUÍDOS"
echo "═══════════════════════════════════════════════════════════════"
```

**Executar:**
```bash
chmod +x test_all_endpoints.sh
./test_all_endpoints.sh
```

---

### Teste com Python (Requests)

Crie um arquivo `test_endpoints.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/ml"

def test_health():
    """Teste de health check"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"✅ Health Check: {response.json()['status']}")
    assert response.status_code == 200
    
def test_forecast():
    """Teste de previsão"""
    payload = {
        "province": "Luanda",
        "month": 12,
        "year": 2025
    }
    response = requests.post(f"{BASE_URL}/forecast", json=payload)
    data = response.json()
    print(f"✅ Forecast Luanda: {data['predicted_visitors']} visitantes")
    assert response.status_code == 200
    assert data['predicted_visitors'] > 0

def test_recommend():
    """Teste de recomendações"""
    payload = {
        "preferences": {
            "categories": ["beach"],
            "provinces": ["Benguela"]
        },
        "limit": 3
    }
    response = requests.post(f"{BASE_URL}/recommend", json=payload)
    data = response.json()
    print(f"✅ Recomendações: {len(data['recommendations'])} destinos")
    assert response.status_code == 200
    assert len(data['recommendations']) > 0

def test_segments():
    """Teste de segmentos"""
    response = requests.get(f"{BASE_URL}/segments")
    data = response.json()
    print(f"✅ Segmentos: {data['total_segments']} clusters identificados")
    assert response.status_code == 200
    assert data['total_segments'] == 5

if __name__ == "__main__":
    print("🧪 Executando testes...\n")
    test_health()
    test_forecast()
    test_recommend()
    test_segments()
    print("\n🎉 Todos os testes passaram!")
```

**Executar:**
```bash
pip install requests
python test_endpoints.py
```

---

## 🔧 Troubleshooting

### Erro: Connection Refused

```bash
curl: (7) Failed to connect to localhost port 8000: Connection refused
```

**Solução:**
```bash
# Verificar se servidor está rodando
ps aux | grep uvicorn

# Se não estiver, iniciar
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

### Erro: 404 Not Found

```json
{"detail": "Not Found"}
```

**Causa**: URL incorreta (faltando `/api` prefix)

**Solução:**
```bash
# ❌ Errado
curl http://localhost:8000/ml/health

# ✅ Correto
curl http://localhost:8000/api/ml/health
```

---

### Erro: Field Required

```json
{
  "detail": [
    {
      "loc": ["body", "preferences"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Causa**: Falta parâmetro obrigatório no request body

**Solução:**
```bash
# ❌ Errado
curl -X POST http://localhost:8000/api/ml/recommend -d '{"limit": 5}'

# ✅ Correto
curl -X POST http://localhost:8000/api/ml/recommend \
  -H "Content-Type: application/json" \
  -d '{"preferences": {}, "limit": 5}'
```

---

### Erro: Província Inválida

```json
{
  "detail": "Província inválida. Use uma de: Luanda, Benguela, Huila, Namibe, Cunene, Malanje"
}
```

**Causa**: Província não tem modelo treinado

**Solução**: Usar uma das províncias listadas

---

### Performance Lenta

**Diagnóstico:**
```bash
# Verificar modelos carregados
curl -s http://localhost:8000/api/ml/health | grep trained_models

# Verificar logs
tail -f /tmp/uvicorn.log
```

**Otimizações:**
- Usar `limit` menor em recomendações
- Cache de resultados frequentes
- Pré-computar similaridades

---

## 📊 Resumo de Validações

### Checklist de Testes

- [ ] **Health Check** retorna `status: "healthy"`
- [ ] **Modelos** listados corretamente (20 modelos)
- [ ] **Forecast** retorna previsão numérica válida
- [ ] **Forecast** inclui confidence interval
- [ ] **Recomendações** retorna lista de destinos
- [ ] **Recomendações** respeita filtros (categories, provinces)
- [ ] **Recomendações** ordenadas por score (0-1)
- [ ] **Segmentos** retorna 5 clusters
- [ ] **Segmentos** percentagens somam ~100%
- [ ] **Documentação** acessível em `/docs`

### Métricas de Qualidade Esperadas

| Modelo | Métrica | Valor Esperado |
|--------|---------|----------------|
| Forecast | MAE | < 5000 visitantes |
| Forecast | MAPE | < 100% |
| Clustering | Silhouette | > 0.3 |
| Recommender | Response time | < 500ms |

---

## 🎓 Referências e Recursos

### Documentação Técnica
- FastAPI Docs: https://fastapi.tiangolo.com
- Scikit-learn: https://scikit-learn.org
- Pandas: https://pandas.pydata.org

### Artigos sobre ML em Turismo
- Time Series Forecasting for Tourism Demand
- Content-Based Recommendation Systems
- Customer Segmentation with K-Means

### Ferramentas de Teste
- Postman: Testes interativos de API
- JMeter: Testes de carga
- pytest: Testes automatizados em Python

---

## 📝 Notas Finais

- **Versionamento**: Todos os modelos incluem `model_version` para rastreabilidade
- **Logs**: Recomendações são logadas em `recommendations_log` para análise
- **Retreinamento**: Modelos devem ser retreinados mensalmente com novos dados
- **Monitoramento**: Usar `/health` para health checks contínuos

---

**Última atualização**: 12 de Novembro de 2025  
**Versão do documento**: 1.0.0  
**Autor**: Equipa Wenda ML
