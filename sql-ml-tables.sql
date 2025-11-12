-- ============================================
-- TABELAS NECESSÁRIAS PARA O BACKEND DE ML
-- ============================================
-- Execute este SQL no seu banco de dados se preferir criar as tabelas manualmente

-- ============================================
-- 1. TOURISM STATISTICS
-- ============================================
CREATE TABLE IF NOT EXISTS tourism_statistics (
    id SERIAL PRIMARY KEY,
    province VARCHAR(100) NOT NULL,
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    domestic_visitors INTEGER,
    foreign_visitors INTEGER,
    occupancy_rate DOUBLE PRECISION,
    avg_stay_days DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tourism_stats_province_year_month 
ON tourism_statistics(province, year, month);

-- ============================================
-- 2. ML MODELS REGISTRY
-- ============================================
CREATE TABLE IF NOT EXISTS ml_models_registry (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    version VARCHAR(20) NOT NULL,
    algorithm VARCHAR(100),
    metrics JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    trained_on DATE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ml_models_name_version 
ON ml_models_registry(model_name, version);

CREATE INDEX IF NOT EXISTS idx_ml_models_status 
ON ml_models_registry(status);

-- ============================================
-- 3. ML PREDICTIONS
-- ============================================
CREATE TABLE IF NOT EXISTS ml_predictions (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(20),
    province VARCHAR(100) NOT NULL,
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    predicted_visitors INTEGER,
    confidence_interval JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ml_predictions_province_year_month 
ON ml_predictions(province, year, month);

CREATE INDEX IF NOT EXISTS idx_ml_predictions_model 
ON ml_predictions(model_name, model_version);

-- ============================================
-- 4. RECOMMENDATIONS LOG
-- ============================================
CREATE TABLE IF NOT EXISTS recommendations_log (
    id SERIAL PRIMARY KEY,
    user_id UUID,
    destination_id UUID,
    score DOUBLE PRECISION,
    model_version VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign keys (assumindo que users e destinations já existem)
    CONSTRAINT fk_recommendations_user 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_recommendations_destination 
        FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_recommendations_user 
ON recommendations_log(user_id);

CREATE INDEX IF NOT EXISTS idx_recommendations_destination 
ON recommendations_log(destination_id);

CREATE INDEX IF NOT EXISTS idx_recommendations_created 
ON recommendations_log(created_at DESC);

-- ============================================
-- VERIFICAÇÃO
-- ============================================
-- Execute esta query para verificar se todas as tabelas foram criadas:
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
  AND tablename IN (
    'tourism_statistics', 
    'ml_models_registry', 
    'ml_predictions', 
    'recommendations_log'
  )
ORDER BY tablename;

-- Resultado esperado: 4 tabelas
