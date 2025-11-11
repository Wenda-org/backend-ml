"""
Check user data for clustering analysis.
"""
import asyncio
import asyncpg
import os

async def main():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        database_url = "postgresql://neondb_owner:npg_3aSeQW0qTPju@ep-cold-king-adyr1oj3-pooler.c-2.us-east-1.aws.neon.tech/neondb"
    
    if database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    conn = await asyncpg.connect(database_url, ssl='require')
    
    print("📊 DADOS DISPONÍVEIS PARA CLUSTERING\n")
    
    # Users
    users = await conn.fetch('SELECT COUNT(*) as cnt FROM users')
    print(f"✅ Users: {users[0]['cnt']}")
    
    # Recommendations log
    logs = await conn.fetch('SELECT COUNT(*) as cnt FROM recommendations_log')
    print(f"✅ Recommendation logs: {logs[0]['cnt']}")
    
    # Sample users
    sample = await conn.fetch('SELECT name, email, role, country FROM users LIMIT 5')
    print(f"\n📋 Sample users:")
    for row in sample:
        print(f"   {row['name']} ({row['country']}) - {row['role']}")
    
    await conn.close()

if __name__ == '__main__':
    asyncio.run(main())
