# 📱💻 Integração Mobile & Web - Wenda ML Backend

**Data:** 11 de Novembro de 2025  
**Versão API:** v1.0.0  
**Base URL:** `https://api.wenda.ao` (produção) | `http://localhost:8000` (desenvolvimento)

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Autenticação](#autenticação)
3. [Endpoints ML](#endpoints-ml)
   - [Previsão de Visitantes](#1-previsão-de-visitantes-forecast)
   - [Segmentação de Turistas](#2-segmentação-de-turistas-clustering)
   - [Recomendação de Destinos](#3-recomendação-de-destinos-recommender)
   - [Listar Modelos](#4-listar-modelos-ml)
   - [Health Check](#5-health-check-ml)
4. [Integração Mobile (React Native)](#integração-mobile-react-native)
5. [Integração Web (React/Next.js)](#integração-web-reactnextjs)
6. [Tratamento de Erros](#tratamento-de-erros)
7. [Cache & Performance](#cache--performance)

---

## 🎯 Visão Geral

O backend ML da Wenda expõe **5 endpoints principais** que serão consumidos pelas aplicações mobile e web:

| Endpoint | Método | Usado em | Propósito |
|----------|--------|----------|-----------|
| `/api/ml/forecast` | POST | 📊 Dashboard Admin | Prever visitantes futuros |
| `/api/ml/segments` | GET | 👥 Perfil do Usuário | Identificar perfil do turista |
| `/api/ml/recommend` | POST | 🏖️ Tela Principal | Recomendar destinos personalizados |
| `/api/ml/models` | GET | ⚙️ Admin/Debug | Listar modelos treinados |
| `/api/ml/health` | GET | 🔍 Monitoring | Status do módulo ML |

---

## 🔐 Autenticação

### Headers Obrigatórios

```http
Content-Type: application/json
Authorization: Bearer <token_jwt>  # Somente para endpoints protegidos
```

> **Nota:** Por enquanto, os endpoints ML são **públicos** para fins de desenvolvimento. Em produção, adicionar autenticação JWT para `/api/ml/forecast` e `/api/ml/models`.

---

## 🤖 Endpoints ML

### 1. Previsão de Visitantes (Forecast)

**Usado em:** Dashboard Administrativo (Web)

#### Requisição

```http
POST /api/ml/forecast
Content-Type: application/json

{
  "destination_id": "164a0127-06b4-47a1-b9c2-3475caa82305",
  "forecast_months": 12
}
```

**Parâmetros:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `destination_id` | UUID | ✅ | ID do destino turístico |
| `forecast_months` | integer | ✅ | Número de meses para prever (1-24) |

#### Resposta

```json
{
  "destination_id": "164a0127-06b4-47a1-b9c2-3475caa82305",
  "destination_name": "Fortaleza de São Miguel",
  "province": "Luanda",
  "forecast": [
    {
      "month": "2025-12",
      "predicted_visitors": 15234,
      "confidence_interval": {
        "min": 14102,
        "max": 16366
      }
    },
    {
      "month": "2026-01",
      "predicted_visitors": 18456,
      "confidence_interval": {
        "min": 17124,
        "max": 19788
      }
    }
  ],
  "total_predicted": 189234,
  "model_version": "v1.0.0-rf-trained",
  "generated_at": "2025-11-11T10:30:00Z"
}
```

#### Integração Mobile (React Native)

```typescript
// services/forecastService.ts
import axios from 'axios';

interface ForecastRequest {
  destination_id: string;
  forecast_months: number;
}

interface ForecastResponse {
  destination_id: string;
  destination_name: string;
  province: string;
  forecast: Array<{
    month: string;
    predicted_visitors: number;
    confidence_interval: {
      min: number;
      max: number;
    };
  }>;
  total_predicted: number;
  model_version: string;
  generated_at: string;
}

export const getForecast = async (
  destinationId: string,
  months: number = 12
): Promise<ForecastResponse> => {
  try {
    const response = await axios.post<ForecastResponse>(
      `${API_BASE_URL}/api/ml/forecast`,
      {
        destination_id: destinationId,
        forecast_months: months,
      }
    );
    return response.data;
  } catch (error) {
    console.error('Forecast error:', error);
    throw error;
  }
};
```

#### UI/UX - Mobile

**Tela:** Dashboard Admin > Estatísticas > Previsões

```
┌─────────────────────────────────┐
│ 📊 Previsão de Visitantes       │
├─────────────────────────────────┤
│ Destino: Fortaleza São Miguel   │
│ Província: Luanda                │
│                                  │
│ ┌─────────────────────────────┐ │
│ │  📈 Gráfico de Linha        │ │
│ │                             │ │
│ │  18k ┤    ╱╲               │ │
│ │  15k ┤   ╱  ╲   ╱╲         │ │
│ │  12k ┤  ╱    ╲ ╱  ╲        │ │
│ │      └─────────────────     │ │
│ │   Dez Jan Fev Mar Abr       │ │
│ └─────────────────────────────┘ │
│                                  │
│ Total Previsto: 189.234          │
│ Modelo: RandomForest v1.0.0      │
└─────────────────────────────────┘
```

#### Integração Web (React/Next.js)

```tsx
// components/admin/ForecastChart.tsx
import { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { getForecast } from '@/services/api';

interface Props {
  destinationId: string;
}

export function ForecastChart({ destinationId }: Props) {
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadForecast() {
      try {
        const data = await getForecast(destinationId, 12);
        setForecast(data);
      } catch (error) {
        console.error('Failed to load forecast:', error);
      } finally {
        setLoading(false);
      }
    }
    loadForecast();
  }, [destinationId]);

  if (loading) return <Skeleton />;

  const chartData = {
    labels: forecast.forecast.map(f => f.month),
    datasets: [
      {
        label: 'Visitantes Previstos',
        data: forecast.forecast.map(f => f.predicted_visitors),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
      },
      {
        label: 'Intervalo de Confiança (Min)',
        data: forecast.forecast.map(f => f.confidence_interval.min),
        borderColor: 'rgba(59, 130, 246, 0.3)',
        borderDash: [5, 5],
      },
      {
        label: 'Intervalo de Confiança (Max)',
        data: forecast.forecast.map(f => f.confidence_interval.max),
        borderColor: 'rgba(59, 130, 246, 0.3)',
        borderDash: [5, 5],
      },
    ],
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <h3 className="text-xl font-bold mb-4">
        Previsão de Visitantes - {forecast.destination_name}
      </h3>
      <Line data={chartData} />
      <p className="text-sm text-gray-500 mt-4">
        Total previsto: {forecast.total_predicted.toLocaleString()} visitantes
      </p>
      <p className="text-xs text-gray-400">
        Modelo: {forecast.model_version}
      </p>
    </div>
  );
}
```

---

### 2. Segmentação de Turistas (Clustering)

**Usado em:** Perfil do Usuário (Mobile & Web)

#### Requisição

```http
GET /api/ml/segments
```

**Parâmetros:** Nenhum (retorna todos os segmentos)

#### Resposta

```json
{
  "segments": [
    {
      "id": 0,
      "name": "Negócios & Lazer",
      "percentage": 15.0,
      "description": "Viajantes de negócios que combinam trabalho com lazer curto",
      "characteristics": {
        "budget_level": "high",
        "avg_trip_duration": 4,
        "avg_group_size": 1,
        "top_preferences": ["gastronomy", "culture"],
        "preference_scores": {
          "beach": 0.45,
          "culture": 0.75,
          "nature": 0.30,
          "adventure": 0.20,
          "gastronomy": 0.83
        }
      },
      "recommended_destinations": [
        "Fortaleza de São Miguel",
        "Ilha do Mussulo",
        "Museu Nacional de Antropologia"
      ]
    },
    {
      "id": 2,
      "name": "Relaxante Tradicional",
      "percentage": 35.0,
      "description": "Busca praias, descanso e boa gastronomia com a família",
      "characteristics": {
        "budget_level": "medium",
        "avg_trip_duration": 6,
        "avg_group_size": 3,
        "top_preferences": ["beach", "gastronomy"],
        "preference_scores": {
          "beach": 0.90,
          "culture": 0.40,
          "nature": 0.45,
          "adventure": 0.15,
          "gastronomy": 0.66
        }
      },
      "recommended_destinations": [
        "Praia Morena",
        "Baía de Luanda",
        "Cabo Ledo"
      ]
    }
  ],
  "total_segments": 5,
  "model_version": "v1.0.0-kmeans",
  "generated_at": "2025-11-11T10:30:00Z"
}
```

#### Integração Mobile (React Native)

```typescript
// services/segmentService.ts
interface Segment {
  id: number;
  name: string;
  percentage: number;
  description: string;
  characteristics: {
    budget_level: string;
    avg_trip_duration: number;
    avg_group_size: number;
    top_preferences: string[];
    preference_scores: {
      beach: number;
      culture: number;
      nature: number;
      adventure: number;
      gastronomy: number;
    };
  };
  recommended_destinations: string[];
}

export const getSegments = async (): Promise<Segment[]> => {
  const response = await axios.get(`${API_BASE_URL}/api/ml/segments`);
  return response.data.segments;
};

// Hook personalizado
export const useUserSegment = (userPreferences: any) => {
  const [segment, setSegment] = useState<Segment | null>(null);

  useEffect(() => {
    async function identifySegment() {
      const segments = await getSegments();
      
      // Calcular similaridade com preferências do usuário
      const match = segments.reduce((best, seg) => {
        const similarity = calculateSimilarity(
          userPreferences,
          seg.characteristics.preference_scores
        );
        return similarity > best.score 
          ? { segment: seg, score: similarity }
          : best;
      }, { segment: null, score: 0 });
      
      setSegment(match.segment);
    }
    
    identifySegment();
  }, [userPreferences]);

  return segment;
};
```

#### UI/UX - Mobile

**Tela:** Perfil > Meu Perfil de Viajante

```
┌─────────────────────────────────┐
│ 👤 Seu Perfil de Viajante       │
├─────────────────────────────────┤
│                                  │
│  🎯 Relaxante Tradicional        │
│  ─────────────────────────       │
│  35% dos viajantes como você    │
│                                  │
│  Busca praias, descanso e boa   │
│  gastronomia com a família      │
│                                  │
│  📊 Características:             │
│  • Orçamento: Médio              │
│  • Duração: ~6 dias              │
│  • Grupo: ~3 pessoas             │
│                                  │
│  ❤️ Suas Preferências:           │
│  🏖️ Praia        ████████░ 90%   │
│  🍴 Gastronomia  ██████░░░ 66%   │
│  🌳 Natureza     ████░░░░░ 45%   │
│  🏛️ Cultura      ████░░░░░ 40%   │
│  🧗 Aventura     █░░░░░░░░ 15%   │
│                                  │
│  📍 Destinos Recomendados:       │
│  • Praia Morena                  │
│  • Baía de Luanda                │
│  • Cabo Ledo                     │
│                                  │
│  [Ver Todos os Destinos]         │
└─────────────────────────────────┘
```

#### Integração Web

```tsx
// components/profile/UserSegmentCard.tsx
import { useUserSegment } from '@/hooks/useUserSegment';
import { Progress } from '@/components/ui/progress';

export function UserSegmentCard() {
  const { user } = useAuth();
  const segment = useUserSegment(user.preferences);

  if (!segment) return <Loading />;

  return (
    <div className="bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl p-6 text-white">
      <h2 className="text-2xl font-bold mb-2">🎯 {segment.name}</h2>
      <p className="text-blue-100 mb-4">{segment.description}</p>
      
      <div className="bg-white/10 rounded-lg p-4 mb-4">
        <p className="text-sm mb-2">
          {segment.percentage}% dos viajantes como você
        </p>
        <Progress value={segment.percentage} className="bg-white/20" />
      </div>

      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-white/10 rounded p-3">
          <p className="text-xs opacity-80">Orçamento</p>
          <p className="font-semibold capitalize">
            {segment.characteristics.budget_level}
          </p>
        </div>
        <div className="bg-white/10 rounded p-3">
          <p className="text-xs opacity-80">Duração</p>
          <p className="font-semibold">
            ~{segment.characteristics.avg_trip_duration} dias
          </p>
        </div>
        <div className="bg-white/10 rounded p-3">
          <p className="text-xs opacity-80">Grupo</p>
          <p className="font-semibold">
            ~{segment.characteristics.avg_group_size} pessoas
          </p>
        </div>
      </div>

      <h3 className="font-semibold mb-3">❤️ Suas Preferências</h3>
      {Object.entries(segment.characteristics.preference_scores).map(
        ([pref, score]) => (
          <div key={pref} className="mb-2">
            <div className="flex justify-between text-sm mb-1">
              <span className="capitalize">{pref}</span>
              <span>{Math.round(score * 100)}%</span>
            </div>
            <Progress value={score * 100} className="bg-white/20" />
          </div>
        )
      )}
    </div>
  );
}
```

---

### 3. Recomendação de Destinos (Recommender)

**Usado em:** Tela Principal, Pesquisa, Favoritos (Mobile & Web)

#### Requisição

```http
POST /api/ml/recommend
Content-Type: application/json

{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "preferences": {
    "categories": ["beach", "nature"],
    "provinces": ["Luanda", "Benguela"],
    "min_rating": 4.0
  },
  "limit": 10,
  "exclude_visited": true
}
```

**Parâmetros:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `user_id` | UUID | ✅ | ID do usuário (para personalização) |
| `preferences.categories` | array | ❌ | Categorias desejadas |
| `preferences.provinces` | array | ❌ | Províncias desejadas |
| `preferences.min_rating` | float | ❌ | Rating mínimo (0-5) |
| `limit` | integer | ❌ | Número de recomendações (padrão: 10) |
| `exclude_visited` | boolean | ❌ | Excluir destinos já visitados |

#### Resposta

```json
{
  "recommendations": [
    {
      "destination_id": "ecc5f3f9-0a61-4063-8e8c-094f79f5e2a8",
      "name": "Ilha do Mussulo",
      "province": "Luanda",
      "category": "beach",
      "rating_avg": 4.7,
      "description": "Península paradisíaca com praias de areia branca...",
      "images": [
        "https://cdn.wenda.ao/mussulo1.jpg",
        "https://cdn.wenda.ao/mussulo2.jpg"
      ],
      "latitude": -9.0189,
      "longitude": 12.8444,
      "score": 0.876,
      "reason": "Baseado em suas preferências de praia e natureza"
    },
    {
      "destination_id": "e75029de-0e4b-4a44-b931-335fab346e0b",
      "name": "Miradouro da Lua",
      "province": "Luanda",
      "category": "nature",
      "rating_avg": 4.6,
      "description": "Formações rochosas espetaculares com vista lunar...",
      "images": [
        "https://cdn.wenda.ao/miradouro1.jpg"
      ],
      "latitude": -9.3667,
      "longitude": 13.1000,
      "score": 0.823,
      "reason": "Destinos similares aos seus favoritos"
    }
  ],
  "total_recommendations": 10,
  "model_version": "v1.0.0-content",
  "personalized": true,
  "generated_at": "2025-11-11T10:30:00Z"
}
```

#### Integração Mobile (React Native)

```typescript
// services/recommendService.ts
interface RecommendRequest {
  user_id: string;
  preferences?: {
    categories?: string[];
    provinces?: string[];
    min_rating?: number;
  };
  limit?: number;
  exclude_visited?: boolean;
}

interface Destination {
  destination_id: string;
  name: string;
  province: string;
  category: string;
  rating_avg: number;
  description: string;
  images: string[];
  latitude: number;
  longitude: number;
  score: number;
  reason: string;
}

export const getRecommendations = async (
  userId: string,
  preferences: any = {},
  limit: number = 10
): Promise<Destination[]> => {
  const response = await axios.post(`${API_BASE_URL}/api/ml/recommend`, {
    user_id: userId,
    preferences,
    limit,
    exclude_visited: true,
  });
  return response.data.recommendations;
};

// Hook com cache
export const useRecommendations = (userId: string) => {
  const [recommendations, setRecommendations] = useState<Destination[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await getRecommendations(userId);
        setRecommendations(data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [userId]);

  return { recommendations, loading, error };
};
```

#### UI/UX - Mobile

**Tela:** Home > Para Você

```
┌─────────────────────────────────┐
│ 🏠 Wenda                    ≡   │
├─────────────────────────────────┤
│ 👋 Olá, João!                   │
│ Para onde vamos hoje?           │
│                                  │
│ 🎯 Recomendados para Você        │
│ ─────────────────────────       │
│                                  │
│ ┌───────────────────────────┐   │
│ │ [Imagem: Ilha Mussulo]    │   │
│ │                           │   │
│ │ 🏖️ Ilha do Mussulo         │   │
│ │ Luanda • ⭐ 4.7           │   │
│ │                           │   │
│ │ Baseado em suas           │   │
│ │ preferências de praia     │   │
│ │                           │   │
│ │ [Ver Detalhes] [❤️ Salvar]│   │
│ └───────────────────────────┘   │
│                                  │
│ ┌───────────────────────────┐   │
│ │ [Imagem: Miradouro]       │   │
│ │                           │   │
│ │ 🌄 Miradouro da Lua        │   │
│ │ Luanda • ⭐ 4.6           │   │
│ │                           │   │
│ │ Destinos similares aos    │   │
│ │ seus favoritos            │   │
│ │                           │   │
│ │ [Ver Detalhes] [❤️ Salvar]│   │
│ └───────────────────────────┘   │
│                                  │
│ [Ver Todos (10)]                 │
└─────────────────────────────────┘
```

#### Integração Web

```tsx
// pages/home.tsx
import { useRecommendations } from '@/hooks/useRecommendations';
import { DestinationCard } from '@/components/DestinationCard';

export default function HomePage() {
  const { user } = useAuth();
  const { recommendations, loading } = useRecommendations(user.id);

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-2">
        👋 Olá, {user.name}!
      </h1>
      <p className="text-gray-600 mb-8">
        Para onde vamos hoje?
      </p>

      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-6">
          🎯 Recomendados para Você
        </h2>
        
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => <SkeletonCard key={i} />)}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recommendations.map((dest) => (
              <DestinationCard
                key={dest.destination_id}
                destination={dest}
                showReason
                score={dest.score}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

// components/DestinationCard.tsx
interface Props {
  destination: Destination;
  showReason?: boolean;
  score?: number;
}

export function DestinationCard({ destination, showReason, score }: Props) {
  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-2xl transition-shadow">
      <div className="relative h-48">
        <img
          src={destination.images[0]}
          alt={destination.name}
          className="w-full h-full object-cover"
        />
        {score && (
          <div className="absolute top-3 right-3 bg-white/90 rounded-full px-3 py-1">
            <span className="text-sm font-semibold text-blue-600">
              {Math.round(score * 100)}% match
            </span>
          </div>
        )}
      </div>

      <div className="p-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="text-lg font-semibold">{destination.name}</h3>
          <div className="flex items-center gap-1">
            <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
            <span className="text-sm font-medium">
              {destination.rating_avg.toFixed(1)}
            </span>
          </div>
        </div>

        <p className="text-sm text-gray-600 mb-3">
          {destination.province} • {destination.category}
        </p>

        <p className="text-sm text-gray-700 line-clamp-2 mb-3">
          {destination.description}
        </p>

        {showReason && (
          <div className="bg-blue-50 rounded-lg p-2 mb-3">
            <p className="text-xs text-blue-700">
              💡 {destination.reason}
            </p>
          </div>
        )}

        <div className="flex gap-2">
          <Button variant="primary" className="flex-1">
            Ver Detalhes
          </Button>
          <Button variant="outline" size="icon">
            <Heart className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
```

---

### 4. Listar Modelos ML

**Usado em:** Dashboard Admin > Configurações ML (Web)

#### Requisição

```http
GET /api/ml/models
```

#### Resposta

```json
{
  "models": [
    {
      "model_type": "forecast",
      "model_name": "forecast_Luanda",
      "version": "v1.0.0-rf-trained",
      "algorithm": "RandomForestRegressor",
      "metrics": {
        "mae": 707.23,
        "mape": 4.85,
        "test_samples": 12
      },
      "status": "active",
      "trained_on": "2025-11-11"
    },
    {
      "model_type": "clustering",
      "model_name": "clustering_kmeans",
      "version": "v1.0.0-kmeans",
      "algorithm": "KMeans",
      "metrics": {
        "n_clusters": 5,
        "n_samples": 500,
        "silhouette_score": 0.357
      },
      "status": "active",
      "trained_on": "2025-11-11"
    },
    {
      "model_type": "recommender",
      "model_name": "recommender_content_based",
      "version": "v1.0.0-content",
      "algorithm": "TF-IDF + Cosine Similarity",
      "metrics": {
        "n_destinations": 23,
        "feature_dim": 63,
        "similarity_metric": "cosine"
      },
      "status": "active",
      "trained_on": "2025-11-11"
    }
  ],
  "total_models": 14,
  "by_type": {
    "forecast": 12,
    "clustering": 1,
    "recommender": 1
  },
  "generated_at": "2025-11-11T10:30:00Z"
}
```

#### Integração Web (Admin)

```tsx
// pages/admin/ml-models.tsx
export default function MLModelsPage() {
  const { data: models, isLoading } = useQuery('ml-models', () =>
    axios.get('/api/ml/models').then(res => res.data)
  );

  if (isLoading) return <Loading />;

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">🤖 Modelos ML</h1>

      <div className="grid grid-cols-3 gap-4 mb-8">
        <StatsCard
          title="Total de Modelos"
          value={models.total_models}
          icon="🎯"
        />
        <StatsCard
          title="Forecast"
          value={models.by_type.forecast}
          icon="📊"
        />
        <StatsCard
          title="Clustering + Recommender"
          value={models.by_type.clustering + models.by_type.recommender}
          icon="🧠"
        />
      </div>

      <Tabs defaultValue="all">
        <TabsList>
          <TabsTrigger value="all">Todos</TabsTrigger>
          <TabsTrigger value="forecast">Forecast</TabsTrigger>
          <TabsTrigger value="clustering">Clustering</TabsTrigger>
          <TabsTrigger value="recommender">Recommender</TabsTrigger>
        </TabsList>

        <TabsContent value="all">
          <ModelsTable models={models.models} />
        </TabsContent>
        {/* ... outros tabs */}
      </Tabs>
    </div>
  );
}
```

---

### 5. Health Check ML

**Usado em:** Monitoring, Status Pages

#### Requisição

```http
GET /api/ml/health
```

#### Resposta

```json
{
  "status": "healthy",
  "module": "ml",
  "endpoints": ["forecast", "recommend", "segments", "models"],
  "trained_models": 14,
  "model_status": "trained models available",
  "timestamp": "2025-11-11T10:30:00Z"
}
```

---

## 📱 Integração Mobile (React Native)

### Estrutura de Pastas

```
mobile/
├── src/
│   ├── services/
│   │   ├── api.ts                 # Configuração Axios
│   │   ├── forecastService.ts     # Forecast endpoints
│   │   ├── segmentService.ts      # Clustering endpoints
│   │   └── recommendService.ts    # Recommender endpoints
│   ├── hooks/
│   │   ├── useRecommendations.ts
│   │   ├── useUserSegment.ts
│   │   └── useForecast.ts
│   ├── screens/
│   │   ├── HomeScreen.tsx         # Usa recommendations
│   │   ├── ProfileScreen.tsx      # Usa segments
│   │   └── AdminDashboard.tsx     # Usa forecast
│   └── components/
│       ├── DestinationCard.tsx
│       ├── SegmentBadge.tsx
│       └── ForecastChart.tsx
```

### Configuração Base

```typescript
// services/api.ts
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = __DEV__
  ? 'http://localhost:8000'
  : 'https://api.wenda.ao';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token
api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor para tratamento de erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirecionar para login
    }
    return Promise.reject(error);
  }
);
```

---

## 💻 Integração Web (React/Next.js)

### Estrutura de Pastas

```
web/
├── src/
│   ├── lib/
│   │   └── api.ts                # Configuração Axios/Fetch
│   ├── hooks/
│   │   ├── useRecommendations.ts
│   │   ├── useUserSegment.ts
│   │   └── useForecast.ts
│   ├── components/
│   │   ├── home/
│   │   │   ├── RecommendationsGrid.tsx
│   │   │   └── DestinationCard.tsx
│   │   ├── profile/
│   │   │   └── UserSegmentCard.tsx
│   │   └── admin/
│   │       ├── ForecastChart.tsx
│   │       └── MLModelsTable.tsx
│   └── pages/
│       ├── index.tsx              # Home (recommendations)
│       ├── profile.tsx            # Profile (segment)
│       └── admin/
│           ├── dashboard.tsx      # Admin (forecast)
│           └── ml-models.tsx      # ML config
```

### Configuração Base (Next.js)

```typescript
// lib/api.ts
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Se usar Server-Side Rendering
export async function getServerSideApi(req: any) {
  const token = req.cookies.auth_token;
  
  return axios.create({
    baseURL: API_BASE_URL,
    headers: {
      Authorization: token ? `Bearer ${token}` : undefined,
    },
  });
}
```

---

## ⚠️ Tratamento de Erros

### Códigos de Status

| Código | Significado | Ação UI |
|--------|-------------|---------|
| 200 | Sucesso | Exibir dados |
| 400 | Dados inválidos | Mostrar mensagem de validação |
| 404 | Não encontrado | "Destino não encontrado" |
| 422 | Validação falhou | Destacar campos com erro |
| 500 | Erro do servidor | "Tente novamente em instantes" |
| 503 | Serviço indisponível | "Usando dados em cache" |

### Exemplo de Tratamento

```typescript
// hooks/useRecommendations.ts
export const useRecommendations = (userId: string) => {
  const [state, setState] = useState({
    data: [],
    loading: true,
    error: null,
    fromCache: false,
  });

  useEffect(() => {
    async function fetchRecommendations() {
      try {
        const response = await getRecommendations(userId);
        setState({
          data: response,
          loading: false,
          error: null,
          fromCache: false,
        });
      } catch (error) {
        // Tentar carregar do cache
        const cached = await loadFromCache('recommendations');
        
        if (cached) {
          setState({
            data: cached,
            loading: false,
            error: 'Usando recomendações em cache',
            fromCache: true,
          });
        } else {
          setState({
            data: [],
            loading: false,
            error: error.message,
            fromCache: false,
          });
        }
      }
    }

    fetchRecommendations();
  }, [userId]);

  return state;
};
```

---

## ⚡ Cache & Performance

### Estratégias de Cache

| Endpoint | Estratégia | TTL | Motivo |
|----------|-----------|-----|--------|
| `/ml/segments` | Cache agressivo | 24h | Dados mudam raramente |
| `/ml/recommend` | Cache por usuário | 1h | Personalizado mas estável |
| `/ml/forecast` | Cache por destino | 12h | Previsões mudam devagar |
| `/ml/models` | Cache simples | 6h | Admin, baixa frequência |

### Implementação React Native

```typescript
// utils/cache.ts
import AsyncStorage from '@react-native-async-storage/async-storage';

interface CacheItem<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

export async function getCached<T>(
  key: string,
  ttl: number = 3600000 // 1h padrão
): Promise<T | null> {
  try {
    const item = await AsyncStorage.getItem(`cache:${key}`);
    if (!item) return null;

    const cached: CacheItem<T> = JSON.parse(item);
    const now = Date.now();

    if (now - cached.timestamp > cached.ttl) {
      await AsyncStorage.removeItem(`cache:${key}`);
      return null;
    }

    return cached.data;
  } catch {
    return null;
  }
}

export async function setCache<T>(
  key: string,
  data: T,
  ttl: number = 3600000
): Promise<void> {
  const item: CacheItem<T> = {
    data,
    timestamp: Date.now(),
    ttl,
  };
  await AsyncStorage.setItem(`cache:${key}`, JSON.stringify(item));
}

// Uso
const recommendations = await getCached('recommendations:user123', 3600000);
if (!recommendations) {
  const fresh = await api.getRecommendations('user123');
  await setCache('recommendations:user123', fresh, 3600000);
}
```

---

## 📊 Resumo de Uso

| Funcionalidade | Mobile | Web | Admin | Frequência de Uso |
|----------------|--------|-----|-------|-------------------|
| Recomendações | ✅ Alta | ✅ Alta | ❌ | Toda abertura do app |
| Segmentos | ✅ Média | ✅ Média | ✅ Baixa | Perfil do usuário |
| Forecast | ❌ | ❌ | ✅ Alta | Dashboard admin |
| Listar Modelos | ❌ | ❌ | ✅ Baixa | Config ML |

---

## 🔄 Versionamento da API

Quando a API mudar:

```typescript
// Suporte a múltiplas versões
const API_VERSION = 'v1';

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/${API_VERSION}`,
});

// Feature flags para novas funcionalidades
if (useFeatureFlag('ml_hybrid_recommendations')) {
  // Usar novo endpoint
  await api.post('/ml/recommend-hybrid', ...);
} else {
  // Usar endpoint atual
  await api.post('/ml/recommend', ...);
}
```

---

## 📞 Suporte

Para questões de integração:
- **Email:** dev@wenda.ao
- **Slack:** #wenda-ml-integration
- **Docs:** https://docs.wenda.ao/ml-api

---

**Última atualização:** 11 de Novembro de 2025
