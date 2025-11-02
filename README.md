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
