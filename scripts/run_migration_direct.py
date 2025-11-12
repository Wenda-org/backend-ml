#!/usr/bin/env python3
"""
Executa a migration SQL diretamente no banco de dados
"""
import os
import sys

SQL_MIGRATION = """
-- 1. CREATE CATEGORIES TABLE
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    slug VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50),
    color VARCHAR(7),
    is_active BOOLEAN DEFAULT true,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_categories_slug ON categories(slug);
CREATE INDEX IF NOT EXISTS idx_categories_display_order ON categories(display_order);

-- 2. ADD NEW COLUMNS TO USERS TABLE
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='avatar_url') THEN
        ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='phone') THEN
        ALTER TABLE users ADD COLUMN phone VARCHAR(20);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='bio') THEN
        ALTER TABLE users ADD COLUMN bio TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='email_verified_at') THEN
        ALTER TABLE users ADD COLUMN email_verified_at TIMESTAMP;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='google_id') THEN
        ALTER TABLE users ADD COLUMN google_id VARCHAR(255);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='apple_id') THEN
        ALTER TABLE users ADD COLUMN apple_id VARCHAR(255);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='is_active') THEN
        ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT true;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='updated_at') THEN
        ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='deleted_at') THEN
        ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- 3. ADD NEW COLUMNS TO DESTINATIONS TABLE
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='destinations' AND column_name='slug') THEN
        ALTER TABLE destinations ADD COLUMN slug VARCHAR(200);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='destinations' AND column_name='long_description') THEN
        ALTER TABLE destinations ADD COLUMN long_description TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='destinations' AND column_name='location') THEN
        ALTER TABLE destinations ADD COLUMN location VARCHAR(100);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='destinations' AND column_name='address') THEN
        ALTER TABLE destinations ADD COLUMN address TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='destinations' AND column_name='category_id') THEN
        ALTER TABLE destinations ADD COLUMN category_id UUID;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='destinations' AND column_name='opening_hours') THEN
        ALTER TABLE destinations ADD COLUMN opening_hours VARCHAR(200);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='destinations' AND column_name='ticket_price') THEN
        ALTER TABLE destinations ADD COLUMN ticket_price VARCHAR(100);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='destinations' AND column_name='phone') THEN
        ALTER TABLE destinations ADD COLUMN phone VARCHAR(20);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='destinations' AND column_name='email') THEN
        ALTER TABLE destinations ADD COLUMN email VARCHAR(255);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='destinations' AND column_name='website') THEN
        ALTER TABLE destinations ADD COLUMN website VARCHAR(500);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='destinations' AND column_name='amenities') THEN
        ALTER TABLE destinations ADD COLUMN amenities JSONB;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='destinations' AND column_name='accessibility') THEN
        ALTER TABLE destinations ADD COLUMN accessibility JSONB;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='destinations' AND column_name='rating') THEN
        ALTER TABLE destinations ADD COLUMN rating DECIMAL(2,1) DEFAULT 0.0;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='destinations' AND column_name='review_count') THEN
        ALTER TABLE destinations ADD COLUMN review_count INTEGER DEFAULT 0;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='destinations' AND column_name='view_count') THEN
        ALTER TABLE destinations ADD COLUMN view_count INTEGER DEFAULT 0;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='destinations' AND column_name='is_featured') THEN
        ALTER TABLE destinations ADD COLUMN is_featured BOOLEAN DEFAULT false;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='destinations' AND column_name='is_active') THEN
        ALTER TABLE destinations ADD COLUMN is_active BOOLEAN DEFAULT true;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='destinations' AND column_name='updated_at') THEN
        ALTER TABLE destinations ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='destinations' AND column_name='deleted_at') THEN
        ALTER TABLE destinations ADD COLUMN deleted_at TIMESTAMP;
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_destinations_category') THEN
        ALTER TABLE destinations ADD CONSTRAINT fk_destinations_category 
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT;
    END IF;
END $$;

CREATE UNIQUE INDEX IF NOT EXISTS idx_dest_slug ON destinations(slug);
CREATE INDEX IF NOT EXISTS idx_dest_category ON destinations(category_id);
CREATE INDEX IF NOT EXISTS idx_dest_rating ON destinations(rating);
CREATE INDEX IF NOT EXISTS idx_dest_featured ON destinations(is_featured);
CREATE INDEX IF NOT EXISTS idx_dest_province_category ON destinations(province, category_id);

-- 4. CREATE DESTINATION_IMAGES TABLE
CREATE TABLE IF NOT EXISTS destination_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    destination_id UUID NOT NULL REFERENCES destinations(id) ON DELETE CASCADE,
    url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500) NOT NULL,
    caption VARCHAR(200),
    is_main BOOLEAN DEFAULT false,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dest_img_destination ON destination_images(destination_id);
CREATE INDEX IF NOT EXISTS idx_dest_img_main ON destination_images(destination_id, is_main);

-- 5. CREATE REVIEWS TABLE
CREATE TABLE IF NOT EXISTS reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    destination_id UUID NOT NULL REFERENCES destinations(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT NOT NULL,
    helpful_count INTEGER DEFAULT 0,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    UNIQUE(user_id, destination_id)
);

CREATE INDEX IF NOT EXISTS idx_reviews_user ON reviews(user_id);
CREATE INDEX IF NOT EXISTS idx_reviews_destination ON reviews(destination_id);
CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating);
CREATE INDEX IF NOT EXISTS idx_reviews_created ON reviews(created_at);

-- 6. CREATE REVIEW_IMAGES TABLE
CREATE TABLE IF NOT EXISTS review_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500) NOT NULL,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_review_img_review ON review_images(review_id);

-- 7. CREATE REVIEW_HELPFUL TABLE
CREATE TABLE IF NOT EXISTS review_helpful (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(review_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_helpful_review ON review_helpful(review_id);
CREATE INDEX IF NOT EXISTS idx_helpful_user ON review_helpful(user_id);

-- 8. CREATE FAVORITES TABLE
CREATE TABLE IF NOT EXISTS favorites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    destination_id UUID NOT NULL REFERENCES destinations(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, destination_id)
);

CREATE INDEX IF NOT EXISTS idx_fav_user ON favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_fav_destination ON favorites(destination_id);
CREATE INDEX IF NOT EXISTS idx_fav_created ON favorites(created_at);

-- 9. CREATE TRIPS TABLE
CREATE TABLE IF NOT EXISTS trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL CHECK (end_date >= start_date),
    notes TEXT,
    status VARCHAR(20) DEFAULT 'upcoming',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_trips_user ON trips(user_id);
CREATE INDEX IF NOT EXISTS idx_trips_status ON trips(status);
CREATE INDEX IF NOT EXISTS idx_trips_dates ON trips(start_date, end_date);

-- 10. CREATE TRIP_DESTINATIONS TABLE
CREATE TABLE IF NOT EXISTS trip_destinations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    destination_id UUID NOT NULL REFERENCES destinations(id) ON DELETE CASCADE,
    display_order INTEGER DEFAULT 0,
    visit_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(trip_id, destination_id)
);

CREATE INDEX IF NOT EXISTS idx_trip_dest_trip ON trip_destinations(trip_id);
CREATE INDEX IF NOT EXISTS idx_trip_dest_destination ON trip_destinations(destination_id);

-- 11. CREATE USER_PREFERENCES TABLE
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    language VARCHAR(5) DEFAULT 'pt',
    notifications_enabled BOOLEAN DEFAULT true,
    email_notifications BOOLEAN DEFAULT true,
    push_notifications BOOLEAN DEFAULT true,
    favorite_categories JSONB,
    theme VARCHAR(10) DEFAULT 'light',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_pref_user ON user_preferences(user_id);

-- 12. CREATE PASSWORD_RESETS TABLE
CREATE TABLE IF NOT EXISTS password_resets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    token VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pwd_reset_email ON password_resets(email);
CREATE INDEX IF NOT EXISTS idx_pwd_reset_token ON password_resets(token);
CREATE INDEX IF NOT EXISTS idx_pwd_reset_expires ON password_resets(expires_at);

-- 13. INSERT INITIAL CATEGORIES (if not exists)
INSERT INTO categories (name, slug, description, icon, color, display_order)
SELECT 'Natural', 'natural', 'Praias, montanhas, parques e natureza', 'leaf', '#10B981', 1
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE slug = 'natural');

INSERT INTO categories (name, slug, description, icon, color, display_order)
SELECT 'Cultural', 'cultural', 'Museus, galerias, centros culturais', 'palette', '#8B5CF6', 2
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE slug = 'cultural');

INSERT INTO categories (name, slug, description, icon, color, display_order)
SELECT 'Histórico', 'historical', 'Monumentos, fortalezas, sítios históricos', 'book', '#F59E0B', 3
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE slug = 'historical');

INSERT INTO categories (name, slug, description, icon, color, display_order)
SELECT 'Aventura', 'adventure', 'Esportes radicais, trilhas, atividades', 'rocket', '#EF4444', 4
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE slug = 'adventure');

-- Update alembic version
UPDATE alembic_version SET version_num = '0a749f63da11';
"""

