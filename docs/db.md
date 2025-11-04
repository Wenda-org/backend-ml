Excelente, Reinaldo 👏🏾 — agora vamos montar **a estrutura completa da base de dados da Wenda**, de forma **documentada e explicada**, cobrindo tanto o **backend CRUD (operacional)** quanto o **backend ML (analítico/preditivo)**.

A ideia é que tenhas uma visão **única e coesa do modelo de dados**, mostrando como a Wenda organiza informações de usuários, destinos, visitas, preferências, previsões e resultados de aprendizado de máquina.

---

# 🗂️ Estrutura da Base de Dados – Projeto **Wenda**

---

## 🧱 1️⃣ Visão Geral

A base de dados da Wenda é composta por **dois domínios principais**, integrados entre si:

| Domínio                  | Descrição                                                                                  | Tipo de Banco                        |
| ------------------------ | ------------------------------------------------------------------------------------------ | ------------------------------------ |
| **Wenda Core (CRUD)**    | Gerencia informações operacionais — usuários, destinos, reservas, feedbacks, eventos, etc. | **PostgreSQL + PostGIS**             |
| **Wenda ML (Analytics)** | Armazena datasets para treinamento, predições e resultados de modelos de Machine Learning. | **PostgreSQL / Parquet (analítico)** |

Esses dois bancos compartilham chaves e sincronizam dados via **pipelines ETL** (extração e transformação periódica).

---

## 🧩 2️⃣ Estrutura do **Wenda Core (CRUD)**

### 🧍‍♂️ Tabela `users`

Armazena informações básicas de usuários (turistas, operadores e administradores).

| Campo           | Tipo                                 | Descrição           |
| --------------- | ------------------------------------ | ------------------- |
| `id`            | UUID (PK)                            | Identificador único |
| `name`          | VARCHAR(100)                         | Nome completo       |
| `email`         | VARCHAR(120)                         | Email (único)       |
| `password_hash` | VARCHAR(255)                         | Hash da senha       |
| `role`          | ENUM('tourist', 'operator', 'admin') | Tipo de usuário     |
| `country`       | VARCHAR(80)                          | País de origem      |
| `created_at`    | TIMESTAMP                            | Data de registro    |

---

### 📍 Tabela `destinations`

Contém os destinos turísticos disponíveis.

| Campo         | Tipo                                                                  | Descrição                |
| ------------- | --------------------------------------------------------------------- | ------------------------ |
| `id`          | UUID (PK)                                                             | Identificador do destino |
| `name`        | VARCHAR(150)                                                          | Nome do destino          |
| `province`    | VARCHAR(100)                                                          | Província                |
| `description` | TEXT                                                                  | Descrição detalhada      |
| `latitude`    | FLOAT                                                                 | Coordenada geográfica    |
| `longitude`   | FLOAT                                                                 | Coordenada geográfica    |
| `category`    | ENUM('beach', 'culture', 'nature', 'business', 'gastronomy', 'other') | Tipo de destino          |
| `rating_avg`  | FLOAT                                                                 | Média de avaliação       |
| `images`      | JSONB                                                                 | URLs de imagens          |
| `created_at`  | TIMESTAMP                                                             | Data de criação          |

> ⚙️ *Usa extensão PostGIS para consultas geoespaciais (distância, raio, clusters).*

---

### 🗓️ Tabela `events`

Eventos e atividades turísticas.

| Campo            | Tipo                                                                    | Descrição           |
| ---------------- | ----------------------------------------------------------------------- | ------------------- |
| `id`             | UUID                                                                    | Identificador       |
| `destination_id` | UUID (FK → destinations.id)                                             | Local do evento     |
| `name`           | VARCHAR(120)                                                            | Nome do evento      |
| `start_date`     | DATE                                                                    | Início              |
| `end_date`       | DATE                                                                    | Fim                 |
| `description`    | TEXT                                                                    | Descrição           |
| `category`       | ENUM('festival', 'business', 'culture', 'music', 'gastronomy', 'other') | Tipo                |
| `created_at`     | TIMESTAMP                                                               | Registro no sistema |

