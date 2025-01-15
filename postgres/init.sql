ALTER SCHEMA public RENAME TO candles;
CREATE SCHEMA t_users;

CREATE TABLE IF NOT EXISTS candles.candles (
    candle_id VARCHAR(100)  PRIMARY KEY,
    url VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    picture_url VARCHAR(255),
    ingredients VARCHAR[]
);


CREATE TABLE IF NOT EXISTS candles.price_history (
    id VARCHAR(50) PRIMARY KEY,
    candle_id VARCHAR(100) NOT NULL,
    price REAL NOT NULL,
    entry_date DATE DEFAULT CURRENT_DATE,
    CONSTRAINT fk_candles
        FOREIGN KEY (candle_id)
        REFERENCES candles.candles(candle_id)
        ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS candles.current_prices (
    candle_id VARCHAR(100) PRIMARY KEY,
    price REAL NOT NULL,
    price_update_date DATE DEFAULT CURRENT_DATE
);

ALTER TABLE candles.current_prices REPLICA IDENTITY FULL;

CREATE OR REPLACE FUNCTION candles.update_price()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.price != OLD.price THEN
        NEW.price_update_date = CURRENT_DATE;
        RETURN NEW;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_price_trigger
BEFORE UPDATE ON candles.current_prices
FOR EACH ROW
EXECUTE FUNCTION candles.update_price();

CREATE TABLE IF NOT EXISTS candles.changes_reports (
    datetime TIMESTAMP PRIMARY KEY,
    report JSON
);

CREATE TABLE IF NOT EXISTS t_users.users (
    user_id VARCHAR(40) PRIMARY KEY,
    chat_id VARCHAR(40) NOT NULL,
    subscribed BOOLEAN NOT NULL DEFAULT FALSE
);

ALTER ROLE admin SET search_path TO t_users, candles;

SET search_path TO t_users, candles;
