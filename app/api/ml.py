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
    
    **Placeholder:** Atualmente usa média histórica + tendência.
    Futuramente será substituído por modelo de séries temporais (SARIMA/Prophet).
    
    **Algoritmo placeholder:**
    1. Busca dados históricos dos últimos 3 anos para a província
    2. Calcula média do mesmo mês em anos anteriores
    3. Aplica tendência de crescimento (5% ao ano)
    4. Adiciona sazonalidade
    5. Calcula intervalo de confiança (±15%)
    """
    
    # Validar província
    valid_provinces = ["Luanda", "Benguela", "Huila", "Namibe", "Cunene", "Malanje"]
    if request.province not in valid_provinces:
        raise HTTPException(
            status_code=400,
            detail=f"Província inválida. Use uma de: {', '.join(valid_provinces)}"
        )
    
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
        model_version="v0.1.0-baseline-avg"
    )


@router.post("/recommend", response_model=RecommendResponse)
async def recommend_destinations(
    request: RecommendRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Recomenda destinos personalizados baseado em preferências
    
    **Placeholder:** Usa filtros simples + popularidade.
    Futuramente implementará:
    - Content-based filtering (similaridade de destinos)
    - Collaborative filtering (comportamento de usuários similares)
    - Hybrid approach
    
    **Algoritmo placeholder:**
    1. Filtra destinos por categorias preferidas
    2. Filtra por províncias (se especificado)
    3. Ordena por rating + popularidade
    4. Retorna top N com scores calculados
    """
    
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
        model_version="v0.1.0-content-filter"
    )


@router.get("/segments", response_model=SegmentsResponse)
async def get_tourist_segments():
    """
    Retorna perfis/clusters de turistas identificados
    
    **Placeholder:** Perfis hardcoded baseados nos docs de estratégia.
    Futuramente será gerado por clustering (K-Means) sobre dados reais de:
    - Padrões de visita
    - Gastos médios
    - Preferências de categorias
    - Duração de estadia
    
    **Fonte:** docs/perfis-viajantes-wenda.md
    """
    
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
        model_version="v0.1.0-clustering-placeholder"
    )


# ============================================================================
# Endpoint de saúde do módulo ML
# ============================================================================

@router.get("/health")
async def ml_health_check():
    """
    Verifica status do módulo ML
    """
    return {
        "status": "healthy",
        "module": "ml",
        "endpoints": ["forecast", "recommend", "segments"],
        "model_status": "placeholder - using baseline algorithms",
        "timestamp": datetime.utcnow().isoformat()
    }
