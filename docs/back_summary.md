# Resumo do Backend Python (Wenda ML)

Este documento resume o propósito, responsabilidades e endpoints iniciais do backend Python do projeto Wenda (serviço ML).

Resumo do projeto
- O backend serve modelos de Machine Learning (previsão de procura, segmentação e recomendação de POIs) e expõe APIs para consumo por front-end e outros serviços.

Responsabilidades do backend
- Expor endpoints REST para inferência (predição) e gestão de modelos.
- Fornecer dados limpos e agregados para dashboards (via queries à base Postgres/PostGIS).
- Implementar autenticação/autorização para endpoints administrativos (pendente).
- Orquestrar pipelines de ETL (ligação a Airflow ou jobs programados).
- Monitorização de saúde, métricas e logs.

Endpoints iniciais (esqueleto)
- GET / -> status do serviço
- GET /api/health -> status da app
- POST /api/predict -> inferência (payload: {"features": {...}})

Notas sobre DB e NeonDB
- Em desenvolvimento usamos Postgres local (via docker-compose). Para produção recomendamos NeonDB (serverless Postgres). Configure `DATABASE_URL` com a connection string do Neon.

Documentação adicional
- A documentação técnica e os documentos de preparação de dados estão em `docs/` e incluem: dados, estratégias e perfis de viajantes.
