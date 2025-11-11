"""
Endpoints de Machine Learning para previsões, recomendações e segmentação
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.db import get_db
from app.models import TourismStatistics, Destination, User
from app.services.forecast import get_forecast_service
from app.services.clustering import get_clustering_service
from app.services.recommender import get_recommender_service


router = APIRouter(prefix="/ml", tags=["Machine Learning"])


# ============================================================================
# Schemas (Pydantic Models)
# ============================================================================

class ForecastRequest(BaseModel):
    """Request para previsão de visitantes"""
    province: str = Field(..., description="Província alvo (ex: Luanda, Benguela)")
    month: int = Field(..., ge=1, le=12, description="Mês (1-12)")
    year: int = Field(..., ge=2024, description="Ano da previsão")


class ConfidenceInterval(BaseModel):
    """Intervalo de confiança da previsão"""
    lower: int = Field(..., description="Limite inferior")
    upper: int = Field(..., description="Limite superior")


class ForecastResponse(BaseModel):
    """Response com previsão de visitantes"""
    province: str
    month: int
    year: int
    predicted_visitors: int = Field(..., description="Número previsto de visitantes")
    confidence_interval: ConfidenceInterval
    model_version: str = Field(..., description="Versão do modelo usado")
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class UserPreferences(BaseModel):
    """Preferências do usuário para recomendações"""
    categories: Optional[List[str]] = Field(
        default=None, 
        description="Categorias de interesse (culture, beach, nature)"
    )
    budget: Optional[str] = Field(
        default=None, 
        description="Orçamento (low, medium, high)"
    )
    provinces: Optional[List[str]] = Field(
        default=None,
        description="Províncias preferidas"
    )


class RecommendRequest(BaseModel):
    """Request para recomendações personalizadas"""
    user_id: Optional[UUID] = Field(default=None, description="ID do usuário (opcional)")
    preferences: UserPreferences = Field(..., description="Preferências do usuário")
    limit: int = Field(default=10, ge=1, le=50, description="Número de recomendações")


class DestinationRecommendation(BaseModel):
    """Destino recomendado com score"""
    destination_id: UUID
    name: str
    province: str
    category: str
    description: str
    rating_avg: Optional[float]
    score: float = Field(..., ge=0.0, le=1.0, description="Score de relevância (0-1)")
    reason: str = Field(..., description="Motivo da recomendação")


class RecommendResponse(BaseModel):
    """Response com lista de recomendações"""
    recommendations: List[DestinationRecommendation]
    model_version: str = "v0.1.0-placeholder"
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class TouristSegment(BaseModel):
    """Perfil/cluster de turista"""
    segment_id: str
    name: str
    description: str
    typical_destinations: List[str]
    avg_budget: str
    percentage: float = Field(..., ge=0.0, le=100.0, description="% do total de turistas")
    characteristics: List[str]


class SegmentsResponse(BaseModel):
    """Response com perfis de turistas"""
    segments: List[TouristSegment]
    total_segments: int
    model_version: str = "v0.1.0-clustering"
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/forecast", response_model=ForecastResponse)
async def forecast_visitors(
    request: ForecastRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Prevê número de visitantes para uma província/mês/ano
    
    **Usa modelo treinado:** RandomForestRegressor por província
    Se o modelo não existir para a província, usa fallback com média histórica.
    
    **Features do modelo:**
    - year, month (transformado em sin/cos para sazonalidade)
    - occupancy_rate, avg_stay_days (opcionais, defaultam para 0)
    
    **Algoritmo com modelo treinado:**
    1. Tenta carregar modelo treinado para a província
    2. Se existe, usa o modelo para predição com intervalo de confiança
    3. Se não existe, fallback: média histórica + tendência + sazonalidade
    """
    
    # Validar província
    valid_provinces = ["Luanda", "Benguela", "Huila", "Namibe", "Cunene", "Malanje"]
    if request.province not in valid_provinces:
        raise HTTPException(
            status_code=400,
            detail=f"Província inválida. Use uma de: {', '.join(valid_provinces)}"
        )
    
    forecast_service = get_forecast_service()
    
    # Tentar usar modelo treinado
    prediction = forecast_service.predict(
        province=request.province,
        year=request.year,
        month=request.month,
        occupancy_rate=0.0,  # Pode ser expandido para aceitar no request
        avg_stay_days=0.0
    )
    
    if prediction:
        # Modelo disponível - usar predição real
        return ForecastResponse(
            province=request.province,
            month=request.month,
            year=request.year,
            predicted_visitors=prediction['predicted_visitors'],
            confidence_interval=ConfidenceInterval(**prediction['confidence_interval']),
            model_version="v1.0.0-rf-trained"
        )
    
    # Fallback: modelo não disponível - usar baseline
    # Buscar dados históricos do mesmo mês
    query = select(
        func.avg(
            TourismStatistics.domestic_visitors + TourismStatistics.foreign_visitors
        ).label("avg_visitors")
    ).where(
        and_(
            TourismStatistics.province == request.province,
            TourismStatistics.month == request.month
        )
    )
    
    result = await db.execute(query)
    row = result.first()
    
    if not row or row.avg_visitors is None:
        # Fallback: usar valor base por província
        province_base_visitors = {
            "Luanda": 12000,
            "Benguela": 4500,
            "Huila": 3000,
            "Namibe": 1500,
            "Cunene": 800,
            "Malanje": 2000,
        }
        avg_historical = province_base_visitors.get(request.province, 2000)
    else:
        avg_historical = int(row.avg_visitors)
    
    # Aplicar tendência de crescimento (5% ao ano desde 2024)
    years_ahead = request.year - 2024
    growth_factor = 1 + (years_ahead * 0.05)
    
    # Aplicar sazonalidade
    seasonal_multipliers = {
        1: 1.3, 2: 0.9, 3: 0.8, 4: 0.9, 5: 0.95, 6: 1.0,
        7: 1.25, 8: 1.2, 9: 0.9, 10: 0.85, 11: 0.95, 12: 1.4
    }
    seasonal_factor = seasonal_multipliers.get(request.month, 1.0)
    
    # Calcular previsão
    predicted = int(avg_historical * growth_factor * seasonal_factor)
    
    # Intervalo de confiança (±15%)
    margin = int(predicted * 0.15)
    confidence_interval = ConfidenceInterval(
        lower=max(0, predicted - margin),
        upper=predicted + margin
    )
    
    return ForecastResponse(
        province=request.province,
        month=request.month,
        year=request.year,
        predicted_visitors=predicted,
        confidence_interval=confidence_interval,
        model_version="v0.1.0-baseline-fallback"
    )


