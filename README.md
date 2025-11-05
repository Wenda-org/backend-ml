# Wenda — Backend ML (FastAPI)

Resumo rápido
- Serviço backend Python para funcionalidades de Machine Learning do projeto Wenda (previsão, segmentação e recomendação).
- API construída com FastAPI; base de dados Postgres (em produção: NeonDB/Postgres).

O que incluí aqui (esqueleto inicial)
- API FastAPI mínima com endpoints de health e `/api/predict` (placeholder).
- Configuração de base de dados assíncrona (SQLAlchemy + asyncpg).
- Dockerfile e `docker-compose.yml` para ambiente de desenvolvimento com Postgres local.
- `requirements.txt` com dependências básicas (FastAPI, sqlalchemy, asyncpg, pandas, scikit-learn).
- `.env.example` com variáveis de ambiente essenciais.
- `docs/back_summary.md` com resumo do projecto e responsabilidades do backend.

Como iniciar (dev com Makefile)

Este repositório usa um `Makefile` para tarefas comuns (build de imagem, execução, dev rápido). A base de dados é externa — configure `DATABASE_URL` apontando para a sua instância Neon/Postgres.

1. Copie `.env.example` para `.env` e ajuste `DATABASE_URL` se preferir manter variáveis em ficheiro local:

```bash
cp .env.example .env
# edite .env e substitua DATABASE_URL pela connection string do Neon
```

2. Instalar dependências do ambiente local (opcional, para desenvolvimento sem Docker):

```bash
make install
```

3. Rodar em modo de desenvolvimento (uvicorn local, recarregamento automático):

```bash
make dev
```

4. Construir imagem Docker (opcional):

```bash
make build
```

5. Executar a app containerizada (irá usar `.env` se existir):

```bash
make docker-run
```

6. Verificar ligação à base de dados (usa `psycopg`):

```bash
export DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/dbname"
make db-check
```

OpenAPI / docs está disponível em `http://localhost:8000/docs` (quando a app estiver a correr).

Nota sobre NeonDB / produção
- Configure a variável `DATABASE_URL` para a connection string fornecida pelo Neon. O Makefile e a aplicação leem `DATABASE_URL` do ambiente ou de `.env`.

Rotas principais
- `GET /` → status básico
- `GET /api/health` → health check da aplicação
- `POST /api/predict` → inferência (payload: features) — endpoint placeholder legado

### 🤖 Endpoints ML (v0.1.0)
- `GET /api/ml/health` → status do módulo ML
- `POST /api/ml/forecast` → previsão de visitantes (província, mês, ano)
- `POST /api/ml/recommend` → recomendações personalizadas de destinos
- `GET /api/ml/segments` → perfis de turistas (clusters)

**📚 Documentação completa:** Ver [`docs/API.md`](docs/API.md) para exemplos detalhados de request/response.

**Dados de exemplo:**  
O banco de dados contém:
- 6 users (turistas, operadores, admin)
- 23 destinos turísticos (Luanda, Benguela, Huíla, Namibe, etc.)
- 216 registros de estatísticas (2022-2024, 6 províncias × 12 meses × 3 anos)

Para popular o BD:
```bash
export DATABASE_URL="postgresql://..."
python3 scripts/seed_data.py
```

Próximos passos

### ✅ Completo (v0.1.0)
1. ✅ Migrations Alembic criadas e executadas
2. ✅ Endpoints ML implementados (forecast, recommend, segments)
3. ✅ Dados de seed para desenvolvimento
4. ✅ Documentação da API

### 🚧 Em desenvolvimento
1. Implementar modelos ML reais (SARIMA/Prophet para previsões)
2. Content-based filtering para recomendações
3. Clustering real (K-Means) para segmentação
4. Testes automatizados (pytest)
5. Autenticação JWT
6. Cache de previsões frequentes

Licença & Contribuição
- Este repositório é a base inicial — sinta-se à vontade para abrir issues/PRs com melhorias.
