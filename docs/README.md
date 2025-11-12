# 📚 Documentação - Wenda ML Backend

> **Backend de Machine Learning para a Plataforma de Turismo Wenda**  
> Versão: 1.0.0 | Última atualização: 12 de Novembro de 2025

---

## 🚀 Início Rápido

### Para começar imediatamente:
1. **[QUICK-START-ML.md](QUICK-START-ML.md)** - Comandos rápidos para treinar modelos
2. **[GUIA-TESTES-ENDPOINTS.md](GUIA-TESTES-ENDPOINTS.md)** - Testar todos os endpoints ML

### Para entender o projeto:
3. **[descricao-projecto.md](descricao-projecto.md)** - Visão geral do projeto Wenda

---

## 📖 Documentação por Categoria

### 🎯 Treinamento e Modelos ML

| Documento | Descrição | Quando Usar |
|-----------|-----------|-------------|
| **[QUICK-START-ML.md](QUICK-START-ML.md)** | Comandos rápidos para treinar todos os modelos | Quando quiser treinar rapidamente |
| **[GUIA-TREINAMENTO-ML.md](GUIA-TREINAMENTO-ML.md)** | Guia completo de treinamento passo a passo | Para entender o processo detalhadamente |
| **[MODELOS_ML.md](MODELOS_ML.md)** | Arquitetura e implementação dos modelos | Para entender como os modelos funcionam |
| **[CONCEITOS_ML_ESSENCIAIS.md](CONCEITOS_ML_ESSENCIAIS.md)** | Teoria de ML aplicada ao projeto | Para aprender os conceitos de ML |

### 🔌 API e Integração

| Documento | Descrição | Quando Usar |
|-----------|-----------|-------------|
| **[GUIA-TESTES-ENDPOINTS.md](GUIA-TESTES-ENDPOINTS.md)** | Documentação completa de todos os endpoints | Para testar e integrar com a API |
| **[INTEGRACAO_MOBILE_WEB.md](INTEGRACAO_MOBILE_WEB.md)** | Integração com React Native e React/Next.js | Para desenvolvedores frontend |
| **[how-it-works.md](how-it-works.md)** | Arquitetura geral do sistema | Para entender a arquitetura completa |

### 🗄️ Banco de Dados

| Documento | Descrição | Quando Usar |
|-----------|-----------|-------------|
| **[db.txt](db.txt)** | Schema Prisma atual (FONTE DA VERDADE) | Para ver a estrutura atual do BD |
| **[database-schema.md](database-schema.md)** | Documentação detalhada do schema | Para entender todas as tabelas |

### 📊 Estratégia e Planejamento

| Documento | Descrição | Quando Usar |
|-----------|-----------|-------------|
| **[descricao-projecto.md](descricao-projecto.md)** | Descrição completa do projeto Wenda | Para entender o objetivo do projeto |
| **[estrategia-dados-wenda.md](estrategia-dados-wenda.md)** | Estratégia de dados e ML | Para entender a estratégia de dados |
| **[documento-preparacao-dados.md](documento-preparacao-dados.md)** | Preparação e ETL de dados | Para processar dados brutos |
| **[perfis-viajantes-wenda.md](perfis-viajantes-wenda.md)** | Perfis de usuários (personas) | Para entender os tipos de turistas |

---

## 🎯 Fluxos Comuns

### 1️⃣ Novo Desenvolvedor

```bash
# 1. Ler descrição do projeto
docs/descricao-projecto.md

# 2. Entender o schema do banco
docs/db.txt
docs/database-schema.md

# 3. Treinar modelos
docs/QUICK-START-ML.md

# 4. Testar endpoints
docs/GUIA-TESTES-ENDPOINTS.md
```

### 2️⃣ Integração Frontend

```bash
# 1. Ver documentação da API
docs/GUIA-TESTES-ENDPOINTS.md

# 2. Exemplos de integração
docs/INTEGRACAO_MOBILE_WEB.md

# 3. Arquitetura do sistema
docs/how-it-works.md
```

