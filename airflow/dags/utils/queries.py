latest_candle_entry_query = '''
    SELECT entry_date
    FROM candles.price_history
    WHERE candle_id = %s
    ORDER BY entry_date DESC
    LIMIT 1
'''

history_insert_query = '''
    INSERT INTO candles.price_history (id, candle_id, url, name, picture_url, ingredients, price)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
'''

curr_price_update_query = '''
    UPDATE candles.current_prices
    SET price = %s
    WHERE candle_id = %s;
'''

curr_price_insert_query = '''
    INSERT INTO candles.current_prices (candle_id, price) VALUES (%s, %s);
'''

curr_price_select_query = '''
    SELECT candle_id, price 
    FROM candles.current_prices 
    WHERE candle_id = %s;
'''

history_select_query = '''
    SELECT candle_id, name, url, picture_url, price 
    FROM candles.price_history
    WHERE candle_id = %s
    ORDER BY entry_date DESC;
'''

report_insert_query = '''
    INSERT INTO candles.changes_reports (datetime, report) VALUES (%s, %s);
'''

last_report_select_query = '''
    SELECT datetime, report FROM candles.changes_reports 
    ORDER BY datetime DESC
    LIMIT 1;
'''

users_select_query = '''
    SELECT user_id, chat_id FROM t_users.users;
'''