@router.post("/recommend", response_model=RecommendResponse)
async def recommend_destinations(
    request: RecommendRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Recomenda destinos personalizados baseado em preferências
    
    **Usa modelo treinado:** Content-Based Filtering com TF-IDF + Cosine Similarity
    Se o modelo não existir, usa fallback com filtros simples + rating.
    
    **Features do modelo:**
    - TF-IDF em descrição do destino
    - One-hot encoding de categoria e província
    - Rating normalizado
    
    **Algoritmo com modelo treinado:**
    1. Tenta usar RecommenderService para recomendações
    2. Filtra por preferências (categoria, província)
    3. Ordena por score de similaridade ou rating
    4. Retorna top N com scores e razões
    """
    
    recommender_service = get_recommender_service()
    
    # Try to use trained model
    recommendations_data = recommender_service.recommend_by_preferences(
        categories=request.preferences.categories,
        provinces=request.preferences.provinces,
        min_rating=None,  # No hard filter, let ranking decide
        n_recommendations=request.limit
    )
    
    if recommendations_data:
        # Model available - use real recommendations
        recommendations = []
        
        for rec in recommendations_data:
            # Generate reason
            reasons = []
            if request.preferences.categories and rec['category'] in request.preferences.categories:
                reasons.append(f"Matches your interest in {rec['category']}")
            if rec['rating_avg'] and rec['rating_avg'] >= 4.5:
                reasons.append("Highly rated destination")
            if rec['province']:
                reasons.append(f"Located in {rec['province']}")
            if not reasons:
                reasons.append("Recommended based on content similarity")
            
            reason = " | ".join(reasons)
            
            recommendations.append(
                DestinationRecommendation(
                    destination_id=rec['destination_id'],
                    name=rec['name'],
                    province=rec['province'],
                    category=rec['category'],
                    description="",  # Not in metadata, would need DB query
                    rating_avg=rec['rating_avg'],
                    score=rec['score'],
                    reason=reason
                )
            )
        
        return RecommendResponse(
            recommendations=recommendations,
            model_version="v1.0.0-content-based-trained"
        )
    
    # Fallback: model not available - use database query
    # Construir query base
    query = select(Destination)
    
    # Aplicar filtros de preferências
    filters = []
    
    if request.preferences.categories:
        filters.append(Destination.category.in_(request.preferences.categories))
    
    if request.preferences.provinces:
        filters.append(Destination.province.in_(request.preferences.provinces))
    
    if filters:
        query = query.where(and_(*filters))
    
    # Ordenar por rating (destinos melhor avaliados primeiro)
    query = query.order_by(Destination.rating_avg.desc())
    query = query.limit(request.limit)
    
    # Executar query
    result = await db.execute(query)
    destinations = result.scalars().all()
    
    if not destinations:
        raise HTTPException(
            status_code=404,
            detail="Nenhum destino encontrado com as preferências fornecidas"
        )
    
    # Calcular scores e razões
    recommendations = []
    max_rating = 5.0
    
    for idx, dest in enumerate(destinations):
        # Score baseado em rating + posição no ranking
        rating_score = (dest.rating_avg or 3.5) / max_rating
        position_penalty = 1 - (idx * 0.05)  # Penalidade leve por posição
        score = min(1.0, rating_score * position_penalty)
        
        # Gerar razão da recomendação
        reasons = []
        if request.preferences.categories and dest.category in request.preferences.categories:
            reasons.append(f"Matches your interest in {dest.category}")
        if dest.rating_avg and dest.rating_avg >= 4.5:
            reasons.append("Highly rated destination")
        if not reasons:
            reasons.append("Popular destination in Angola")
        
        reason = " | ".join(reasons)
        
        recommendations.append(
            DestinationRecommendation(
                destination_id=dest.id,
                name=dest.name,
                province=dest.province,
                category=dest.category,
                description=dest.description,
                rating_avg=dest.rating_avg,
                score=round(score, 2),
                reason=reason
            )
        )
    
    return RecommendResponse(
        recommendations=recommendations,
        model_version="v0.1.0-content-filter-fallback"
    )


@router.get("/segments", response_model=SegmentsResponse)
async def get_tourist_segments():
    """
    Retorna perfis/clusters de turistas identificados
    
    **Usa modelo treinado:** K-Means clustering com 5 segmentos
    Se o modelo não existir, usa fallback com perfis hardcoded.
    
    **Features do modelo:**
    - Budget preference (low/medium/high)
    - Trip duration (days)
    - Activity preferences (beach, culture, nature, adventure, gastronomy)
    - Travel frequency (trips per year)
    - Group size
    
    **Algoritmo:**
    1. Tenta carregar modelo K-Means treinado e metadata
    2. Se existe, retorna segmentos do modelo real
    3. Se não existe, fallback para perfis documentados
    """
    
    clustering_service = get_clustering_service()
    
    # Try to use trained model
    segments_data = clustering_service.get_segments()
    
    if segments_data:
        # Model available - use real clusters
        segments = []
        for seg in segments_data:
            # Map characteristics to budget string
            budget_val = seg['characteristics']['avg_budget']
            if budget_val >= 2.7:
                budget_str = "high"
            elif budget_val >= 2.3:
                budget_str = "medium-high"
            elif budget_val >= 1.7:
                budget_str = "medium"
            else:
                budget_str = "low"
            
            # Get top destinations based on preferences
            prefs = seg['characteristics']['preferences']
            if prefs['beach'] > 0.7:
                typical_dest = ["Benguela", "Lobito", "Namibe"]
            elif prefs['culture'] > 0.7:
                typical_dest = ["Luanda", "Benguela", "Lunda Norte"]
            elif prefs['nature'] > 0.8:
                typical_dest = ["Iona National Park", "Kissama", "Cunene"]
            elif prefs['adventure'] > 0.7:
                typical_dest = ["Namibe", "Huíla", "Malanje"]
            else:
                typical_dest = ["Luanda", "Benguela", "Huíla"]
            
            # Build characteristics list
            chars = seg['characteristics']
            characteristics = [
                f"Budget: {budget_str}",
                f"Avg trip: {chars['avg_trip_duration']:.0f} days",
                f"Group size: {chars['avg_group_size']:.0f} people",
                f"Travels {chars['trips_per_year']:.1f} times/year",
                f"Top preferences: {max(prefs, key=prefs.get)}, {sorted(prefs.items(), key=lambda x: x[1], reverse=True)[1][0]}"
            ]
            
            segments.append(
                TouristSegment(
                    segment_id=f"cluster_{seg['cluster_id']}",
                    name=seg['name'],
                    description=seg['description'],
                    typical_destinations=typical_dest,
                    avg_budget=budget_str,
                    percentage=seg['percentage'],
                    characteristics=characteristics
                )
            )
        
        return SegmentsResponse(
            segments=segments,
            total_segments=len(segments),
            model_version="v1.0.0-kmeans-trained"
        )
    
    # Fallback: model not available - use hardcoded profiles
    segments = [
        TouristSegment(
            segment_id="relaxante_tradicional",
            name="Relaxante Tradicional",
            description="Busca descanso e tranquilidade em ambientes familiares",
            typical_destinations=["Benguela", "Lobito", "Namibe"],
            avg_budget="medium",
            percentage=35.0,
            characteristics=[
                "Prefere praias e resorts",
                "Viaja em família ou casal",
                "Média de 5-7 dias de estadia",
                "Orçamento médio: $100-200/dia"
            ]
        ),
        TouristSegment(
            segment_id="aventureiro_explorador",
            name="Aventureiro Explorador",
            description="Procura experiências únicas e contato com natureza",
            typical_destinations=["Namibe", "Huíla", "Malanje"],
            avg_budget="medium-high",
            percentage=25.0,
            characteristics=[
                "Interessado em natureza e aventura",
                "Viaja sozinho ou em grupos pequenos",
                "Média de 7-10 dias",
                "Orçamento: $150-300/dia"
            ]
        ),
        TouristSegment(
            segment_id="cultural_historico",
            name="Cultural e Histórico",
            description="Interessado em patrimônio cultural e história",
            typical_destinations=["Luanda", "Benguela", "Lunda Norte"],
            avg_budget="medium",
            percentage=20.0,
            characteristics=[
                "Visita museus e sítios históricos",
                "Viaja em casal ou grupos organizados",
                "Média de 4-6 dias",
                "Orçamento: $120-250/dia"
            ]
        ),
        TouristSegment(
            segment_id="negocios_lazer",
            name="Negócios + Lazer",
            description="Combina viagens de negócios com turismo",
            typical_destinations=["Luanda", "Benguela", "Lubango"],
            avg_budget="high",
            percentage=15.0,
            characteristics=[
                "Estadia em hotéis de negócios",
                "Viaja frequentemente",
                "Média de 3-5 dias",
                "Orçamento: $200-400/dia"
            ]
        ),
        TouristSegment(
            segment_id="ecoturista",
            name="Ecoturista Consciente",
            description="Foco em sustentabilidade e preservação ambiental",
            typical_destinations=["Iona National Park", "Kissama", "Cunene"],
            avg_budget="medium-high",
            percentage=5.0,
            characteristics=[
                "Prefere ecoturismo e safaris",
                "Viaja em grupos especializados",
                "Média de 7-14 dias",
                "Orçamento: $180-350/dia"
            ]
        )
    ]
    
    return SegmentsResponse(
        segments=segments,
        total_segments=len(segments),
        model_version="v0.1.0-clustering-fallback"
    )


# ============================================================================
# Endpoint de modelos e métricas
# ============================================================================

class ModelInfo(BaseModel):
    """Informações sobre modelo treinado"""
    province: str
    model_path: str
    metrics: dict
    loaded: bool


class ModelsListResponse(BaseModel):
    """Lista de modelos disponíveis"""
    models: List[ModelInfo]
    total_models: int
    generated_at: datetime = Field(default_factory=datetime.utcnow)


@router.get("/models", response_model=ModelsListResponse)
async def list_available_models():
    """
    Lista todos os modelos treinados disponíveis com suas métricas
    
    Retorna informações sobre:
    - Província do modelo
    - Path do arquivo do modelo
    - Métricas (MAE, MAPE, test samples)
    - Status de carregamento
    """
    forecast_service = get_forecast_service()
    models = forecast_service.list_available_models()
    
    return ModelsListResponse(
        models=[ModelInfo(**m) for m in models],
        total_models=len(models)
    )


# ============================================================================
# Endpoint de saúde do módulo ML
# ============================================================================

@router.get("/health")
async def ml_health_check():
    """
    Verifica status do módulo ML
    """
    forecast_service = get_forecast_service()
    available_models = forecast_service.list_available_models()
    
    return {
        "status": "healthy",
        "module": "ml",
        "endpoints": ["forecast", "recommend", "segments", "models"],
        "trained_models": len(available_models),
        "model_status": "trained models available" if available_models else "using fallback",
        "timestamp": datetime.utcnow().isoformat()
    }
