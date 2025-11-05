"""Script para contar registros em cada tabela"""

import asyncio
import os
import sys
from pathlib import Path
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncpg


def normalize_database_url(url: str) -> str:
    """Converte URL do formato psycopg para asyncpg"""
    if not url:
        raise ValueError("DATABASE_URL não encontrada")
    
    url = url.replace('postgresql://', 'postgresql+asyncpg://')
    url = re.sub(r'[?&]channel_binding=\w+', '', url)
    url = url.replace('sslmode=require', 'ssl=require')
    url = url.replace('postgresql+asyncpg://', 'postgresql://')  # asyncpg usa postgresql://
    
    # Remover ssl= para asyncpg.connect (usa connect_args)
    url = url.replace('?ssl=require', '')
    
    return url


async def count_records():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return
    
    database_url = normalize_database_url(database_url)
    
    # Conectar com SSL
    conn = await asyncpg.connect(database_url, ssl='require')
    
    print("\n📊 Contagem de registros nas tabelas:")
    print("=" * 60)
    
    tables = ["users", "destinations", "tourism_statistics", 
              "ml_models_registry", "ml_predictions", "recommendations_log"]
    
    for table in tables:
        count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
        print(f"✓ {table:25} {count:>6} registros")
    
    print("=" * 60)
    
    # Mostrar alguns exemplos
    print("\n📍 Exemplos de Destinos:")
    destinations = await conn.fetch(
        "SELECT name, province, category, rating_avg FROM destinations LIMIT 5"
    )
    for dest in destinations:
        print(f"  • {dest['name']:35} ({dest['province']:12}) - {dest['category']:10} - ⭐ {dest['rating_avg']}")
    
    print("\n👥 Exemplos de Users:")
    users = await conn.fetch(
        "SELECT name, email, role, country FROM users LIMIT 5"
    )
    for user in users:
        print(f"  • {user['name']:20} | {user['role']:10} | {user['country']}")
    
    print("\n📈 Estatísticas por Província (Total 2022-2024):")
    stats = await conn.fetch("""
        SELECT province, 
               SUM(domestic_visitors + foreign_visitors) as total_visitors,
               ROUND(AVG(occupancy_rate)::numeric, 2) as avg_occupancy
        FROM tourism_statistics
        GROUP BY province
        ORDER BY total_visitors DESC
    """)
    for stat in stats:
        print(f"  • {stat['province']:15} {stat['total_visitors']:>9} visitantes  |  {stat['avg_occupancy']}% ocupação média")
    
    await conn.close()


if __name__ == "__main__":
    asyncio.run(count_records())
