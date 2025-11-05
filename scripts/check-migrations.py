#!/usr/bin/env python3
"""
Script para verificar o histórico de migrações
"""

import os
import sys
from pathlib import Path

def check_migrations():
    print("Checking migration history...")
    
    # Carregar variáveis de ambiente
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
    
    # Verificar se alembic está instalado
    try:
        from alembic.config import Config
        from alembic import command
    except ImportError as e:
        print('ERROR: Alembic not installed:', e)
        return 2
    
    try:
        # Configurar Alembic
        alembic_cfg = Config("alembic.ini")
        
        # Verificar migrações aplicadas
        print("\nChecking applied migrations...")
        command.current(alembic_cfg)
        
        # Verificar histórico
        print("\nMigration history:")
        command.history(alembic_cfg)
        
        return 0
        
    except Exception as e:
        print(f'ERROR: Failed to check migrations: {e}')
        return 3

if __name__ == "__main__":
    sys.exit(check_migrations())
