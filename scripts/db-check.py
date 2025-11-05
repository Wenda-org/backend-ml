#!/usr/bin/env python3
"""
Script para verificar conexão com o banco de dados
"""

import os
import sys

def check_database_connection():
    print("Checking DATABASE_URL...")
    
    # Verificar se psycopg está instalado
    try:
        import psycopg
    except ImportError as e:
        print('ERROR: psycopg not installed:', e)
        return 1
    
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
        return 2
    
    # Tentar conectar ao banco de dados
    try:
        print(f"Attempting to connect to database...")
        conn = psycopg.connect(db_url, connect_timeout=5)
        # Testar uma consulta simples
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()
            print(f"OK: Connected to database - {version[0]}")
        conn.close()
        return 0
    except Exception as e:
        print('ERROR: Could not connect to database:', e)
        return 3

if __name__ == "__main__":
    sys.exit(check_database_connection())
