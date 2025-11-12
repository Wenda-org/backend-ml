# 🗄️ Database Schema - Wenda Mobile App

**Versão:** 1.0  
**Data:** 11 de Novembro de 2025  
**Database:** PostgreSQL (recomendado) ou MySQL  
**ORM Sugerido:** Prisma, TypeORM ou Sequelize

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Diagrama de Relacionamentos](#diagrama-de-relacionamentos)
3. [Tabelas](#tabelas)
4. [Índices Recomendados](#índices-recomendados)
5. [Migrations](#migrations)
6. [Considerações de Performance](#considerações-de-performance)

---

## 📊 Visão Geral

### Total de Tabelas: 12

1. `users` - Usuários do sistema
2. `destinations` - Destinos turísticos
3. `destination_images` - Imagens dos destinos
4. `categories` - Categorias de destinos
5. `reviews` - Avaliações dos usuários
6. `review_images` - Imagens das avaliações
7. `review_helpful` - Marcações de "útil" em reviews
8. `favorites` - Destinos favoritos dos usuários
9. `trips` - Viagens planejadas
10. `trip_destinations` - Destinos em cada viagem
11. `user_preferences` - Preferências dos usuários
12. `password_resets` - Tokens de reset de senha

---

## 🔗 Diagrama de Relacionamentos

```
users (1) ──────── (N) reviews ──────── (N) review_images
  │                    │
  │                    └──────── (N) review_helpful
  │
  ├────────── (N) favorites
  │
  ├────────── (N) trips ──────── (N) trip_destinations
  │
  └────────── (1) user_preferences

destinations (1) ──────── (N) destination_images
     │
     ├──────── (N) reviews
     │
     ├──────── (N) favorites
     │
     ├──────── (N) trip_destinations
     │
     └──────── (N) categories (N)
```

---

## 📁 Tabelas

### 1. users

**Objetivo:** Armazenar informações dos usuários do aplicativo.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    avatar_url VARCHAR(500),
    phone VARCHAR(20),
    bio TEXT,
    email_verified_at TIMESTAMP,
    google_id VARCHAR(255) UNIQUE,
    apple_id VARCHAR(255) UNIQUE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    
    INDEX idx_email (email),
    INDEX idx_google_id (google_id),
    INDEX idx_created_at (created_at)
);
```

**Campos:**
- `id`: Identificador único (UUID)
- `name`: Nome completo do usuário
- `email`: Email único para login
- `password_hash`: Senha criptografada (bcrypt)
- `avatar_url`: URL da foto de perfil
- `phone`: Telefone (opcional)
- `bio`: Biografia do usuário (max 500 chars)
- `email_verified_at`: Data/hora de verificação do email
- `google_id`: ID do Google OAuth (se aplicável)
- `apple_id`: ID do Apple Sign In (se aplicável)
- `is_active`: Status da conta
- `deleted_at`: Soft delete (null = ativo)

---

### 2. categories

**Objetivo:** Categorias de destinos turísticos.

```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    slug VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50),
    color VARCHAR(7),
    is_active BOOLEAN DEFAULT true,
    display_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_slug (slug),
    INDEX idx_display_order (display_order)
);
```

**Dados Iniciais (Seed):**
```sql
INSERT INTO categories (name, slug, description, icon, color, display_order) VALUES
('Natural', 'natural', 'Praias, montanhas, parques e natureza', 'leaf', '#10B981', 1),
('Cultural', 'cultural', 'Museus, galerias, centros culturais', 'business', '#8B5CF6', 2),
('Histórico', 'historical', 'Monumentos, fortalezas, sítios históricos', 'library', '#F59E0B', 3),
('Aventura', 'adventure', 'Esportes radicais, trilhas, atividades', 'bicycle', '#EF4444', 4);
```

---

### 3. destinations

**Objetivo:** Destinos turísticos de Angola.

```sql
CREATE TABLE destinations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    long_description TEXT,
    location VARCHAR(100) NOT NULL,
    province VARCHAR(50) NOT NULL,
    address TEXT,
    category_id UUID NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    opening_hours VARCHAR(200),
    ticket_price VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(500),
    amenities JSON,
    accessibility JSON,
    rating DECIMAL(2, 1) DEFAULT 0.0,
    review_count INT DEFAULT 0,
    view_count INT DEFAULT 0,
    is_featured BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
    
    INDEX idx_slug (slug),
    INDEX idx_category (category_id),
    INDEX idx_location (province, location),
    INDEX idx_coordinates (latitude, longitude),
    INDEX idx_rating (rating),
    INDEX idx_featured (is_featured),
    FULLTEXT INDEX idx_search (name, description, location)
);
```

**Campos JSON:**
- `amenities`: `["parking", "wifi", "restaurant", "guide", "wheelchair"]`
- `accessibility`: `["wheelchair", "elevator", "audio_guide", "sign_language"]`

---

### 4. destination_images

**Objetivo:** Galeria de imagens dos destinos.

```sql
CREATE TABLE destination_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    destination_id UUID NOT NULL,
    url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500) NOT NULL,
    caption VARCHAR(200),
    is_main BOOLEAN DEFAULT false,
    display_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE,
    
    INDEX idx_destination (destination_id),
    INDEX idx_main (destination_id, is_main),
    INDEX idx_order (destination_id, display_order)
);
```

**Regra de Negócio:** Cada destino deve ter pelo menos 1 imagem com `is_main = true`.

---

### 5. reviews

**Objetivo:** Avaliações dos usuários sobre destinos.

```sql
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    destination_id UUID NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT NOT NULL,
    helpful_count INT DEFAULT 0,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_user_destination (user_id, destination_id),
    INDEX idx_destination (destination_id),
    INDEX idx_user (user_id),
    INDEX idx_rating (rating),
    INDEX idx_created (created_at)
);
```

**Constraint:** Um usuário só pode avaliar um destino uma vez (UNIQUE).

**Trigger:** Atualizar `rating` e `review_count` em `destinations` após INSERT/UPDATE/DELETE.

---

### 6. review_images

**Objetivo:** Imagens anexadas às avaliações.

```sql
CREATE TABLE review_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID NOT NULL,
    url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500) NOT NULL,
    display_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE,
    
    INDEX idx_review (review_id)
);
```

---

### 7. review_helpful

**Objetivo:** Rastrear quais usuários marcaram reviews como úteis.

```sql
CREATE TABLE review_helpful (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID NOT NULL,
    user_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_review_user (review_id, user_id),
    INDEX idx_review (review_id),
    INDEX idx_user (user_id)
);
```

**Trigger:** Atualizar `helpful_count` em `reviews` após INSERT/DELETE.

---

### 8. favorites

**Objetivo:** Destinos favoritos dos usuários.

```sql
CREATE TABLE favorites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    destination_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_user_destination (user_id, destination_id),
    INDEX idx_user (user_id),
    INDEX idx_destination (destination_id),
    INDEX idx_created (created_at)
);
```

---

### 9. trips

**Objetivo:** Viagens planejadas pelos usuários.

```sql
CREATE TABLE trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    name VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    notes TEXT,
    status ENUM('upcoming', 'ongoing', 'completed', 'cancelled') DEFAULT 'upcoming',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    CHECK (end_date >= start_date),
    
    INDEX idx_user (user_id),
    INDEX idx_status (status),
    INDEX idx_dates (start_date, end_date),
    INDEX idx_created (created_at)
);
```

---

### 10. trip_destinations

**Objetivo:** Destinos incluídos em cada viagem (itinerário).

```sql
CREATE TABLE trip_destinations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL,
    destination_id UUID NOT NULL,
    display_order INT NOT NULL DEFAULT 0,
    visit_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE,
    FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_trip_destination (trip_id, destination_id),
    INDEX idx_trip (trip_id),
    INDEX idx_destination (destination_id),
    INDEX idx_order (trip_id, display_order)
);
```

---

### 11. user_preferences

**Objetivo:** Preferências e configurações do usuário.

```sql
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    language VARCHAR(5) DEFAULT 'pt',
    notifications_enabled BOOLEAN DEFAULT true,
    email_notifications BOOLEAN DEFAULT true,
    push_notifications BOOLEAN DEFAULT true,
    favorite_categories JSON,
    theme VARCHAR(10) DEFAULT 'light',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    INDEX idx_user (user_id)
);
```

**Campos JSON:**
- `favorite_categories`: `["natural", "historical"]`

---

### 12. password_resets

**Objetivo:** Tokens para recuperação de senha.

```sql
CREATE TABLE password_resets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    token VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_email (email),
    INDEX idx_token (token),
    INDEX idx_expires (expires_at)
);
```

**Limpeza:** Remover tokens expirados regularmente (CRON job).

---

## 📊 Índices Recomendados

### Índices Espaciais (Para Buscas Geográficas)

```sql
-- PostgreSQL com PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;

