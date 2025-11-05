#!/usr/bin/env python3
"""
Script para executar migrações do Alembic
"""

import os
import sys
from pathlib import Path

def run_migrations():
    print("Running Alembic migrations...")
    
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
    
    print(f"Database URL: {db_url.split('@')[0]}@...")
    
    # Verificar se alembic está instalado
    try:
        from alembic.config import Config
        from alembic import command
    except ImportError as e:
        print('ERROR: Alembic not installed:', e)
        return 2
    
    # Verificar se psycopg está instalado (para psycopg3)
    try:
        import psycopg
        print("✓ psycopg (psycopg3) available")
    except ImportError as e:
        print('ERROR: psycopg not installed:', e)
        return 3
    
    # Configurar e executar migrações
    try:
        # Configurar Alembic
        alembic_cfg = Config("alembic.ini")
        
        # Verificar se o arquivo alembic.ini existe
        if not Path("alembic.ini").exists():
            print("ERROR: alembic.ini not found")
            return 4
        
        # Garantir que estamos usando psycopg3 na URL
        db_url = db_url.replace('postgresql+psycopg2://', 'postgresql+psycopg://')
        
        # Configurar a URL do banco diretamente (sobrescreve o alembic.ini)
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)
        print("✓ Database URL configured for migrations")
        
        print("Running migrations...")
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrations completed successfully!")
        return 0
        
    except Exception as e:
        print('❌ ERROR: Failed to run migrations:', e)
        
        # Diagnóstico adicional
        if "psycopg2" in str(e):
            print("\n💡 Issue detected: Trying to use psycopg2 but you have psycopg3")
            print("Make sure your DATABASE_URL uses 'postgresql+psycopg://' not 'postgresql+psycopg2://'")
        
        return 5

if __name__ == "__main__":
    sys.exit(run_migrations())
