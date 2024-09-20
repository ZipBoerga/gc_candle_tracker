ALTER SCHEMA public RENAME TO candles;
CREATE SCHEMA t_users;

CREATE TABLE IF NOT EXISTS candles.price_history (
    id VARCHAR(50) PRIMARY KEY,
    candle_id VARCHAR(100) NOT NULL,
    url VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    picture_url VARCHAR(255),
    ingredients VARCHAR[],
    price REAL NOT NULL,
    entry_date DATE DEFAULT CURRENT_DATE
);



CREATE TABLE IF NOT EXISTS candles.current_prices (
    candle_id VARCHAR(100) PRIMARY KEY,
    price REAL NOT NULL,
    date_updated DATE DEFAULT CURRENT_DATE
);

ALTER TABLE candles.current_prices REPLICA IDENTITY FULL;

CREATE OR REPLACE FUNCTION candles.update_date()
RETURNS TRIGGER AS $$
BEGIN
    NEW.date_updated = CURRENT_DATE;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_date_trigger
BEFORE UPDATE ON candles.current_prices
FOR EACH ROW
EXECUTE FUNCTION candles.update_date();

CREATE TABLE IF NOT EXISTS t_users.users (
    user_id INTEGER PRIMARY KEY,
    chat_id INTEGER NOT NULL
);


--SET search_path TO t_users, candles;
