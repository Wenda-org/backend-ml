
# Apresentação Final — Plataforma Wenda (visão completa)

Este documento contém o roteiro para a apresentação da plataforma Wenda, cobrindo toda a solução: produto (frontend), backend (API), módulo ML, dados e operações.

Objetivo: apresentar a proposta de valor, arquitetura end-to-end, fluxo de dados, resultados iniciais e roadmap, com um demo curto mostrando integração entre frontend → API → ML → DB.

---

## Tempo sugerido e formato
- Duração total sugerida: 20–30 minutos
  - Apresentação (slides): 12–18 min
  - Demo ao vivo (end-to-end): 6–8 min
  - Perguntas: 3–4 min
- Público-alvo: stakeholders do produto, time de produto/engenharia, parceiros e investidores

---

## Estrutura de slides (ordem e conteúdo)
Cada item abaixo corresponde a 1 slide; alguns podem usar 2 slides quando indicado.

1) Slide 1 — Título & Equipe
- Título: "Wenda — Plataforma de Turismo Inteligente"
- Subtítulo: "Previsões, Recomendações e Segmentação para destinos em Angola"
- Nome da equipe, papeis e data

Notas do apresentador:
- Saudação rápida e apresentação da equipe
- Contextualizar objetivo da apresentação (mostrar plataforma completa e demo)

2) Slide 2 — Problema de Negócio & Oportunidade
- Problema: falta de previsibilidade na demanda e pouca personalização nas recomendações turísticas
- Oportunidade: aumentar ocupação, melhorar experiência do turista, apoiar operadores e roteiros locais

Notas:
- Use números e exemplos de sazonalidade (Dezembro, Julho)
- Ligar ao impacto em receita e operação de turismo

3) Slide 3 — Proposta de Valor da Plataforma
- O que a Wenda entrega: previsões, recomendações personalizadas, perfis de turistas, APIs fáceis de integrar
- Benefícios para operadores, turistas e governo/local

Notas:
- Exemplos de outcomes esperados (ex.: otimizar preços, campanhas locais)

4) Slide 4 — Visão do Produto (user journeys)
- Três jornadas rápidas: turista buscando destino, operador ajustando oferta, time de análise visualizando previsões
- Screenshots/fluxos (frontend → chamada API → resultados)

Notas:
- Mostrar como cada ator usa a plataforma e que valor ganho

5) Slide 5 — Arquitetura End-to-End
- Diagrama com componentes: Frontend (web/app), Backend API (FastAPI), ML service (módulo), Database (NeonDB), Jobs (training), Migrations (Alembic), Observability (logs/metrics), CI/CD

Notas:
- Explicar por que cada componente foi escolhido (escalabilidade, custo, facilidade de integração)

6) Slide 6 — Esquema de Dados & Principais Tabelas
- Tabelas: users, destinations, tourism_statistics, ml_models_registry, ml_predictions, recommendations_log
- Exemplo de dados usados para treinar/modelar (colunas chave)

Notas:
- Mostrar a relação entre dados operacionais e dados para ML

7) Slide 7 — API & Integrações
- Endpoints principais expostos para consumo por frontend/outros backends
  - `GET /api/ml/health`
  - `POST /api/ml/forecast`
  - `POST /api/ml/recommend`
  - `GET /api/ml/segments`
- SDKs / contratos de integração (ex.: JSON payloads)

Notas:
- Reforçar que a API é desacoplada e pode ser consumida por multiple clients

8) Slide 8 — Experiência do Frontend (exemplos)
- Mockups / screenshots da interface do turista e do painel do operador (se existirem)
- Como a UI consome recomendações e previsões

Notas:
- Se não houver frontend pronto, mostrar wireframes e explicar integrações

9) Slide 9 — Estratégia ML (o que está implementado agora)
- Implementação inicial (baseline): média histórica + sazonalidade para forecast; filtros e ranking por rating para recommend; perfis pré-definidos para segments
- Planos para modelos reais: Prophet/SARIMA, content-based, collaborative, model registry

Notas:
- Explicar trade-off entre protótipo rápido e modelos completos

