## 🧠 1️⃣ Conceitos Fundamentais de Machine Learning

Esses são os **conceitos que deves entender e saber explicar** — com exemplos, fórmulas básicas e aplicações no teu projeto:

| Conceito                                     | O que estudar                                                                  | Como se aplica no Wenda                                       |
| -------------------------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------- |
| **Tipos de aprendizado**                     | Supervisionado, não supervisionado, por reforço                                | Regressão (previsões), Clustering (segmentação), Recomendação |
| **Regressão**                                | Linear, Ridge, Lasso, XGBoost                                                  | Previsão de fluxo turístico                                   |
| **Classificação**                            | Logistic Regression, Random Forest, Gradient Boosting                          | Classificação de regiões emergentes                           |
| **Clustering**                               | K-Means, DBSCAN, PCA (redução de dimensionalidade)                             | Segmentação de perfis de turistas                             |
| **Séries Temporais**                         | ARIMA, Prophet, LSTM, decomposição de tendência/sazonalidade                   | Previsão de demanda turística ao longo do tempo               |
| **Sistemas de Recomendação**                 | Content-based, Collaborative Filtering, Modelos híbridos                       | Recomendação de destinos personalizados                       |
| **NLP (Processamento de Linguagem Natural)** | Tokenização, Bag of Words, TF-IDF, embeddings, análise de sentimento           | Interpretação de comentários e avaliações                     |
| **Feature Engineering**                      | Normalização, encoding, extração de features temporais, geográficas e textuais | Preparar dados antes de treinar modelos                       |
| **Avaliação de Modelos**                     | RMSE, MAE, R², F1-score, Precision, Recall, Silhouette Score                   | Escolher o melhor modelo e justificar decisões                |
| **Overfitting / Underfitting**               | Regularização, validação cruzada                                               | Garantir generalização dos modelos                            |

📘 **Recurso recomendado:**
Curso “Machine Learning Specialization” do Andrew Ng (Coursera) + “Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow” (livro base).

---

## ⚙️ 2️⃣ Tecnologias e Ferramentas Essenciais

Aqui estão os **pilares técnicos** que formam o teu backend ML (o que realmente vais programar):

| Área                             | Tecnologias                                   | O que aprender nelas                           |
| -------------------------------- | --------------------------------------------- | ---------------------------------------------- |
| **Linguagem base**               | Python 3.11+                                  | Tipagem, OOP, async, ambiente virtual, logging |
| **Bibliotecas ML**               | scikit-learn, XGBoost, Prophet, pandas, NumPy | Treinar e salvar modelos                       |
| **NLP**                          | NLTK, spaCy, Transformers (HuggingFace)       | Tokenização, embeddings, análise de sentimento |
| **APIs ML**                      | FastAPI                                       | Servir modelos como endpoints REST             |
| **Persistência de modelos**      | joblib, pickle, MLflow                        | Serializar e versionar modelos                 |
| **Monitoramento**                | MLflow, Prometheus, Grafana                   | Métricas de treino e produção                  |
| **Re-treinamento**               | Celery + Redis                                | Agendar treinos automáticos                    |
| **Controle de versões de dados** | DVC (Data Version Control)                    | Versionar datasets                             |
| **Testes e CI/CD**               | pytest, Docker, GitHub Actions                | Garantir estabilidade no deploy                |

---

## ☁️ 3️⃣ Infraestrutura e Deploy

Para defender tecnicamente o **backend ML**, tu precisas mostrar que sabes como ele roda em produção.

| Tema                     | O que dominar                          | Ferramentas                        |
| ------------------------ | -------------------------------------- | ---------------------------------- |
| **Containerização**      | Dockerfile, Docker Compose             | Docker                             |
| **Serviço Web**          | uvicorn + FastAPI                      |                                    |
| **Pipelines de Dados**   | ETL, agendamento, jobs automáticos     | Celery, Cron, Airflow (opcional)   |
| **Armazenamento**        | datasets e modelos em PostgreSQL + GCS | PostgreSQL, GCS/AWS S3             |
| **Deploy**               | APIs em containers e CI/CD             | Docker, GitHub Actions, Render/EC2 |
| **Monitoramento e Logs** | métricas, healthchecks, erros          | Prometheus, Grafana                |

---

## 🧩 4️⃣ Roadmap Prático de Estudo (em blocos)

| Etapa                                                | Tópico                                                 | Resultado esperado                                |
| ---------------------------------------------------- | ------------------------------------------------------ | ------------------------------------------------- |
| **1. Fundamentos ML (2–3 semanas)**                  | Regressão, classificação, clustering, séries temporais | Consegues explicar e justificar modelos           |
| **2. Modelagem prática (3–4 semanas)**               | scikit-learn, Prophet, XGBoost, NLP                    | Consegues treinar, testar e salvar modelos        |
| **3. Backend ML (2 semanas)**                        | FastAPI, MLflow, Celery                                | Consegues criar endpoints e pipelines automáticos |
| **4. Deploy e monitoramento (2 semanas)**            | Docker, MLflow UI, Prometheus                          | Consegues mostrar métricas e estabilidade         |
| **5. Integração com o backend principal (1 semana)** | Comunicação entre serviços                             | API entre Fastify e ML backend funcional          |

---

## 🎓 Resultado final

Quando dominares esses tópicos, poderás **defender o backend ML da Wenda** explicando:

* Por que cada modelo foi escolhido.
* Como é feito o pré-processamento e o treino.
* Como o backend serve e monitora as previsões.
* E como o sistema aprende com novos dados.

---
