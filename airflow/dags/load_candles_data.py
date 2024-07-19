from datetime import datetime

import psycopg2
from airflow.decorators import dag, task

import scrapping as scrap


@dag(schedule='0 13 * * *', start_date=datetime(2023, 7, 19), catchup=True)
def load_candles_data() -> list[str]:
    @task()
    def get_urls():
        urls = scrap.get_candle_urls()
        return urls

    @task()
    def get_candles_data(urls: list[str]) -> list[dict]:
        candles: list[dict] = []
        for url in urls:
            candles.append(scrap.get_candle_details(url))
        return candles

    @task
    def write_to_db(candles: list[dict]) -> None:
        conn = psycopg2.connect(
            {
                'dbname': 'candles',
                'user': 'admin',
                'password': 'admin',
                'host': 'postgres',
                'port': '5432',
            }
        )
        cursor = conn.cursor()

        query = '''
            INSERT INTO candle_updates (id, candle_id, url, name, picture_url, ingredients, price)
            VALUES (%s, %s, %s, %s, %s, %s);
        '''

        for candle in candles:
            id_ = f"{candle['candle_id']}_{candle['processing_timestamp']}"
            cursor.execute(
                query,
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
        conn.commit()

    get_urls_task = get_urls()
    get_candles_data_task = get_candles_data(get_urls_task)
    write_to_db_task = write_to_db(get_candles_data_task)

    get_urls_task >> get_candles_data_task >> write_to_db_task

load_candles_data_dag = load_candles_data()
