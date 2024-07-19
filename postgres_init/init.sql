CREATE TABLE IF NOT EXISTS price_history (
    id VARCHAR(50) PRIMARY KEY,
    candle_id VARCHAR(100) NOT NULL,
    url VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    picture_url VARCHAR(255),
    ingredients VARCHAR[],
    price REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS current_prices (
    candle_id VARCHAR(100) PRIMARY KEY,
    price REAL NOT NULL
);