### 3️⃣ Cientista de Dados / ML Engineer

```bash
# 1. Conceitos ML
docs/CONCEITOS_ML_ESSENCIAIS.md

# 2. Arquitetura dos modelos
docs/MODELOS_ML.md

# 3. Guia de treinamento
docs/GUIA-TREINAMENTO-ML.md

# 4. Estratégia de dados
docs/estrategia-dados-wenda.md
```

---

## 📊 Modelos ML Implementados

O sistema possui **3 modelos de Machine Learning** em produção:

| Modelo | Tipo | Algoritmo | Endpoint | Status |
|--------|------|-----------|----------|--------|
| **Forecast** | Regressão | Random Forest | `POST /api/ml/forecast` | ✅ Produção |
| **Recommender** | Content-Based | TF-IDF + Cosine Similarity | `POST /api/ml/recommend` | ✅ Produção |
| **Clustering** | Unsupervised | K-Means | `GET /api/ml/segments` | ✅ Produção |

Detalhes completos em: **[MODELOS_ML.md](MODELOS_ML.md)**

---

## 🔧 Estrutura de Arquivos

```
docs/
├── README.md                          # Este arquivo (índice geral)
│
├── 🚀 Início Rápido
│   ├── QUICK-START-ML.md             # Comandos rápidos
│   └── descricao-projecto.md         # Descrição do projeto
│
├── 🎯 Machine Learning
│   ├── GUIA-TREINAMENTO-ML.md        # Guia completo de treinamento
│   ├── MODELOS_ML.md                 # Arquitetura dos modelos
│   └── CONCEITOS_ML_ESSENCIAIS.md    # Teoria de ML
│
├── 🔌 API e Integração
│   ├── GUIA-TESTES-ENDPOINTS.md      # Documentação completa da API
│   ├── INTEGRACAO_MOBILE_WEB.md      # Exemplos de integração
│   └── how-it-works.md               # Arquitetura geral
│
├── 🗄️ Banco de Dados
│   ├── db.txt                        # Schema Prisma (atual)
│   └── database-schema.md            # Documentação detalhada
│
└── 📊 Estratégia
    ├── estrategia-dados-wenda.md     # Estratégia de dados
    ├── documento-preparacao-dados.md  # ETL e preparação
    └── perfis-viajantes-wenda.md     # Personas de usuários
```

---

## 🆘 Precisa de Ajuda?

### Problemas Comuns

| Problema | Solução | Documento |
|----------|---------|-----------|
| Modelos não treinam | Verificar DATABASE_URL e dados | [GUIA-TREINAMENTO-ML.md](GUIA-TREINAMENTO-ML.md) |
| Endpoints retornam erro | Verificar modelos treinados | [GUIA-TESTES-ENDPOINTS.md](GUIA-TESTES-ENDPOINTS.md) |
| Erro no schema | Verificar db.txt | [db.txt](db.txt) |
| Performance lenta | Ver otimizações | [INTEGRACAO_MOBILE_WEB.md](INTEGRACAO_MOBILE_WEB.md) |

### Contato

- **GitHub:** Wenda-org/backend-ml
- **Documentação Online:** Em breve

---

## 📝 Changelog da Documentação

### v1.0.0 (12 Nov 2025)
- ✅ Reorganização completa da documentação
- ✅ Remoção de 15 documentos duplicados/obsoletos
- ✅ Criação do README principal
- ✅ Consolidação de guias de treinamento
- ✅ Documentação completa de endpoints

### v0.9.0 (11 Nov 2025)
- ✅ GUIA-TESTES-ENDPOINTS.md criado
- ✅ INTEGRACAO_MOBILE_WEB.md criado
- ✅ Adaptações para novo schema

---

**Última atualização:** 12 de Novembro de 2025  
**Mantido por:** Equipe Wenda ML
