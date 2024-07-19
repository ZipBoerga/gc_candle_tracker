CREATE TABLE IF NOT EXISTS candle_update (
    id VARCHAR(50) PRIMARY KEY,
    candle_id VARCHAR(100) NOT NULL,
    url VARCHAR(255) NOT NULL,
    picture_url VARCHAR(255),
    ingredients VARCHAR[],
    price REAL NOT NULL
)