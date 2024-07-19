history_query = '''
    INSERT INTO price_history (id, candle_id, url, name, picture_url, ingredients, price)
    VALUES (%s, %s, %s, %s, %s, %s);
'''

curr_price_update_query = '''
    UPDATE current_prices 
    SET price = %
    WHERE candle_id = %;
'''

curr_price_insert_query = '''
    INSERT INTO current_prices (candle_id, price) VALUES (%s, %s);
'''

curr_price_select_query = '''
    SELECT candle, price FROM current_prices WHERE candle_id = %s;
'''