---

### 💬 Tabela `reviews`

Avaliações de usuários sobre destinos e eventos.

| Campo            | Tipo                        | Descrição                                   |
| ---------------- | --------------------------- | ------------------------------------------- |
| `id`             | UUID                        | Identificador                               |
| `user_id`        | UUID (FK → users.id)        | Autor                                       |
| `destination_id` | UUID (FK → destinations.id) | Destino avaliado                            |
| `rating`         | INT                         | Nota (1–5)                                  |
| `comment`        | TEXT                        | Comentário                                  |
| `sentiment`      | FLOAT                       | Resultado da análise de sentimento (-1 a 1) |
| `created_at`     | TIMESTAMP                   | Data da avaliação                           |

---

### 🗺️ Tabela `itineraries`

Roteiros personalizados de viagem gerados para turistas.

| Campo          | Tipo                                | Descrição                      |
| -------------- | ----------------------------------- | ------------------------------ |
| `id`           | UUID                                | Identificador                  |
| `user_id`      | UUID (FK → users.id)                | Turista                        |
| `destinations` | JSONB                               | Lista de destinos recomendados |
| `start_date`   | DATE                                | Data de início                 |
| `end_date`     | DATE                                | Data de término                |
| `generated_by` | ENUM('manual', 'ml_recommendation') | Origem                         |
| `created_at`   | TIMESTAMP                           | Registro                       |

---

### 🧾 Tabela `service_requests`

Solicitações de serviços (guia, transporte, hospedagem, etc.)

| Campo            | Tipo                                                  | Descrição       |
| ---------------- | ----------------------------------------------------- | --------------- |
| `id`             | UUID                                                  | Identificador   |
| `user_id`        | UUID (FK → users.id)                                  | Solicitante     |
| `service_type`   | ENUM('guide', 'transport', 'hotel', 'other')          | Tipo de serviço |
| `destination_id` | UUID (FK → destinations.id)                           | Local           |
| `status`         | ENUM('pending', 'accepted', 'completed', 'cancelled') | Estado          |
| `created_at`     | TIMESTAMP                                             | Registro        |

---

## 🧠 3️⃣ Estrutura do **Wenda ML (Analytics)**

Esta base armazena dados tratados, features e resultados preditivos.

---

### 📊 Tabela `tourism_statistics`

Dados históricos do INE e de fontes oficiais.

| Campo               | Tipo         | Descrição                  |
| ------------------- | ------------ | -------------------------- |
| `id`                | SERIAL       | Identificador              |
| `province`          | VARCHAR(100) | Província                  |
| `month`             | INT          | Mês                        |
| `year`              | INT          | Ano                        |
| `domestic_visitors` | INT          | Visitantes nacionais       |
| `foreign_visitors`  | INT          | Visitantes estrangeiros    |
| `occupancy_rate`    | FLOAT        | Taxa de ocupação hoteleira |
| `avg_stay_days`     | FLOAT        | Duração média da estadia   |
| `created_at`        | TIMESTAMP    | Inserção no banco          |

---

### 🌦️ Tabela `weather_data`

Dados climáticos associados às regiões turísticas.

| Campo         | Tipo         | Descrição           |
| ------------- | ------------ | ------------------- |
| `id`          | SERIAL       | Identificador       |
| `province`    | VARCHAR(100) | Província           |
| `date`        | DATE         | Data                |
| `avg_temp`    | FLOAT        | Temperatura média   |
| `rainfall_mm` | FLOAT        | Precipitação        |
| `humidity`    | FLOAT        | Umidade             |
| `wind_speed`  | FLOAT        | Velocidade do vento |

---

### 💡 Tabela `ml_features`