def run_migration():
    # Carregar variáveis de ambiente do arquivo .env exatamente como check-tables.py
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"📄 Carregando variáveis de ambiente de {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL não encontrada no .env")
        return False
    
    print("🚀 Executando Migration SQL Diretamente")
    print("=" * 60)
    
    try:
        import psycopg
        
        print("✅ Conectando ao banco de dados...")
        conn = psycopg.connect(database_url, connect_timeout=10)
        
        print("✅ Conectado!")
        print("⏳ Executando SQL migration...")
        
        with conn.cursor() as cur:
            # Execute migration
            cur.execute(SQL_MIGRATION)
            conn.commit()
        
        print("✅ Migration executada com sucesso!")
        
        # Verify tables
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = cur.fetchall()
            
            print(f"\n📊 Total de tabelas: {len(tables)}")
            print("\n📋 Tabelas criadas:")
            for table in tables:
                print(f"  ✓ {table[0]}")
            
            # Check categories
            cur.execute("SELECT name, slug FROM categories ORDER BY display_order")
            categories = cur.fetchall()
            
            print(f"\n🏷️  Categorias inseridas ({len(categories)}):")
            for cat in categories:
                print(f"  ✓ {cat[0]} ({cat[1]})")
        
        conn.close()
        print("\n🎉 Todas as tabelas foram criadas com sucesso!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
