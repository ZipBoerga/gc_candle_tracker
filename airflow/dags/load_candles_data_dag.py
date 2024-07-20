from datetime import datetime
from typing import Optional

import psycopg2
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

import utils.scrapping as scrap
import utils.queries as queries


@dag(schedule='0 13 * * *', start_date=datetime(2023, 7, 19), catchup=False)
def load_candles_data():
    @task()
    def get_urls() -> list[str]:
        urls = scrap.get_candle_urls()
        return urls

    @task()
    def get_candles_data(urls: list[str]) -> list[dict]:
        candles: list[dict] = []
        for i, url in enumerate(urls):
            if (i + 1) % 10 == 0 and i != 0:
                print(f'Fetched {i + 1} urls from {len(urls)}')
            candles.append(scrap.get_candle_details(url))
        return candles

    # TODO avoiding unique_key violation
    @task
    def write_to_db(candles: list[dict]) -> None:
        pg_hook = PostgresHook(
            postgres_conn_id='postgres_db'
        )
        conn = pg_hook.get_conn()
        cursor = conn.cursor()

        for candle in candles:
            id_ = f"{candle['candle_id']}_{candle['processing_date']}"
            cursor.execute(
                queries.history_query,
                (
                    id_,
                    candle['candle_id'],
                    candle['url'],
                    candle['name'],
                    candle['picture_url'],
                    candle['ingredients'],
                    candle['price'],
                ),
            )
            cursor.execute(queries.curr_price_select_query, (candle['candle_id'],))
            price = cursor.fetchall()
            if len(price) == 0:
                cursor.execute(queries.curr_price_insert_query, (candle['candle_id'], candle['price']))
            else:
                cursor.execute(queries.curr_price_update_query, (candle['price'], candle['candle_id']))
            conn.commit()

    get_urls_task = get_urls()
    get_candles_data_task = get_candles_data(get_urls_task)
    write_to_db_task = write_to_db(get_candles_data_task)

    get_urls_task >> get_candles_data_task >> write_to_db_task


load_candles_data_dag = load_candles_data()
