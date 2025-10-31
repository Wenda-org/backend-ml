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

Como iniciar (desenvolvimento com Docker)
1. Copie `.env.example` para `.env` e ajuste se necessário.
2. Construir e subir serviços:

```bash
docker compose up --build
```

3. Aceder à API em `http://localhost:8000` e à documentação automática OpenAPI em `http://localhost:8000/docs`.

Conexão com NeonDB / produção
- Para produção, use a variável `DATABASE_URL` com a connection string fornecida pelo Neon. No `docker-compose` usamos um Postgres local apenas para dev.

Rotas principais (esqueleto)
- GET / -> status básico
- GET /api/health -> status da aplicação
- POST /api/predict -> inferência (payload: features) — endpoint placeholder que será ligado ao serviço de modelos

Próximos passos recomendados
1. Definir o contrato exato do payload de inferência (features esperadas e formato do output).
2. Implementar cargas e versionamento de modelos (joblib / MLflow) em `app/services`.
3. Adicionar migrations (Alembic) e scripts de inicialização da DB.
4. Criar testes unitários para a API e para as funções de preprocessamento.

Licença & Contribuição
- Este repositório é a base inicial — sinta-se à vontade para abrir issues/PRs com melhorias.
