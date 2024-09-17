from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.helpers import chain

import utils.scrapping as scrap
import utils.queries as queries


@dag(
    dag_id='load_candles_data',
    schedule='0 13 * * *',
    start_date=datetime(2023, 7, 19),
    is_paused_upon_creation=True,
    catchup=False
)
def load_candles_data():
    @task(
        retries=3,
        retry_delay=timedelta(hours=1)
    )
    def get_urls() -> list[str]:
        urls = scrap.get_candle_urls()
        return urls

    @task(
        retries=3,
        retry_delay=timedelta(hours=1)
    )
    def get_candles_data(urls: list[str]) -> list[dict]:
        candles: list[dict] = []
        for i, url in enumerate(urls):
            if (i + 1) % 10 == 0 and i != 0:
                print(f'Fetched {i + 1} urls from {len(urls)}')
            candles.append(scrap.get_candle_details(url))
        return candles

    # what are the chances that I will not write the full batch?
    @task
    def write_to_db(candles: list[dict]) -> None:
        pg_hook = PostgresHook(
            postgres_conn_id='postgres_db'
        )
        conn = pg_hook.get_conn()
        cursor = conn.cursor()

        for candle in candles:
            # cursor.execute(queries.latest_candle_entry_query, (candle['candle_id'],))
            # previous_entry_date_row = cursor.fetchone()

            # if previous_entry_date_row is not None and previous_entry_date_row[0] == datetime.now().date():
            #     continue

            id_ = f"{candle['candle_id']}_{candle['processing_date']}"
            cursor.execute(
                queries.history_insert_query,
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
    trigger_processing = TriggerDagRunOperator(
        task_id='trigger_data_processing',
        trigger_dag_id='process_data_changes'
    )

    chain(get_urls_task, get_candles_data_task, write_to_db_task, trigger_processing)
    # chain(trigger_processing)
    # get_urls_task >> get_candles_data_task >> write_to_db_task


load_candles_data_dag = load_candles_data()