ALTER TABLE destinations ADD COLUMN geom GEOMETRY(Point, 4326);

CREATE INDEX idx_destinations_geom ON destinations USING GIST(geom);

-- Atualizar geom quando lat/lon mudar
CREATE OR REPLACE FUNCTION update_destination_geom()
RETURNS TRIGGER AS $$
BEGIN
    NEW.geom = ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_destination_geom
BEFORE INSERT OR UPDATE ON destinations
FOR EACH ROW
EXECUTE FUNCTION update_destination_geom();
```

### Índices Compostos Importantes

```sql
-- Busca de destinos por província e categoria
CREATE INDEX idx_destinations_province_category 
ON destinations(province, category_id);

-- Busca de viagens por usuário e status
CREATE INDEX idx_trips_user_status 
ON trips(user_id, status);

-- Favoritos recentes do usuário
CREATE INDEX idx_favorites_user_created 
ON favorites(user_id, created_at DESC);

-- Reviews ordenadas por data
CREATE INDEX idx_reviews_destination_created 
ON reviews(destination_id, created_at DESC);
```

---

## 🔄 Triggers Essenciais

### 1. Atualizar Rating dos Destinos

```sql
CREATE OR REPLACE FUNCTION update_destination_rating()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE destinations
    SET 
        rating = (
            SELECT COALESCE(AVG(rating), 0)
            FROM reviews
            WHERE destination_id = COALESCE(NEW.destination_id, OLD.destination_id)
            AND deleted_at IS NULL
        ),
        review_count = (
            SELECT COUNT(*)
            FROM reviews
            WHERE destination_id = COALESCE(NEW.destination_id, OLD.destination_id)
            AND deleted_at IS NULL
        )
    WHERE id = COALESCE(NEW.destination_id, OLD.destination_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_destination_rating
AFTER INSERT OR UPDATE OR DELETE ON reviews
FOR EACH ROW
EXECUTE FUNCTION update_destination_rating();
```

### 2. Atualizar Helpful Count

```sql
CREATE OR REPLACE FUNCTION update_review_helpful_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE reviews
    SET helpful_count = (
        SELECT COUNT(*)
        FROM review_helpful
        WHERE review_id = COALESCE(NEW.review_id, OLD.review_id)
    )
    WHERE id = COALESCE(NEW.review_id, OLD.review_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_review_helpful_count
AFTER INSERT OR DELETE ON review_helpful
FOR EACH ROW
EXECUTE FUNCTION update_review_helpful_count();
```

### 3. Auto-create User Preferences

```sql
CREATE OR REPLACE FUNCTION create_user_preferences()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO user_preferences (user_id)
    VALUES (NEW.id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_create_user_preferences
AFTER INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION create_user_preferences();
```

---

## 🚀 Migrations (Ordem de Execução)

```bash
migrations/
├── 001_create_users_table.sql
├── 002_create_categories_table.sql
├── 003_create_destinations_table.sql
├── 004_create_destination_images_table.sql
├── 005_create_reviews_table.sql
├── 006_create_review_images_table.sql
├── 007_create_review_helpful_table.sql
├── 008_create_favorites_table.sql
├── 009_create_trips_table.sql
├── 010_create_trip_destinations_table.sql
├── 011_create_user_preferences_table.sql
├── 012_create_password_resets_table.sql
├── 013_create_triggers.sql
├── 014_create_spatial_indexes.sql
└── 015_seed_categories.sql
```

---

## ⚡ Considerações de Performance

### 1. Caching

**Recomendação:** Usar Redis para:
- Destinos mais populares (view_count)
- Destinos em destaque (is_featured = true)
- Categorias (raramente mudam)
- Resultado de buscas frequentes

```redis
# Exemplo de cache
SET destination:{id} {json_data} EX 3600
SET featured_destinations {json_array} EX 1800
SET categories {json_array} EX 86400
```

### 2. Particionamento

Para escalabilidade futura, considerar particionamento de:

```sql
-- Particionar reviews por ano
CREATE TABLE reviews_2025 PARTITION OF reviews
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE reviews_2026 PARTITION OF reviews
FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
```

### 3. Full-Text Search

```sql
-- PostgreSQL
CREATE INDEX idx_destinations_fts ON destinations 
USING GIN(to_tsvector('portuguese', name || ' ' || description || ' ' || location));

-- Query
SELECT * FROM destinations
WHERE to_tsvector('portuguese', name || ' ' || description || ' ' || location) 
@@ plainto_tsquery('portuguese', 'fortaleza luanda');
```

### 4. Database Views (Opcional)

```sql
-- View para destinos com estatísticas completas
CREATE VIEW destinations_with_stats AS
SELECT 
    d.*,
    COUNT(DISTINCT f.id) as favorite_count,
    COUNT(DISTINCT td.id) as trip_count,
    (SELECT url FROM destination_images 
     WHERE destination_id = d.id AND is_main = true 
     LIMIT 1) as main_image_url
FROM destinations d
LEFT JOIN favorites f ON f.destination_id = d.id
LEFT JOIN trip_destinations td ON td.destination_id = d.id
WHERE d.deleted_at IS NULL
GROUP BY d.id;
```

---

## 🔒 Segurança

### 1. Row Level Security (RLS) - PostgreSQL

```sql
-- Usuários só podem ver/editar seus próprios dados
ALTER TABLE trips ENABLE ROW LEVEL SECURITY;

CREATE POLICY trips_user_policy ON trips
FOR ALL
USING (user_id = current_setting('app.current_user_id')::uuid);
```

### 2. Validações

- Emails únicos
- Passwords hasheados (bcrypt, custo 12)
- UUIDs para IDs públicos (evita enumeration attacks)
- Soft deletes para auditoria

### 3. Backup

```bash
# Backup diário automatizado
pg_dump -U postgres -d wenda_db -F c -f backup_$(date +%Y%m%d).dump
```

---

## 📊 Estimativa de Tamanho

### Volumes Esperados (1 ano):

| Tabela | Registros | Tamanho Aprox. |
|--------|-----------|----------------|
| users | 50.000 | 15 MB |
| destinations | 1.000 | 5 MB |
| destination_images | 5.000 | 2 MB |
| reviews | 100.000 | 80 MB |
| favorites | 200.000 | 20 MB |
| trips | 30.000 | 10 MB |
| trip_destinations | 150.000 | 15 MB |
| **TOTAL** | **536.000** | **~150 MB** |

**Nota:** Tamanhos não incluem imagens (armazenar em S3/CloudStorage).

---

## ✅ Checklist de Implementação

- [ ] Criar todas as 12 tabelas na ordem correta
- [ ] Adicionar todas as foreign keys
- [ ] Criar todos os índices recomendados
- [ ] Implementar triggers de atualização
- [ ] Configurar PostGIS para buscas geográficas
- [ ] Seed inicial de categorias
- [ ] Configurar soft deletes
- [ ] Implementar RLS (se PostgreSQL)
- [ ] Configurar backup automatizado
- [ ] Testar performance de queries principais
- [ ] Documentar procedures e functions

---

**Database schema completo e otimizado para o app Wenda Mobile!** 🎉
