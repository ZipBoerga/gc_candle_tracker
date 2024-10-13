from airflow.providers.postgres.hooks.postgres import PostgresHook
import utils.queries as queries


def write_price_updates_to_db(update: list[dict]):
    pg_hook = PostgresHook(
        postgres_conn_id='tracker_db'
    )
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    try:
        for update in update:
            # Write a new candle to db
            cursor.execute(queries.candle_select, (update['candle_id'],))
            if cursor.fetchone() is None:
                cursor.execute(queries.candle_insert,
                               (
                                   update['candle_id'],
                                   update['url'],
                                   update['name'],
                                   update['picture_url'],
                                   update['ingredients'],
                               ))

            # write price update
            update_id = f"{update['candle_id']}_{update['processing_date']}"
            cursor.execute(
                queries.history_insert,
                (
                    update_id,
                    update['candle_id'],
                    update['price'],
                ),
            )
            cursor.execute(queries.curr_price_select, (update['candle_id'],))
            price = cursor.fetchall()
            if len(price) == 0:
                cursor.execute(queries.curr_price_insert, (update['candle_id'], update['price']))
            else:
                cursor.execute(queries.curr_price_update, (update['price'], update['candle_id']))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
