"""
Script para popular o banco de dados com dados de exemplo para desenvolvimento e testes.

Popula:
- Users (turistas, operadores, admin)
- Destinations (destinos turísticos de Angola)
- Tourism Statistics (dados históricos 2022-2024)
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
import random

# Adicionar o diretório raiz ao path para importar módulos do app
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import re

from app.models import User, Destination, TourismStatistics


# Normalizar DATABASE_URL para asyncpg
def normalize_database_url(url: str) -> str:
    """Converte URL do formato psycopg para asyncpg"""
    if not url:
        raise ValueError("DATABASE_URL não encontrada")
    
    # Converter para asyncpg dialect
    url = url.replace('postgresql://', 'postgresql+asyncpg://')
    
    # Remover parâmetros incompatíveis com asyncpg
    url = re.sub(r'[?&]channel_binding=\w+', '', url)
    url = url.replace('sslmode=require', 'ssl=require')
    
    return url


# Dados de exemplo
USERS_DATA = [
    {
        "name": "João Silva",
        "email": "joao.silva@example.com",
        "password_hash": "$2b$12$KIX.dummy.hash.for.testing",  # Senha: senha123
        "role": "tourist",
        "country": "Angola"
    },
    {
        "name": "Maria Santos",
        "email": "maria.santos@example.com",
        "password_hash": "$2b$12$KIX.dummy.hash.for.testing",
        "role": "tourist",
        "country": "Portugal"
    },
    {
        "name": "Carlos Mendes",
        "email": "carlos.mendes@example.com",
        "password_hash": "$2b$12$KIX.dummy.hash.for.testing",
        "role": "tourist",
        "country": "Brazil"
    },
    {
        "name": "Ana Costa",
        "email": "ana.costa@turismo.ao",
        "password_hash": "$2b$12$KIX.dummy.hash.for.testing",
        "role": "operator",
        "country": "Angola"
    },
    {
        "name": "Pedro Tavares",
        "email": "pedro.tavares@wenda.ao",
        "password_hash": "$2b$12$KIX.dummy.hash.for.testing",
        "role": "operator",
        "country": "Angola"
    },
    {
        "name": "Admin Wenda",
        "email": "admin@wenda.ao",
        "password_hash": "$2b$12$KIX.dummy.hash.for.testing",
        "role": "admin",
        "country": "Angola"
    },
]

DESTINATIONS_DATA = [
    # Luanda
    {
        "name": "Fortaleza de São Miguel",
        "province": "Luanda",
        "description": "Fortaleza militar portuguesa construída em 1576. Abriga o Museu das Forças Armadas com vasta coleção histórica.",
        "latitude": -8.8099,
        "longitude": 13.2344,
        "category": "culture",
        "rating_avg": 4.5,
        "images": ["fortaleza_sao_miguel_1.jpg", "fortaleza_sao_miguel_2.jpg"]
    },
    {
        "name": "Ilha do Mussulo",
        "province": "Luanda",
        "description": "Península de areia com 30km de extensão, praias paradisíacas e restaurantes à beira-mar.",
        "latitude": -9.0833,
        "longitude": 12.9167,
        "category": "beach",
        "rating_avg": 4.7,
        "images": ["ilha_mussulo_1.jpg", "ilha_mussulo_2.jpg"]
    },
    {
        "name": "Miradouro da Lua",
        "province": "Luanda",
        "description": "Formações rochosas únicas esculpidas pela erosão, paisagem lunar ao pôr do sol.",
        "latitude": -9.3167,
        "longitude": 13.1333,
        "category": "nature",
        "rating_avg": 4.6,
        "images": ["miradouro_lua_1.jpg", "miradouro_lua_2.jpg"]
    },
    {
        "name": "Museu Nacional de Antropologia",
        "province": "Luanda",
        "description": "Acervo rico sobre culturas e etnias angolanas, arte tradicional e arqueologia.",
        "latitude": -8.8383,
        "longitude": 13.2344,
        "category": "culture",
        "rating_avg": 4.3,
        "images": ["museu_antropologia_1.jpg"]
    },
    {
        "name": "Baía de Luanda",
        "province": "Luanda",
        "description": "Marginal renovada com palmeiras, restaurantes e vista para o Atlântico. Ótima para caminhadas.",
        "latitude": -8.8061,
        "longitude": 13.2302,
        "category": "beach",
        "rating_avg": 4.4,
        "images": ["baia_luanda_1.jpg", "baia_luanda_2.jpg"]
    },
    
    # Benguela
    {
        "name": "Praia Morena",
        "province": "Benguela",
        "description": "Uma das praias mais bonitas de Angola, areia dourada e águas cristalinas.",
        "latitude": -12.5833,
        "longitude": 13.4000,
        "category": "beach",
        "rating_avg": 4.8,
        "images": ["praia_morena_1.jpg", "praia_morena_2.jpg"]
    },
    {
        "name": "Baía Azul",
        "province": "Benguela",
        "description": "Praia urbana famosa com infraestrutura turística e eventos culturais.",
        "latitude": -12.5667,
        "longitude": 13.4167,
        "category": "beach",
        "rating_avg": 4.5,
        "images": ["baia_azul_1.jpg"]
    },
    {
        "name": "Catumbela",
        "province": "Benguela",
        "description": "Cidade costeira com praias tranquilas e rio Catumbela para pesca.",
        "latitude": -12.4333,
        "longitude": 13.5500,
        "category": "beach",
        "rating_avg": 4.2,
        "images": ["catumbela_1.jpg"]
    },
    {
        "name": "Igreja da Nossa Senhora do Pópulo",
        "province": "Benguela",
        "description": "Igreja histórica do século XVII, arquitetura colonial portuguesa.",
        "latitude": -12.5761,
        "longitude": 13.4055,
        "category": "culture",
        "rating_avg": 4.0,
        "images": ["igreja_populo_1.jpg"]
    },
    
    # Huíla
    {
        "name": "Fenda da Tundavala",
        "province": "Huila",
        "description": "Miradouro espetacular com vista de 1000m sobre o vale. Um dos cartões-postais de Angola.",
        "latitude": -14.9167,
        "longitude": 13.3167,
        "category": "nature",
        "rating_avg": 4.9,
        "images": ["tundavala_1.jpg", "tundavala_2.jpg", "tundavala_3.jpg"]
    },
    {
        "name": "Serra da Leba",
        "province": "Huila",
        "description": "Estrada sinuosa com curvas espetaculares descendo a montanha. Obra-prima de engenharia.",
        "latitude": -14.9500,
        "longitude": 13.2833,
        "category": "nature",
        "rating_avg": 4.8,
        "images": ["serra_leba_1.jpg", "serra_leba_2.jpg"]
    },
    {
        "name": "Cristo Rei do Lubango",
        "province": "Huila",
        "description": "Estátua de Cristo com 30m de altura, vista panorâmica da cidade do Lubango.",
        "latitude": -14.9167,
        "longitude": 13.4833,
        "category": "culture",
        "rating_avg": 4.6,
        "images": ["cristo_rei_1.jpg"]
    },
    {
        "name": "Cascatas da Huíla",
        "province": "Huila",
        "description": "Conjunto de quedas d'água em meio à vegetação exuberante. Ideal para picnics.",
        "latitude": -14.8833,
        "longitude": 13.5167,
        "category": "nature",
        "rating_avg": 4.4,
        "images": ["cascatas_huila_1.jpg"]
    },
    
    # Namibe
    {
        "name": "Deserto do Namibe",
        "province": "Namibe",
        "description": "Deserto costeiro mais antigo do mundo, dunas gigantes e paisagens marciais.",
        "latitude": -15.1667,
        "longitude": 12.1500,
        "category": "nature",
        "rating_avg": 4.9,
        "images": ["deserto_namibe_1.jpg", "deserto_namibe_2.jpg"]
    },
    {
        "name": "Iona National Park",
        "province": "Namibe",
        "description": "Maior parque nacional de Angola, vida selvagem diversificada e paisagens desérticas.",
        "latitude": -16.5000,
        "longitude": 12.5000,
        "category": "nature",
        "rating_avg": 4.7,
        "images": ["iona_park_1.jpg", "iona_park_2.jpg"]
    },
    {
        "name": "Arco do Namibe",
        "province": "Namibe",
        "description": "Formação rochosa natural em forma de arco, encontro do deserto com o oceano.",
        "latitude": -15.0833,
        "longitude": 12.1167,
        "category": "nature",
        "rating_avg": 4.6,
        "images": ["arco_namibe_1.jpg"]
    },
    {
        "name": "Praia dos Flamingos",
        "province": "Namibe",
        "description": "Praia isolada onde flamingos migram. Natureza intocada e tranquilidade.",
        "latitude": -15.1500,
        "longitude": 12.1000,
        "category": "beach",
        "rating_avg": 4.5,
        "images": ["praia_flamingos_1.jpg"]
    },
    
    # Cunene
    {
        "name": "Cataratas do Ruacaná",
        "province": "Cunene",
        "description": "Quedas d'água impressionantes no rio Cunene, fronteira com Namíbia.",
        "latitude": -17.4167,
        "longitude": 14.2167,
        "category": "nature",
        "rating_avg": 4.7,
        "images": ["ruacana_1.jpg", "ruacana_2.jpg"]
    },
    
    # Cuando Cubango
    {
        "name": "Parque Nacional do Luengue-Luiana",
        "province": "Cuando Cubango",
        "description": "Parque de conservação com fauna africana: elefantes, leões, antílopes.",
        "latitude": -15.5000,
        "longitude": 20.0000,
        "category": "nature",
        "rating_avg": 4.6,
        "images": ["luengue_luiana_1.jpg"]
    },
    
    # Malanje
    {
        "name": "Quedas de Calandula",
        "province": "Malanje",
        "description": "Segundas maiores quedas de África (105m), espetáculo natural imperdível.",
        "latitude": -9.2833,
        "longitude": 15.8167,
        "category": "nature",
        "rating_avg": 5.0,
        "images": ["calandula_1.jpg", "calandula_2.jpg", "calandula_3.jpg"]
    },
    {
        "name": "Pedras Negras de Pungo Andongo",
        "province": "Malanje",
        "description": "Formações rochosas gigantescas de granito negro, mistério geológico.",
        "latitude": -9.6833,
        "longitude": 15.4500,
        "category": "nature",
        "rating_avg": 4.7,
        "images": ["pungo_andongo_1.jpg"]
    },
    
    # Lunda Norte
    {
        "name": "Museu do Dundo",
        "province": "Lunda Norte",
        "description": "Museu etnográfico com coleção Chokwe, arte africana e história da mineração.",
        "latitude": -7.3833,
        "longitude": 20.8333,
        "category": "culture",
        "rating_avg": 4.4,
        "images": ["museu_dundo_1.jpg"]
    },
    
    # Uíge
    {
        "name": "Maquela do Zombo",
        "province": "Uige",
        "description": "Região montanhosa com vistas panorâmicas e clima ameno.",
        "latitude": -7.0500,
        "longitude": 15.1667,
        "category": "nature",
        "rating_avg": 4.2,
        "images": ["maquela_zombo_1.jpg"]
    },
]


async def clear_existing_data(session: AsyncSession):
    """Remove todos os dados existentes (útil para re-seed)"""
    print("🗑️  Limpando dados existentes...")
    
    # Ordem importa por causa das foreign keys
    await session.execute(text("DELETE FROM recommendations_log"))
    await session.execute(text("DELETE FROM ml_predictions"))
    await session.execute(text("DELETE FROM tourism_statistics"))
    await session.execute(text("DELETE FROM destinations"))
    await session.execute(text("DELETE FROM users"))
    
    await session.commit()
    print("✅ Dados antigos removidos")


async def seed_users(session: AsyncSession):
    """Popula tabela de users"""
    print(f"\n👥 Inserindo {len(USERS_DATA)} users...")
    
    users = []
    for user_data in USERS_DATA:
        user = User(**user_data)
        users.append(user)
        session.add(user)
    
    await session.commit()
    print(f"✅ {len(users)} users criados")
    return users


async def seed_destinations(session: AsyncSession):
    """Popula tabela de destinations"""
    print(f"\n📍 Inserindo {len(DESTINATIONS_DATA)} destinos...")
    
    destinations = []
    for dest_data in DESTINATIONS_DATA:
        destination = Destination(**dest_data)
        destinations.append(destination)
        session.add(destination)
    
    await session.commit()
    print(f"✅ {len(destinations)} destinos criados")
    return destinations


async def seed_tourism_statistics(session: AsyncSession):
    """
    Gera dados históricos de estatísticas de turismo (2022-2024)
    com sazonalidade realista para Angola
    """
    print("\n📊 Gerando estatísticas de turismo (2022-2024)...")
    
    provinces = ["Luanda", "Benguela", "Huila", "Namibe", "Cunene", "Malanje"]
    
    # Bases de visitantes por província (média mensal)
    province_base_visitors = {
        "Luanda": 12000,      # Capital, maior fluxo
        "Benguela": 4500,     # Praias populares
        "Huila": 3000,        # Serra da Leba, Tundavala
        "Namibe": 1500,       # Deserto, mais remoto
        "Cunene": 800,        # Menos turístico
        "Malanje": 2000,      # Calandula
    }
    
    # Sazonalidade: Dezembro/Janeiro (férias de verão) e Julho/Agosto (inverno)
    seasonal_multipliers = {
        1: 1.3,   # Janeiro - férias
        2: 0.9,   # Fevereiro
        3: 0.8,   # Março
        4: 0.9,   # Abril
        5: 0.95,  # Maio
        6: 1.0,   # Junho
        7: 1.25,  # Julho - férias inverno
        8: 1.2,   # Agosto - férias inverno
        9: 0.9,   # Setembro
        10: 0.85, # Outubro
        11: 0.95, # Novembro
        12: 1.4,  # Dezembro - férias verão
    }
    
    stats = []
    
    for year in [2022, 2023, 2024]:
        for month in range(1, 13):
            for province in provinces:
                base = province_base_visitors[province]
                seasonal = seasonal_multipliers[month]
                
                # Adicionar variação aleatória (-10% a +10%)
                random_var = random.uniform(0.9, 1.1)
                
                # Tendência de crescimento ano a ano (5% ao ano)
                year_growth = 1 + (year - 2022) * 0.05
                
                visitors = int(base * seasonal * random_var * year_growth)
                
                # Taxa de ocupação hoteleira (correlacionada com visitantes)
                # Base: 60-70%, picos: até 85-90%
                base_occupancy = 0.65
                occupancy = min(0.95, base_occupancy * seasonal * random.uniform(0.95, 1.05))
                
                # Dividir visitantes em domésticos (70%) e estrangeiros (30%)
                domestic = int(visitors * 0.7)
                foreign = int(visitors * 0.3)
                
                # Duração média de estadia (3-7 dias)
                avg_stay = round(random.uniform(3.0, 7.0), 1)
                
                stat = TourismStatistics(
                    province=province,
                    month=month,
                    year=year,
                    domestic_visitors=domestic,
                    foreign_visitors=foreign,
                    occupancy_rate=round(occupancy, 2),
                    avg_stay_days=avg_stay
                )
                stats.append(stat)
                session.add(stat)
    
    await session.commit()
    print(f"✅ {len(stats)} registros de estatísticas criados")
    print(f"   - Anos: 2022-2024")
    print(f"   - Províncias: {', '.join(provinces)}")
    print(f"   - Total: {len(stats)} meses de dados")


async def main():
    """Função principal para executar o seed"""
    print("=" * 60)
    print("🌱 SEED DATA - Wenda ML Backend")
    print("=" * 60)
    
    # Obter DATABASE_URL
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("❌ Erro: DATABASE_URL não encontrada no ambiente")
        print("Execute: export DATABASE_URL='...'")
        return
    
    # Normalizar URL
    database_url = normalize_database_url(database_url)
    print(f"📡 Conectando ao banco de dados...")
    
    # Criar engine e session
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Opcionalmente limpar dados existentes
        # Descomente a linha abaixo se quiser fazer re-seed
        # await clear_existing_data(session)
        
        # Inserir dados
        users = await seed_users(session)
        destinations = await seed_destinations(session)
        await seed_tourism_statistics(session)
    
    await engine.dispose()
    
    print("\n" + "=" * 60)
    print("✅ SEED COMPLETO!")
    print("=" * 60)
    print(f"📊 Resumo:")
    print(f"   - {len(USERS_DATA)} users (turistas, operadores, admin)")
    print(f"   - {len(DESTINATIONS_DATA)} destinos turísticos")
    print(f"   - 216 registros de estatísticas (3 anos × 12 meses × 6 províncias)")
    print("\n💡 Próximo passo: Testar os dados")
    print("   python3 scripts/check-tables-async.py")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