Armazena *features* finais usadas no treinamento dos modelos.

| Campo             | Tipo         | Descrição                    |
| ----------------- | ------------ | ---------------------------- |
| `id`              | SERIAL       | Identificador                |
| `province`        | VARCHAR(100) | Província                    |
| `month`           | INT          | Mês                          |
| `year`            | INT          | Ano                          |
| `visitors_total`  | INT          | Total de visitantes (alvo)   |
| `avg_temp`        | FLOAT        | Temperatura média            |
| `rainfall_mm`     | FLOAT        | Precipitação                 |
| `events_count`    | INT          | Número de eventos            |
| `hotel_capacity`  | INT          | Capacidade hoteleira         |
| `economic_index`  | FLOAT        | Indicador econômico regional |
| `feature_version` | VARCHAR(20)  | Versão do dataset            |

---

### 🤖 Tabela `ml_predictions`

Registra previsões geradas pelos modelos.

| Campo                 | Tipo         | Descrição              |
| --------------------- | ------------ | ---------------------- |
| `id`                  | SERIAL       | Identificador          |
| `model_name`          | VARCHAR(100) | Nome do modelo         |
| `model_version`       | VARCHAR(20)  | Versão (ex: v1.2)      |
| `province`            | VARCHAR(100) | Província prevista     |
| `month`               | INT          | Mês                    |
| `year`                | INT          | Ano                    |
| `predicted_visitors`  | INT          | Resultado da previsão  |
| `confidence_interval` | JSONB        | Intervalo de confiança |
| `created_at`          | TIMESTAMP    | Data de execução       |

---

### 🧩 Tabela `ml_models_registry`

Controla metadados e métricas de cada modelo.

| Campo          | Tipo                         | Descrição                                  |
| -------------- | ---------------------------- | ------------------------------------------ |
| `id`           | SERIAL                       | Identificador                              |
| `model_name`   | VARCHAR(100)                 | Nome (forecast, recommend, segment, etc.)  |
| `version`      | VARCHAR(20)                  | Versão                                     |
| `algorithm`    | VARCHAR(100)                 | Algoritmo usado                            |
| `metrics`      | JSONB                        | Métricas de performance (RMSE, MAPE, etc.) |
| `status`       | ENUM('active', 'deprecated') | Estado atual                               |
| `trained_on`   | DATE                         | Data do treino                             |
| `last_updated` | TIMESTAMP                    | Última atualização                         |

---

### 📈 Tabela `recommendations_log`

Registra as recomendações servidas aos usuários (para análise posterior).

| Campo            | Tipo                        | Descrição                  |
| ---------------- | --------------------------- | -------------------------- |
| `id`             | SERIAL                      | Identificador              |
| `user_id`        | UUID (FK → users.id)        | Usuário                    |
| `destination_id` | UUID (FK → destinations.id) | Destino recomendado        |
| `score`          | FLOAT                       | Probabilidade ou afinidade |
| `model_version`  | VARCHAR(20)                 | Versão do modelo           |
| `created_at`     | TIMESTAMP                   | Data/hora da recomendação  |

---

## 🧭 4️⃣ Relações Principais

```
users ───< reviews >─── destinations
users ───< itineraries >─── destinations
destinations ───< events
users ───< recommendations_log
tourism_statistics + weather_data → ml_features → ml_predictions
ml_models_registry ───< ml_predictions
```

---

## ⚙️ 5️⃣ Considerações Técnicas

* **Banco principal:** PostgreSQL 16 com extensão **PostGIS** (para dados espaciais).
* **Data warehouse:** Tabelas analíticas exportadas para **Parquet** (usando pandas + DuckDB).
* **Versionamento de dados:** DVC e MLflow (para rastrear datasets e modelos).
* **Segurança:** criptografia de dados sensíveis (AES), backup automatizado.
* **Chaves primárias:** UUIDs no CRUD e SERIAL no ML (para performance).

---
