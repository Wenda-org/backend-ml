#!/usr/bin/env python3
"""
Script para verificar tabelas no banco de dados
"""

import os
import sys

def check_tables():
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
    
    # Verificar se psycopg está instalado
    try:
        import psycopg
    except ImportError as e:
        print('ERROR: psycopg not installed:', e)
        return 1
    
    # Conectar e verificar tabelas
    try:
        print(f"Connecting to database...")
        conn = psycopg.connect(db_url, connect_timeout=10)
        
        with conn.cursor() as cur:
            # Verificar todas as tabelas
            cur.execute("""
                SELECT table_schema, table_name, table_type 
                FROM information_schema.tables 
                WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
                ORDER BY table_schema, table_name;
            """)
            tables = cur.fetchall()
            
            if tables:
                print(f"\n✅ Found {len(tables)} tables:")
                print("-" * 60)
                for schema, table, table_type in tables:
                    print(f"Schema: {schema}, Table: {table}, Type: {table_type}")
                print("-" * 60)
            else:
                print("\n❌ No tables found in database!")
                
            # Verificar se há tabelas do alembic
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'alembic_version';
            """)
            alembic_table = cur.fetchone()
            
            if alembic_table:
                print(f"\n✓ Alembic version table found: {alembic_table[0]}")
                
                # Verificar a versão atual do alembic
                cur.execute("SELECT version_num FROM alembic_version;")
                version = cur.fetchone()
                print(f"Current alembic version: {version[0]}")
            else:
                print("\n❌ Alembic version table NOT found!")
                
        conn.close()
        return 0
        
    except Exception as e:
        print(f'ERROR: Could not connect to database: {e}')
        return 3

if __name__ == "__main__":
    sys.exit(check_tables())
