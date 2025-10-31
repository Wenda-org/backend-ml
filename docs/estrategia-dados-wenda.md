# 📊 Estratégia de Coleta e Gestão de Dados - Projeto Wenda

## 🎯 Introdução

O projeto **Wenda** é uma plataforma inteligente de turismo para Angola que utiliza Machine Learning para fornecer recomendações personalizadas e análises preditivas do setor turístico. A qualidade e diversidade dos dados são fundamentais para o sucesso do modelo de ML, garantindo que as previsões e recomendações sejam precisas e relevantes.

Este documento apresenta a estratégia completa de coleta, processamento e armazenamento de dados, abrangendo múltiplas fontes que incluem:
- **Estatísticas oficiais de turismo**
- **Dados climáticos e meteorológicos**
- **Informações geográficas e pontos de interesse**
- **Dados de transporte e conectividade**
- **Avaliações e feedback de utilizadores**

---

## 🗂️ Fontes de Dados e Estratégia de Coleta

### 🏛️ 1. INE Angola - Instituto Nacional de Estatística

**🔗 Link:** [https://www.ine.gov.ao](https://www.ine.gov.ao)

**📋 Descrição:**
O INE é a fonte oficial de estatísticas nacionais de Angola, publicando relatórios detalhados sobre o setor turístico, incluindo:
- Número de turistas nacionais e internacionais
- Estatísticas de hospedagem por província
- Receitas do setor turístico
- Dados de transporte turístico
- Indicadores económicos do turismo

**⚙️ Método de Acesso:**
- **Técnica:** Web scraping controlado usando `BeautifulSoup` e `Selenium` (Python)
- **Alternativa:** Download manual de relatórios em PDF/Excel quando necessário
- **Frequência:** Mensal (novos relatórios) e trimestral (dados consolidados)

**📄 Formato dos Dados:**
- PDF (relatórios oficiais)
- XLSX (tabelas estatísticas)
- HTML (dados web)

**🗄️ Plano de Armazenamento:**
```
PostgreSQL:
├── tabela: ine_tourism_stats
│   ├── ano (INT)
│   ├── provincia (VARCHAR)
│   ├── tipo_turista (ENUM: nacional, internacional)
│   ├── numero_visitantes (INT)
│   ├── receita_usd (DECIMAL)
│   └── data_atualizacao (TIMESTAMP)
└── Google Cloud Storage: /raw/ine/
```

**🎯 Uso no Modelo:**
- Alimentar modelos de previsão de demanda turística
- Análise de sazonalidade por região
- Dashboards estatísticos no painel administrativo
- Correlação entre eventos económicos e fluxo turístico

---

### 🌦️ 2. OpenWeatherMap - Dados Climáticos

**🔗 Link:** [https://openweathermap.org/api](https://openweathermap.org/api)

**📋 Descrição:**
API completa de dados meteorológicos que fornece:
- Condições climáticas atuais e históricas
- Previsões meteorológicas de 5-16 dias
- Dados de temperatura, precipitação, humidade, vento
- Índices UV e qualidade do ar

**⚙️ Método de Acesso:**
```python
# Exemplo de implementação
import requests
import asyncio

class WeatherDataCollector:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    async def get_weather_data(self, city, country="AO"):
        url = f"{self.base_url}/weather"
        params = {
            'q': f"{city},{country}",
            'appid': self.api_key,
            'units': 'metric'
        }
        # Implementação da coleta...
```

**📄 Formato dos Dados:** JSON via REST API

**🗄️ Plano de Armazenamento:**
```sql
CREATE TABLE weather_data (
    id SERIAL PRIMARY KEY,
    cidade VARCHAR(100),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    data_medicao TIMESTAMP,
    temperatura DECIMAL(5,2),
    temperatura_min DECIMAL(5,2),
    temperatura_max DECIMAL(5,2),
    precipitacao DECIMAL(5,2),
    humidade INTEGER,
    velocidade_vento DECIMAL(5,2),
    condicao_clima VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**🎯 Uso no Modelo:**
- **Feature engineering:** Variável climática nos modelos de recomendação
- **Análise sazonal:** Correlação clima vs. fluxo turístico
- **Recomendações dinâmicas:** Sugestão de atividades baseadas no clima
- **Alertas:** Notificações sobre condições climáticas adversas

---

### 🗺️ 3. OpenStreetMap - Dados Geográficos

**🔗 Link:** [https://overpass-turbo.eu/](https://overpass-turbo.eu/)

**📋 Descrição:**
Base de dados geográfica colaborativa que fornece:
- Localização de pontos turísticos
- Hotéis, restaurantes e serviços
- Rede rodoviária e transportes
- Fronteiras administrativas
- Infraestruturas turísticas

**⚙️ Método de Acesso:**
```python
# Exemplo usando Overpass API
import overpy
import osmnx as ox

class OSMDataCollector:
    def __init__(self):
        self.api = overpy.Overpass()
    
    def get_tourism_pois(self, bbox):
        query = f"""
        [out:json][timeout:25];
        (
          node["tourism"]{bbox};
          way["tourism"]{bbox};
          relation["tourism"]{bbox};
        );
        out geom;
        """
        return self.api.query(query)
```

**📄 Formato dos Dados:** GeoJSON, XML

**🗄️ Plano de Armazenamento:**
```sql
-- Usando PostGIS para dados geoespaciais
CREATE EXTENSION postgis;

CREATE TABLE pontos_turisticos (
    id SERIAL PRIMARY KEY,
    osm_id BIGINT UNIQUE,
    nome VARCHAR(255),
    tipo_turismo VARCHAR(100),
    categoria VARCHAR(50),
    geometria GEOMETRY(POINT, 4326),
    endereco JSONB,
    tags JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_pontos_turisticos_geom 
ON pontos_turisticos USING GIST (geometria);
```

**🎯 Uso no Modelo:**
- **Visualização:** Renderização de mapas interativos
- **Análise espacial:** Densidade de pontos turísticos por região
- **Recomendações geográficas:** Sugestão de locais próximos
- **Roteamento:** Cálculo de distâncias e rotas turísticas

---

### ✈️ 4. FlightRadar24 - Dados de Tráfego Aéreo

**🔗 Link:** [https://www.flightradar24.com](https://www.flightradar24.com)

**📋 Descrição:**
Plataforma de monitorização de tráfego aéreo que fornece:
- Voos em tempo real
- Estatísticas de aeroportos angolanos
- Rotas internacionais e domésticas
- Dados históricos de conectividade

**⚙️ Método de Acesso:**
```python
# Scraping controlado com rate limiting
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

class FlightDataCollector:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.rate_limit = 2  # segundos entre requests
    
    def get_airport_stats(self, airport_code):
        url = f"https://www.flightradar24.com/data/airports/{airport_code}"
        # Implementação com respeito aos termos de uso...
        time.sleep(self.rate_limit)
```

**📄 Formato dos Dados:** HTML (scraping), JSON (se API disponível)

**🗄️ Plano de Armazenamento:**
```sql
CREATE TABLE voos_dados (
    id SERIAL PRIMARY KEY,
    codigo_voo VARCHAR(10),
    aeroporto_origem VARCHAR(4),
    aeroporto_destino VARCHAR(4),
    data_voo DATE,
    hora_partida TIME,
    hora_chegada TIME,
    companhia_aerea VARCHAR(100),
    tipo_aeronave VARCHAR(50),
    status_voo VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**🎯 Uso no Modelo:**
- **Previsão de chegadas:** Antecipação de fluxo de turistas internacionais
- **Análise de conectividade:** Identificação de mercados-fonte principais
- **Sazonalidade:** Padrões de voos vs. épocas turísticas
- **Capacidade aeroportuária:** Análise de infraestrutura de transporte

---

### 🏨 5. Google Places API - Avaliações e POIs

**🔗 Link:** [https://developers.google.com/maps/documentation/places/web-service](https://developers.google.com/maps/documentation/places/web-service)

**📋 Descrição:**
API oficial do Google que fornece:
- Informações detalhadas de estabelecimentos
- Avaliações e classificações de utilizadores
- Fotos e horários de funcionamento
- Dados de popularidade e tendências

**⚙️ Método de Acesso:**
```python
import googlemaps

class GooglePlacesCollector:
    def __init__(self, api_key):
        self.gmaps = googlemaps.Client(key=api_key)
    
    def search_tourism_places(self, location, radius=50000):
        places = self.gmaps.places_nearby(
            location=location,
            radius=radius,
            type='tourist_attraction'
        )
        return places
```

**📄 Formato dos Dados:** JSON via REST API

**🗄️ Plano de Armazenamento:**
```sql
CREATE TABLE google_places (
    id SERIAL PRIMARY KEY,
    place_id VARCHAR(255) UNIQUE,
    nome VARCHAR(255),
    categoria VARCHAR(100),
    rating DECIMAL(2,1),
    total_avaliacoes INTEGER,
    preco_nivel INTEGER,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    endereco TEXT,
    telefone VARCHAR(20),
    website VARCHAR(255),
    horarios JSONB,
    fotos JSONB,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**🎯 Uso no Modelo:**
- **Sistema de recomendação:** Ranking baseado em avaliações
- **Análise de sentimento:** Processamento de reviews
- **Popularidade:** Identificação de trending destinations
- **Qualidade de serviço:** Métricas de satisfação do cliente

---

## 🏗️ Arquitetura de Armazenamento

### 📁 Estrutura de Diretórios
```
/data
├── raw/                    # Dados brutos originais
│   ├── ine/               # Relatórios INE (PDF, XLSX)
│   ├── weather/           # Dados climáticos (JSON)
│   ├── osm/               # Exports OpenStreetMap (XML, GeoJSON)
│   ├── flights/           # Dados de voos (CSV, JSON)
│   └── google_places/     # Dados Google Places (JSON)
├── processed/             # Dados limpos e normalizados
│   ├── tourism_stats/     # Estatísticas processadas
│   ├── weather_clean/     # Dados climáticos limpos
│   ├── geo_processed/     # Dados geográficos processados
│   └── reviews_processed/ # Avaliações processadas
└── model/                 # Datasets prontos para ML
    ├── features/          # Features engineered
    ├── training/          # Dados de treino
    └── validation/        # Dados de validação
```

### 🗃️ Camadas de Dados

#### **Camada Raw (Bruta)**
- **Propósito:** Armazenamento de dados originais sem modificação
- **Tecnologia:** Google Cloud Storage / AWS S3
- **Retenção:** Permanente (backup e auditoria)

#### **Camada Processed (Processada)**
- **Propósito:** Dados limpos, normalizados e estruturados
- **Tecnologia:** PostgreSQL + PostGIS
- **Características:**
  - Esquemas normalizados
  - Índices otimizados
  - Constraints de integridade
  - Triggers de auditoria

#### **Camada Model (Modelo)**
- **Propósito:** Datasets otimizados para Machine Learning
- **Tecnologia:** PostgreSQL + Data Warehouse
- **Características:**
  - Features engineered
  - Dados balanceados
  - Formato otimizado para treino

---

## ⚙️ Stack Tecnológico

### 🐍 Linguagens e Frameworks
| Tecnologia | Função | Justificativa |
|------------|--------|---------------|
| **Python 3.9+** | Linguagem principal | Ecossistema ML robusto |
| **Pandas** | Manipulação de dados | Performance e facilidade |
| **NumPy** | Computação numérica | Base para análise científica |
| **Scikit-learn** | Machine Learning | Algoritmos testados e documentados |
| **GeoPandas** | Dados geoespaciais | Integração GIS com Pandas |

### 🕷️ Coleta de Dados
| Ferramenta | Uso | Configuração |
|------------|-----|--------------|
| **BeautifulSoup** | Web scraping HTML | `pip install beautifulsoup4` |
| **Selenium** | Scraping dinâmico | `pip install selenium` |
| **Requests** | APIs REST | `pip install requests` |
| **aiohttp** | Requests assíncronos | `pip install aiohttp` |
| **Scrapy** | Scraping em escala | `pip install scrapy` |

### 🗄️ Armazenamento e Processamento
| Componente | Tecnologia | Configuração |
|------------|------------|--------------|
| **Banco Principal** | PostgreSQL 14+ | Com extensão PostGIS |
| **Cache** | Redis | Para dados temporários |
| **Object Storage** | Google Cloud Storage | Dados brutos e backups |
| **ETL** | Apache Airflow | Orquestração de pipelines |
| **Monitorização** | Prometheus + Grafana | Métricas e alertas |

### 📊 Análise e Desenvolvimento
| Ferramenta | Propósito |
|------------|-----------|
| **Jupyter Notebooks** | Análise exploratória e prototipagem |
| **DBeaver** | Administração de base de dados |
| **QGIS** | Análise e visualização geoespacial |
| **Git + GitHub** | Controlo de versão e colaboração |

---

## 🔄 Pipeline de Dados

### 1️⃣ **Extração (Extract)**
```python
# Exemplo de pipeline de extração
class DataExtractor:
    def __init__(self):
        self.collectors = {
            'ine': INEDataCollector(),
            'weather': WeatherDataCollector(),
            'osm': OSMDataCollector(),
            'flights': FlightDataCollector(),
            'places': GooglePlacesCollector()
        }
    
    async def extract_all(self):
        tasks = []
        for source, collector in self.collectors.items():
            task = asyncio.create_task(collector.collect())
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return dict(zip(self.collectors.keys(), results))
```

### 2️⃣ **Transformação (Transform)**
```python
class DataTransformer:
    def clean_tourism_data(self, raw_data):
        # Limpeza e normalização
        df = pd.DataFrame(raw_data)
        df = df.dropna(subset=['visitantes', 'provincia'])
        df['data'] = pd.to_datetime(df['data'])
        df['visitantes'] = pd.to_numeric(df['visitantes'], errors='coerce')
        return df
    
    def engineer_features(self, df):
        # Feature engineering
        df['mes'] = df['data'].dt.month
        df['trimestre'] = df['data'].dt.quarter
        df['ano'] = df['data'].dt.year
        df['sazonalidade'] = df['mes'].map(self.get_season_map())
        return df
```

### 3️⃣ **Carregamento (Load)**
```python
class DataLoader:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def load_to_postgres(self, df, table_name):
        df.to_sql(
            table_name, 
            self.db, 
            if_exists='append',
            index=False,
            method='multi'
        )
```

### 🕐 **Agendamento com Airflow**
```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'wenda-data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'wenda_data_pipeline',
    default_args=default_args,
    description='Pipeline de coleta de dados Wenda',
    schedule_interval='@daily',
    catchup=False
)

extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_all_sources,
    dag=dag
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_all_data,
    dag=dag
)

load_task = PythonOperator(
    task_id='load_data',
    python_callable=load_to_warehouse,
    dag=dag
)

extract_task >> transform_task >> load_task
```

---

## 📈 Monitorização e Qualidade dos Dados

### 🎯 **Métricas de Qualidade**
- **Completude:** % de campos preenchidos
- **Consistência:** Validação de formatos e tipos
- **Precisão:** Verificação de valores válidos
- **Atualidade:** Frequência de atualização
- **Integridade:** Relações entre tabelas

### 🚨 **Sistema de Alertas**
```python
class DataQualityMonitor:
    def __init__(self):
        self.thresholds = {
            'completeness': 0.95,
            'freshness_hours': 24,
            'anomaly_threshold': 2.0
        }
    
    def check_data_quality(self, table_name):
        checks = [
            self.check_completeness(table_name),
            self.check_freshness(table_name),
            self.check_anomalies(table_name)
        ]
        
        failed_checks = [c for c in checks if not c['passed']]
        if failed_checks:
            self.send_alert(table_name, failed_checks)
```

### 📊 **Dashboard de Monitorização**
- **Grafana:** Visualização de métricas em tempo real
- **Prometheus:** Coleta de métricas do sistema
- **Alertmanager:** Gestão de alertas e notificações

---

## 🔒 Considerações de Segurança e Compliance

### 🛡️ **Segurança dos Dados**
- **Encriptação:** Dados sensíveis encriptados em repouso e em trânsito
- **Acesso:** Controlo baseado em roles (RBAC)
- **Auditoria:** Log de todas as operações de dados
- **Backup:** Backups automáticos com retenção de 90 dias

### ⚖️ **Compliance Legal**
- **GDPR:** Conformidade com regulamentação europeia
- **Lei de Proteção de Dados de Angola:** Cumprimento da legislação local
- **Termos de Uso:** Respeito aos ToS de todas as APIs utilizadas
- **Rate Limiting:** Implementação de limites para evitar sobrecarga

### 🔑 **Gestão de Credenciais**
```python
# Exemplo de gestão segura de API keys
import os
from cryptography.fernet import Fernet

class SecureConfig:
    def __init__(self):
        self.cipher = Fernet(os.environ['ENCRYPTION_KEY'])
    
    def get_api_key(self, service):
        encrypted_key = os.environ[f'{service.upper()}_API_KEY_ENCRYPTED']
        return self.cipher.decrypt(encrypted_key.encode()).decode()
```

---

## 🚀 Roadmap de Implementação

### **Fase 1: Fundação (Semanas 1-2)**
- [ ] Configuração da infraestrutura base (PostgreSQL + PostGIS)
- [ ] Implementação dos coletores básicos (INE + Weather)
- [ ] Pipeline ETL inicial
- [ ] Testes unitários e integração

### **Fase 2: Expansão (Semanas 3-4)**
- [ ] Integração OpenStreetMap e Google Places
- [ ] Sistema de monitorização com Grafana
- [ ] Otimização de performance
- [ ] Documentação técnica completa

### **Fase 3: Produção (Semanas 5-6)**
- [ ] Deploy em ambiente de produção
- [ ] Configuração de alertas e backups
- [ ] Testes de carga e stress
- [ ] Treinamento da equipa

### **Fase 4: Otimização (Ongoing)**
- [ ] Machine Learning para detecção de anomalias
- [ ] Auto-scaling baseado em demanda
- [ ] Integração de novas fontes de dados
- [ ] Análise preditiva de qualidade

---

## 📝 Conclusão

Esta estratégia de dados estabelece uma base sólida e escalável para o projeto Wenda, garantindo que o modelo de Machine Learning tenha acesso a dados de alta qualidade, atualizados e diversificados. A arquitetura proposta permite:

- **Escalabilidade:** Fácil adição de novas fontes de dados
- **Confiabilidade:** Monitorização contínua e sistema de alertas
- **Performance:** Otimização para consultas analíticas
- **Manutenibilidade:** Código limpo e bem documentado
- **Segurança:** Proteção de dados sensíveis e compliance legal

O sucesso desta implementação será medido pela qualidade das recomendações da Wenda e pela satisfação dos utilizadores finais, criando um ciclo virtuoso de melhoria contínua baseado em dados reais e feedback do mercado.

---

**Documento preparado por:** Equipa de Dados - Projeto Wenda  
**Data:** Outubro 2024  
**Versão:** 1.0  
**Próxima revisão:** Novembro 2024
