-- StreamPulse Database Schema
-- Tables for storing news, predictions, and actual outcomes for ML training

-- Enhanced Articles Table (already exists, but documenting schema)
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    headline VARCHAR NOT NULL,
    url VARCHAR NOT NULL,
    source VARCHAR NOT NULL,
    published_at TIMESTAMP WITHOUT TIME ZONE,
    event_type VARCHAR,
    sentiment_label VARCHAR,
    sentiment_score DOUBLE PRECISION,
    sentiment_raw_score DOUBLE PRECISION,
    severity VARCHAR,
    keywords_extracted TEXT[],
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add symbol tracking to articles (new column)
ALTER TABLE articles ADD COLUMN IF NOT EXISTS symbol VARCHAR(20);
ALTER TABLE articles ADD COLUMN IF NOT EXISTS price_at_publish DOUBLE PRECISION;

CREATE INDEX IF NOT EXISTS idx_articles_symbol ON articles(symbol);
CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at);
CREATE INDEX IF NOT EXISTS idx_articles_event_type ON articles(event_type);

-- Stock Price Movements Table - Track actual outcomes
CREATE TABLE IF NOT EXISTS stock_movements (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id),
    symbol VARCHAR(20) NOT NULL,
    price_at_event DOUBLE PRECISION NOT NULL,
    price_after_1d DOUBLE PRECISION,
    price_after_3d DOUBLE PRECISION,
    price_after_7d DOUBLE PRECISION,
    change_1d_pct DOUBLE PRECISION,
    change_3d_pct DOUBLE PRECISION,
    change_7d_pct DOUBLE PRECISION,
    volume_at_event BIGINT,
    volume_avg_30d BIGINT,
    nifty_change_1d DOUBLE PRECISION,
    nifty_change_3d DOUBLE PRECISION,
    event_timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    tracked_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stock_movements_article ON stock_movements(article_id);
CREATE INDEX IF NOT EXISTS idx_stock_movements_symbol ON stock_movements(symbol);
CREATE INDEX IF NOT EXISTS idx_stock_movements_event_time ON stock_movements(event_timestamp);

-- Prediction History Table - Track what we predicted vs actual
CREATE TABLE IF NOT EXISTS prediction_history (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id),
    symbol VARCHAR(20) NOT NULL,
    headline TEXT NOT NULL,
    event_type VARCHAR NOT NULL,
    sentiment_label VARCHAR NOT NULL,
    sentiment_score DOUBLE PRECISION,
    severity VARCHAR,
    
    -- Predicted values
    predicted_direction VARCHAR(10) NOT NULL, -- UP/DOWN
    predicted_change_pct DOUBLE PRECISION NOT NULL,
    predicted_probability INTEGER NOT NULL,
    predicted_range_low DOUBLE PRECISION,
    predicted_range_high DOUBLE PRECISION,
    
    -- Model breakdown
    lightgbm_prediction DOUBLE PRECISION,
    garch_prediction DOUBLE PRECISION,
    prophet_prediction DOUBLE PRECISION,
    qdrant_prediction DOUBLE PRECISION,
    
    -- Actual outcome (filled later)
    actual_change_1d DOUBLE PRECISION,
    actual_change_3d DOUBLE PRECISION,
    actual_change_7d DOUBLE PRECISION,
    actual_direction VARCHAR(10),
    
    -- Accuracy metrics
    prediction_error_1d DOUBLE PRECISION,
    prediction_error_3d DOUBLE PRECISION,
    prediction_error_7d DOUBLE PRECISION,
    direction_correct BOOLEAN,
    
    -- Metadata
    price_at_prediction DOUBLE PRECISION,
    predicted_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    outcome_updated_at TIMESTAMP WITHOUT TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_prediction_history_article ON prediction_history(article_id);
CREATE INDEX IF NOT EXISTS idx_prediction_history_symbol ON prediction_history(symbol);
CREATE INDEX IF NOT EXISTS idx_prediction_history_predicted_at ON prediction_history(predicted_at);

-- Model Training Log - Track model performance over time
CREATE TABLE IF NOT EXISTS model_training_log (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(50) NOT NULL, -- lightgbm, garch, prophet, qdrant
    version VARCHAR(20) NOT NULL,
    training_samples INTEGER NOT NULL,
    test_samples INTEGER,
    
    -- Performance metrics
    mae DOUBLE PRECISION,
    rmse DOUBLE PRECISION,
    r2_score DOUBLE PRECISION,
    accuracy DOUBLE PRECISION,
    
    -- Training config
    hyperparameters JSONB,
    feature_importance JSONB,
    
    -- Metadata
    trained_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    training_duration_seconds INTEGER,
    model_path VARCHAR(255),
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_model_training_model ON model_training_log(model_name);
CREATE INDEX IF NOT EXISTS idx_model_training_trained_at ON model_training_log(trained_at);

-- Historical Scrape Log (already exists, documenting)
CREATE TABLE IF NOT EXISTS historical_scrape_log (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    date_from DATE NOT NULL,
    date_to DATE NOT NULL,
    articles_found INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITHOUT TIME ZONE
);

-- Trending News (already exists)
CREATE TABLE IF NOT EXISTS trending_news (
    id VARCHAR PRIMARY KEY,
    title VARCHAR NOT NULL,
    link VARCHAR NOT NULL,
    source VARCHAR NOT NULL,
    fetched_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Function to update last_updated timestamp
CREATE OR REPLACE FUNCTION update_last_updated_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for stock_movements
DROP TRIGGER IF EXISTS update_stock_movements_last_updated ON stock_movements;
CREATE TRIGGER update_stock_movements_last_updated
    BEFORE UPDATE ON stock_movements
    FOR EACH ROW
    EXECUTE FUNCTION update_last_updated_column();
