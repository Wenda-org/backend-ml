#!/usr/bin/env python3
"""
Script para verificar quais tabelas do ML estão faltando no banco de dados
"""
import os
import psycopg
from psycopg.rows import dict_row

def load_env():
    """Carregar variáveis de ambiente do .env"""
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def check_ml_tables():
    load_env()
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL não encontrada no .env")
        return
    
    try:
        conn = psycopg.connect(database_url, connect_timeout=10, row_factory=dict_row)
        cur = conn.cursor()
        
        # Tabelas necessárias para o backend ML
        required_tables = {
            'users': 'Compartilhada - Usuários',
            'destinations': 'Compartilhada - Destinos turísticos',
            'tourism_statistics': 'ML - Estatísticas de turismo',
            'ml_models_registry': 'ML - Registro de modelos',
            'ml_predictions': 'ML - Previsões dos modelos',
            'recommendations_log': 'ML - Log de recomendações'
        }
        
        print("\n" + "=" * 70)
        print("🔍 VERIFICANDO TABELAS NECESSÁRIAS PARA O BACKEND ML")
        print("=" * 70 + "\n")
        
        # Verificar quais tabelas existem
        cur.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        existing_tables = {row['tablename'] for row in cur.fetchall()}
        
        missing_tables = []
        present_tables = []
        
        for table, description in required_tables.items():
            if table in existing_tables:
                print(f"✅ {table.ljust(25)} - {description}")
                present_tables.append(table)
            else:
                print(f"❌ {table.ljust(25)} - {description} [FALTANDO]")
                missing_tables.append(table)
        
        print("\n" + "=" * 70)
        
        if not missing_tables:
            print("🎉 TODAS AS TABELAS NECESSÁRIAS ESTÃO PRESENTES!")
            print("\n✅ Backend ML está pronto para funcionar!")
        else:
            print(f"⚠️  {len(missing_tables)} TABELA(S) FALTANDO!")
            print("\n📋 Tabelas que precisam ser criadas:")
            for table in missing_tables:
                print(f"   - {table}")
            
            print("\n💡 PRÓXIMOS PASSOS:")
            print("\n1. OPÇÃO 1 - Via Prisma (RECOMENDADO):")
            print("   - Adicione os models do arquivo 'prisma-schema-ml-tables.prisma'")
            print("   - Execute: npx prisma migrate dev --name add_ml_tables")
            print("   - Execute: npx prisma generate")
            
            print("\n2. OPÇÃO 2 - Via SQL Direto:")
            print("   - Execute: psql $DATABASE_URL -f sql-ml-tables.sql")
            print("   - Ou copie o conteúdo de 'sql-ml-tables.sql' e execute no seu cliente")
            
            print("\n📖 Leia: README-ML-TABLES.md para instruções completas")
        
        print("\n" + "=" * 70)
        
        # Verificar campos necessários nas tabelas existentes
        if 'users' in existing_tables:
            print("\n🔍 Verificando campos da tabela 'users'...")
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'users'
                ORDER BY ordinal_position
            """)
            user_columns = {row['column_name'] for row in cur.fetchall()}
            
            required_user_fields = ['id', 'name', 'email', 'password_hash', 'role', 'created_at']
            missing_user_fields = [f for f in required_user_fields if f not in user_columns]
            
            if missing_user_fields:
                print(f"   ⚠️  Campos faltando: {', '.join(missing_user_fields)}")
            else:
                print("   ✅ Todos os campos necessários estão presentes")
        
        if 'destinations' in existing_tables:
            print("\n🔍 Verificando campos da tabela 'destinations'...")
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'destinations'
                ORDER BY ordinal_position
            """)
            dest_columns = {row['column_name'] for row in cur.fetchall()}
            
            required_dest_fields = ['id', 'name', 'province', 'description', 'latitude', 'longitude', 'created_at']
            missing_dest_fields = [f for f in required_dest_fields if f not in dest_columns]
            
            if missing_dest_fields:
                print(f"   ⚠️  Campos faltando: {', '.join(missing_dest_fields)}")
            else:
                print("   ✅ Todos os campos necessários estão presentes")
        
        print("\n" + "=" * 70 + "\n")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Erro ao conectar ao banco: {e}\n")
        print("💡 Verifique se DATABASE_URL está correto no .env")

if __name__ == "__main__":
    check_ml_tables()
