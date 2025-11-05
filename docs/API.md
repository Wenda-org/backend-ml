# 📚 Documentação da API - Wenda ML Backend

## 🌐 Base URL
```
http://localhost:8000
```

---

## 📋 Índice
1. [Health Checks](#health-checks)
2. [ML Endpoints - Previsões](#ml-forecast)
3. [ML Endpoints - Recomendações](#ml-recommend)
4. [ML Endpoints - Segmentação](#ml-segments)

---

## 🏥 Health Checks

### GET /
**Descrição:** Health check geral da API

**Response:**
```json
{
  "service": "wenda-ml-backend",
  "status": "ok"
}
```

**Exemplo curl:**
```bash
curl http://localhost:8000/
```

---

### GET /api/ml/health
**Descrição:** Status do módulo ML

**Response:**
```json
{
  "status": "healthy",
  "module": "ml",
  "endpoints": ["forecast", "recommend", "segments"],
  "model_status": "placeholder - using baseline algorithms",
  "timestamp": "2025-11-05T09:12:11.584528"
}
```

**Exemplo curl:**
```bash
curl http://localhost:8000/api/ml/health
```

---

## 📊 ML Endpoints - Previsões

### POST /api/ml/forecast
**Descrição:** Prevê número de visitantes para uma província/mês/ano

**Algoritmo atual (placeholder):**
- Busca dados históricos dos últimos 3 anos
- Calcula média do mesmo mês em anos anteriores
- Aplica tendência de crescimento (5% ao ano)
- Aplica sazonalidade (Dez e Jul/Ago são picos)
- Calcula intervalo de confiança (±15%)

**Request Body:**
```json
{
  "province": "Luanda",     // Províncias válidas: Luanda, Benguela, Huila, Namibe, Cunene, Malanje
  "month": 12,              // 1-12
  "year": 2025              // >= 2024
}
```

**Response:**
```json
{
  "province": "Luanda",
  "month": 12,
  "year": 2025,
  "predicted_visitors": 24515,
  "confidence_interval": {
    "lower": 20838,
    "upper": 28192
  },
  "model_version": "v0.1.0-baseline-avg",
  "generated_at": "2025-11-05T09:12:12.304118"
}
```

**Exemplo curl:**
```bash
curl -X POST http://localhost:8000/api/ml/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "province": "Luanda",
    "month": 12,
    "year": 2025
  }'
```

**Exemplo httpie:**
```bash
http POST localhost:8000/api/ml/forecast \
  province=Luanda month:=12 year:=2025
```

**Erros possíveis:**
- `400 Bad Request`: Província inválida ou mês/ano fora do intervalo

---

### POST /api/ml/forecast - Exemplo 2: Namibe em Julho

**Request:**
```bash
curl -X POST http://localhost:8000/api/ml/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "province": "Namibe",
    "month": 7,
    "year": 2026
  }'
```

**Response:**
```json
{
  "province": "Namibe",
  "month": 7,
  "year": 2026,
  "predicted_visitors": 2663,
  "confidence_interval": {
    "lower": 2264,
    "upper": 3062
  },
  "model_version": "v0.1.0-baseline-avg",
  "generated_at": "2025-11-05T09:12:16.273186"
}
```

---

## 🎯 ML Endpoints - Recomendações

### POST /api/ml/recommend
**Descrição:** Recomenda destinos personalizados baseado em preferências

**Algoritmo atual (placeholder):**
- Filtra destinos por categorias preferidas
- Filtra por províncias (se especificado)
- Ordena por rating + popularidade
- Retorna top N com scores calculados

**Request Body:**
```json
{
  "user_id": "uuid-opcional",    // UUID do usuário (opcional)
  "preferences": {
    "categories": ["beach", "culture"],   // Optional: culture, beach, nature
    "budget": "medium",                   // Optional: low, medium, high
    "provinces": ["Benguela", "Luanda"]   // Optional: filtro por províncias
  },
  "limit": 5                              // Número de recomendações (1-50, default: 10)
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "destination_id": "130ff0c2-51c9-4a57-94de-69825f589436",
      "name": "Praia Morena",
      "province": "Benguela",
      "category": "beach",
      "description": "Uma das praias mais bonitas de Angola, areia dourada e águas cristalinas.",
      "rating_avg": 4.8,
      "score": 0.96,
      "reason": "Matches your interest in beach | Highly rated destination"
    },
    {
      "destination_id": "ecc5f3f9-0a61-4063-8e8c-094f79f5e2a8",
      "name": "Ilha do Mussulo",
      "province": "Luanda",
      "category": "beach",
      "description": "Península de areia com 30km de extensão, praias paradisíacas...",
      "rating_avg": 4.7,
      "score": 0.89,
      "reason": "Matches your interest in beach | Highly rated destination"
    }
  ],
  "model_version": "v0.1.0-content-filter",
  "generated_at": "2025-11-05T09:12:13.123456"
}
```

**Exemplo curl (praias):**
```bash
curl -X POST http://localhost:8000/api/ml/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "preferences": {
      "categories": ["beach"],
      "budget": "medium"
    },
    "limit": 5
  }'
```

**Exemplo httpie (natureza + cultura):**
```bash
http POST localhost:8000/api/ml/recommend \
  preferences:='{"categories": ["nature", "culture"], "provinces": ["Huila", "Luanda"]}' \
  limit:=5
```

**Erros possíveis:**
- `404 Not Found`: Nenhum destino encontrado com as preferências fornecidas

---

## 👥 ML Endpoints - Segmentação

### GET /api/ml/segments
**Descrição:** Retorna perfis/clusters de turistas identificados

**Algoritmo atual (placeholder):**
- Perfis hardcoded baseados em `docs/perfis-viajantes-wenda.md`
- Futuramente será gerado por clustering (K-Means) sobre dados reais

**Response:**
```json
{
  "segments": [
    {
      "segment_id": "relaxante_tradicional",
      "name": "Relaxante Tradicional",
      "description": "Busca descanso e tranquilidade em ambientes familiares",
      "typical_destinations": ["Benguela", "Lobito", "Namibe"],
      "avg_budget": "medium",
      "percentage": 35.0,
      "characteristics": [
        "Prefere praias e resorts",
        "Viaja em família ou casal",
        "Média de 5-7 dias de estadia",
        "Orçamento médio: $100-200/dia"
      ]
    },
    {
      "segment_id": "aventureiro_explorador",
      "name": "Aventureiro Explorador",
      "description": "Procura experiências únicas e contato com natureza",
      "typical_destinations": ["Namibe", "Huíla", "Malanje"],
      "avg_budget": "medium-high",
      "percentage": 25.0,
      "characteristics": [
        "Interessado em natureza e aventura",
        "Viaja sozinho ou em grupos pequenos",
        "Média de 7-10 dias",
        "Orçamento: $150-300/dia"
      ]
    },
    {
      "segment_id": "cultural_historico",
      "name": "Cultural e Histórico",
      "description": "Interessado em patrimônio cultural e história",
      "typical_destinations": ["Luanda", "Benguela", "Lunda Norte"],
      "avg_budget": "medium",
      "percentage": 20.0,
      "characteristics": [
        "Visita museus e sítios históricos",
        "Viaja em casal ou grupos organizados",
        "Média de 4-6 dias",
        "Orçamento: $120-250/dia"
      ]
    },
    {
      "segment_id": "negocios_lazer",
      "name": "Negócios + Lazer",
      "description": "Combina viagens de negócios com turismo",
      "typical_destinations": ["Luanda", "Benguela", "Lubango"],
      "avg_budget": "high",
      "percentage": 15.0,
      "characteristics": [
        "Estadia em hotéis de negócios",
        "Viaja frequentemente",
        "Média de 3-5 dias",
        "Orçamento: $200-400/dia"
      ]
    },
    {
      "segment_id": "ecoturista",
      "name": "Ecoturista Consciente",
      "description": "Foco em sustentabilidade e preservação ambiental",
      "typical_destinations": ["Iona National Park", "Kissama", "Cunene"],
      "avg_budget": "medium-high",
      "percentage": 5.0,
      "characteristics": [
        "Prefere ecoturismo e safaris",
        "Viaja em grupos especializados",
        "Média de 7-14 dias",
        "Orçamento: $180-350/dia"
      ]
    }
  ],
  "total_segments": 5,
  "model_version": "v0.1.0-clustering-placeholder",
  "generated_at": "2025-11-05T09:12:33.578361"
}
```

**Exemplo curl:**
```bash
curl http://localhost:8000/api/ml/segments
```

**Exemplo httpie:**
```bash
http GET localhost:8000/api/ml/segments
```

---

## 🚀 Quick Start

### 1. Iniciar servidor
```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Exportar DATABASE_URL
export DATABASE_URL="postgresql://..."

# Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Acessar documentação interativa
```
http://localhost:8000/docs
```

A documentação interativa gerada pelo FastAPI permite testar todos os endpoints diretamente no navegador.

---

## 📝 Notas Importantes

### Status Atual (v0.1.0)
- ✅ Todos os endpoints implementados e funcionando
- ⚠️ **Modelos ML são placeholders** - usam algoritmos baseline simples
- ⚠️ Previsões baseadas em médias históricas, não em modelos treinados
- ⚠️ Recomendações baseadas em filtros simples, não em ML real

### Roadmap - Próximas Versões

**v0.2.0 - Modelos ML Reais:**
- Implementar SARIMA/Prophet para previsões de séries temporais
- Implementar content-based filtering para recomendações
- Adicionar clustering (K-Means) para segmentação real

**v0.3.0 - Melhorias:**
- Collaborative filtering nas recomendações
- Modelo híbrido (content + collaborative)
- Cache de previsões frequentes
- Métricas de performance dos modelos

**v0.4.0 - Produção:**
- Autenticação JWT
- Rate limiting
- Logging estruturado
- Monitoramento de performance
- Testes automatizados completos

---

## 🐛 Troubleshooting

### Erro: "Province inválida"
Certifique-se de usar uma das províncias válidas:
- Luanda
- Benguela
- Huila
- Namibe
- Cunene
- Malanje

### Erro: "Nenhum destino encontrado"
- Verifique se as categorias existem: `culture`, `beach`, `nature`
- Tente remover filtros de províncias
- Aumente o `limit` do request

### Erro de conexão ao BD
```bash
# Verifique se DATABASE_URL está configurada
echo $DATABASE_URL

# Verifique se consegue conectar ao NeonDB
python3 scripts/check-tables-async.py
```

---

## 📧 Suporte

Para questões sobre a API, consulte:
- 📄 Código fonte: `/home/rsambing/Projects/Wenda/backend-ml/app/api/ml.py`
- 📖 Docs do projeto: `/home/rsambing/Projects/Wenda/backend-ml/docs/`
- 🧪 Scripts de teste: `/home/rsambing/Projects/Wenda/backend-ml/scripts/test_ml_endpoints.sh`
