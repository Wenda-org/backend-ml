#!/usr/bin/env python3
"""
Script para verificar tabelas no banco de dados usando asyncpg
"""

import os
import sys
import asyncio
import re

async def check_tables():
    print("Checking tables in database...")
    
    # Carregar variáveis de ambiente do arquivo .env se existir
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"Loading environment variables from {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    
    # Verificar se DATABASE_URL está definida
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print('ERROR: DATABASE_URL not set in environment variables')
        return 1
    
    # Verificar se asyncpg está instalado
    try:
        import asyncpg
    except ImportError as e:
        print('ERROR: asyncpg not installed:', e)
        return 1
    
    # Normalizar URL para asyncpg (remover dialeto se presente)
    db_url_clean = re.sub(r'postgresql\+\w+://', 'postgresql://', db_url)
    
    # Conectar e verificar tabelas
    try:
        print(f"Connecting to database...")
        conn = await asyncpg.connect(db_url_clean, timeout=10)
        
        # Verificar todas as tabelas
        tables = await conn.fetch("""
            SELECT table_schema, table_name, table_type 
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
            ORDER BY table_schema, table_name;
        """)
        
        if tables:
            print(f"\n✅ Found {len(tables)} tables:")
            print("-" * 60)
            for row in tables:
                print(f"Schema: {row['table_schema']}, Table: {row['table_name']}, Type: {row['table_type']}")
            print("-" * 60)
        else:
            print("\n❌ No tables found in database!")
            
        # Verificar se há tabelas do alembic
        alembic_table = await conn.fetchval("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'alembic_version';
        """)
        
        if alembic_table:
            print(f"\n✓ Alembic version table found: {alembic_table}")
            
            # Verificar a versão atual do alembic
            version = await conn.fetchval("SELECT version_num FROM alembic_version;")
            print(f"Current alembic version: {version}")
        else:
            print("\n❌ Alembic version table NOT found!")
            
        await conn.close()
        return 0
        
    except Exception as e:
        print(f'ERROR: Could not connect to database: {e}')
        return 3

if __name__ == "__main__":
    sys.exit(asyncio.run(check_tables()))
