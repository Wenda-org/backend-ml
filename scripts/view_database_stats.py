#!/usr/bin/env python3
"""
Script para visualizar estatísticas do banco de dados
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

def view_stats():
    load_env()
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return
    
    try:
        conn = psycopg.connect(database_url, connect_timeout=10, row_factory=dict_row)
        cur = conn.cursor()
        
        print("\n" + "=" * 70)
        print("📊 ESTATÍSTICAS DO BANCO DE DADOS WENDA")
        print("=" * 70)
        
        # Usuários
        cur.execute("SELECT COUNT(*) as total FROM users")
        total_users = cur.fetchone()['total']
        
        cur.execute("SELECT role, COUNT(*) as count FROM users GROUP BY role ORDER BY count DESC")
        users_by_role = cur.fetchall()
        
        print(f"\n👥 USUÁRIOS: {total_users}")
        for row in users_by_role:
            print(f"   - {row['role']}: {row['count']}")
        
        # Destinos
        cur.execute("SELECT COUNT(*) as total FROM destinations")
        total_destinations = cur.fetchone()['total']
        
        cur.execute("""
            SELECT c.name, COUNT(d.id) as count 
            FROM categories c 
            LEFT JOIN destinations d ON d.category_id = c.id 
            GROUP BY c.name 
            ORDER BY count DESC
        """)
        destinations_by_category = cur.fetchall()
        
        cur.execute("SELECT COUNT(*) as count FROM destinations WHERE is_featured = true")
        featured_count = cur.fetchone()['count']
        
        print(f"\n🏖️  DESTINOS: {total_destinations}")
        print(f"   - Em destaque: {featured_count}")
        for row in destinations_by_category:
            print(f"   - {row['name']}: {row['count']}")
        
        # Províncias
        cur.execute("""
            SELECT province, COUNT(*) as count 
            FROM destinations 
            GROUP BY province 
            ORDER BY count DESC
        """)
        destinations_by_province = cur.fetchall()
        
        print(f"\n📍 DESTINOS POR PROVÍNCIA:")
        for row in destinations_by_province:
            print(f"   - {row['province']}: {row['count']}")
        
        # Imagens
        cur.execute("SELECT COUNT(*) as total FROM destination_images")
        total_images = cur.fetchone()['total']
        
        cur.execute("SELECT COUNT(*) as count FROM destination_images WHERE is_main = true")
        main_images = cur.fetchone()['count']
        
        print(f"\n📸 IMAGENS: {total_images}")
        print(f"   - Principais: {main_images}")
        print(f"   - Adicionais: {total_images - main_images}")
        
        # Reviews
        cur.execute("SELECT COUNT(*) as total FROM reviews")
        total_reviews = cur.fetchone()['total']
        
        cur.execute("SELECT AVG(rating) as avg_rating FROM reviews")
        avg_rating = cur.fetchone()['avg_rating'] or 0
        
        cur.execute("SELECT rating, COUNT(*) as count FROM reviews GROUP BY rating ORDER BY rating DESC")
        reviews_by_rating = cur.fetchall()
        
        cur.execute("SELECT COUNT(*) as count FROM reviews WHERE is_verified = true")
        verified_reviews = cur.fetchone()['count']
        
        print(f"\n⭐ AVALIAÇÕES: {total_reviews}")
        print(f"   - Média geral: {float(avg_rating):.2f} ⭐")
        print(f"   - Verificadas: {verified_reviews}")
        for row in reviews_by_rating:
            stars = "⭐" * row['rating']
            print(f"   - {stars} ({row['rating']}): {row['count']}")
        
        # Review images
        cur.execute("SELECT COUNT(*) as total FROM review_images")
        review_images = cur.fetchone()['total']
        
        print(f"\n📷 FOTOS DE AVALIAÇÕES: {review_images}")
        
        # Helpful votes
        cur.execute("SELECT COUNT(*) as total FROM review_helpful")
        helpful_votes = cur.fetchone()['total']
        
        print(f"\n👍 VOTOS 'ÚTIL': {helpful_votes}")
        
        # Favoritos
        cur.execute("SELECT COUNT(*) as total FROM favorites")
        total_favorites = cur.fetchone()['total']
        
        cur.execute("""
            SELECT d.name, COUNT(f.user_id) as count 
            FROM destinations d 
            LEFT JOIN favorites f ON f.destination_id = d.id 
            GROUP BY d.name 
            HAVING COUNT(f.user_id) > 0
            ORDER BY count DESC 
            LIMIT 5
        """)
        top_favorites = cur.fetchall()
        
        print(f"\n❤️  FAVORITOS: {total_favorites}")
        if top_favorites:
            print(f"   Top 5 destinos favoritos:")
            for row in top_favorites:
                print(f"   - {row['name']}: {row['count']} ❤️")
        
        # Viagens
        cur.execute("SELECT COUNT(*) as total FROM trips")
        total_trips = cur.fetchone()['total']
        
        cur.execute("SELECT status, COUNT(*) as count FROM trips GROUP BY status ORDER BY count DESC")
        trips_by_status = cur.fetchall()
        
        print(f"\n🗺️  VIAGENS: {total_trips}")
        for row in trips_by_status:
            print(f"   - {row['status']}: {row['count']}")
        
        # Destinos em viagens
        cur.execute("SELECT COUNT(*) as total FROM trip_destinations")
        trip_destinations = cur.fetchone()['total']
        
        print(f"\n📌 DESTINOS EM VIAGENS: {trip_destinations}")
        
        # Preferências
        cur.execute("SELECT COUNT(*) as total FROM user_preferences")
        total_prefs = cur.fetchone()['total']
        
        cur.execute("SELECT theme, COUNT(*) as count FROM user_preferences GROUP BY theme")
        prefs_by_theme = cur.fetchall()
        
        print(f"\n⚙️  PREFERÊNCIAS: {total_prefs}")
        for row in prefs_by_theme:
            print(f"   - Tema {row['theme']}: {row['count']}")
        
        # Top destinos avaliados
        print(f"\n🏆 TOP 5 DESTINOS MAIS AVALIADOS:")
        cur.execute("""
            SELECT d.name, d.province, COUNT(r.id) as review_count, AVG(r.rating) as avg_rating
            FROM destinations d
            LEFT JOIN reviews r ON r.destination_id = d.id
            GROUP BY d.id, d.name, d.province
            HAVING COUNT(r.id) > 0
            ORDER BY review_count DESC, avg_rating DESC
            LIMIT 5
        """)
        top_reviewed = cur.fetchall()
        
        for i, row in enumerate(top_reviewed, 1):
            print(f"   {i}. {row['name']} ({row['province']})")
            print(f"      {row['review_count']} reviews | Média: {float(row['avg_rating']):.1f} ⭐")
        
        # Usuários mais ativos
        print(f"\n👤 TOP 5 USUÁRIOS MAIS ATIVOS:")
        cur.execute("""
            SELECT u.name, u.email, 
                   COUNT(DISTINCT r.id) as reviews_count,
                   COUNT(DISTINCT f.destination_id) as favorites_count,
                   COUNT(DISTINCT t.id) as trips_count
            FROM users u
            LEFT JOIN reviews r ON r.user_id = u.id
            LEFT JOIN favorites f ON f.user_id = u.id
            LEFT JOIN trips t ON t.user_id = u.id
            WHERE u.role = 'tourist'
            GROUP BY u.id, u.name, u.email
            ORDER BY (COUNT(DISTINCT r.id) + COUNT(DISTINCT f.destination_id) + COUNT(DISTINCT t.id)) DESC
            LIMIT 5
        """)
        active_users = cur.fetchall()
        
        for i, row in enumerate(active_users, 1):
            total_activity = row['reviews_count'] + row['favorites_count'] + row['trips_count']
            print(f"   {i}. {row['name']} ({row['email']})")
            print(f"      {row['reviews_count']} reviews | {row['favorites_count']} favoritos | {row['trips_count']} viagens")
        
        print("\n" + "=" * 70)
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    view_stats()
