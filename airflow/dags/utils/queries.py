candle_select = '''
    SELECT candle_id, name, url, picture_url, ingredients
    FROM candles.candles
    WHERE candle_id = %s
    LIMIT 1;
'''

candle_insert = '''
    INSERT INTO candles.candles (candle_id, url, name, picture_url, ingredients) VALUES (%s, %s, %s, %s, %s); 
'''

history_insert = '''
    INSERT INTO candles.price_history (id, candle_id, price)
    VALUES (%s, %s, %s);
'''

curr_price_update = '''
    UPDATE candles.current_prices
    SET price = %s
    WHERE candle_id = %s;
'''

curr_price_insert = '''
    INSERT INTO candles.current_prices (candle_id, price) VALUES (%s, %s);
'''

curr_price_select = '''
    SELECT candle_id, price 
    FROM candles.current_prices 
    WHERE candle_id = %s;
'''

history_select = '''
    SELECT candle_id, price 
    FROM candles.price_history
    WHERE candle_id = %s
    ORDER BY entry_date DESC;
'''

report_insert = '''
    INSERT INTO candles.changes_reports (datetime, report) VALUES (%s, %s);
'''

last_report_select = '''
    SELECT datetime, report FROM candles.changes_reports 
    ORDER BY datetime DESC
    LIMIT 1;
'''

users_select = '''
    SELECT user_id, chat_id FROM t_users.users;
'''