10) Slide 10 — Dados & Resultados Iniciais
- Números do dataset de demonstração: 6 users, 23 destinos, 216 registros (2022-2024)
- Exemplos de previsões e recomendações (screenshots ou saídas JSON)

Notas:
- Mostrar uma previsão e uma recomendação com interpretações de negócio

11) Slide 11 — Demo End-to-End (o que será mostrado)
- Roteiro do demo: iniciar servidor → frontend (ou curl) → request forecast → request recommend → mostrar logs/DB
- Tempo estimado: 6–8 minutos

Notas:
- Avisar a audiência que o demo mostra integração real entre componentes

12) Slide 12 — Operações e Segurança
- Como gerenciamos migrations, credenciais, backups, deploys
- Observability: logs, métricas, saúde do sistema

Notas:
- Mencionar práticas recomendadas para produção (secrets manager, monitoring)

13) Slide 13 — Roadmap e Prioridades
- Curto prazo: treinar modelos reais, adicionar testes, criar SDKs
- Médio prazo: modelo híbrido de recomendação, CI/CD, cache de previsões
- Longo prazo: monitoramento em produção, A/B testing, integração com parceiros

14) Slide 14 — Métricas de Sucesso & KPIs
- MAE/MAPE para forecast, CTR/revenue lift para recomendações, latência da API, adoção pelo usuário

15) Slide 15 — Riscos, Mitigações e Próximos Passos
- Riscos: dados insuficientes, custos, complexidade de integração
- Mitigações: fallbacks, monitoramento, priorização incremental

16) Slide 16 — Perguntas e Contato
- Informações de contato do time, link para repositório e documentação

---

## Roteiro do Demo End-to-End (passo-a-passo)
Objetivo: demonstrar um fluxo real entre frontend → API → ML → DB.

Pré-requisitos (local):

```bash
# ativar venv
source .venv/bin/activate

# configurar DB (Neon) na env
export DATABASE_URL="postgresql://neondb_owner:...@neon.tech/neondb?sslmode=require&channel_binding=require"

# popular dados (se necessário)
python3 scripts/seed_data.py
```

Passos do demo:

1. Iniciar servidor backend:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. (Opcional) Iniciar frontend local ou abrir mockup com link que consome a API

3. Demonstrar chamadas end-to-end (via curl ou frontend):

```bash
# Health
curl http://localhost:8000/api/ml/health | jq

# Forecast
curl -X POST http://localhost:8000/api/ml/forecast \
  -H "Content-Type: application/json" \
  -d '{"province":"Luanda","month":12,"year":2025}' | jq

# Recommend
curl -X POST http://localhost:8000/api/ml/recommend \
  -H "Content-Type: application/json" \
  -d '{"preferences":{"categories":["beach"]},"limit":5}' | jq

# Ver logs / requests no terminal do backend e DB
```

Notas do apresentador durante o demo:
- Mostrar que a UI faz a chamada e consome o resultado (se houver frontend)
- Explicar cada parte da resposta e implicação para o negócio

---

## Assets e Material de Apoio
- Screenshots necessários:
  - Arquitetura (diagrama)
  - Swagger UI (`/docs`)
  - Resultado de `POST /api/ml/forecast` (JSON)
  - Resultado de `POST /api/ml/recommend` (JSON)
  - Painel/Mockup do frontend mostrando recomendações

Sugestão de pasta para assets:
```
docs/assets/presentation/
```

---

## Checklist de Pré-Apresentação
- [ ] Validar acesso ao NeonDB e variáveis de ambiente
- [ ] Rodar `python3 scripts/seed_data.py` se DB estiver vazio
- [ ] Iniciar backend com `uvicorn`
- [ ] Preparar screenshots na pasta `docs/assets/presentation/`
- [ ] Testar demo uma vez antes da apresentação

---

## Observações e opções adicionais
- Posso gerar os slides em formatos variados:
  - `reveal.js` (Markdown → slides HTML)
  - PowerPoint (`.pptx`) a partir do Markdown
  - PDF exportado do reveal.js
- Também posso gerar um diagrama SVG da arquitetura (se quiser, informe preferências)

Diga como prefere: gerar slides automaticamente (qual formato) ou apenas ajustar o roteiro (tempo/ênfase) e eu procedo.
