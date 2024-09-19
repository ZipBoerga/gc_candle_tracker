from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.helpers import chain
from airflow.utils.trigger_rule import TriggerRule

import utils.scrapping as scrap
from utils.store_candles_data import write_price_updates_to_db


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

    @task(task_id="task_final", trigger_rule=TriggerRule.ALL_DONE)
    def write_to_db(candles: list[dict]) -> None:
        write_price_updates_to_db(candles)

    get_urls_task = get_urls()
    get_candles_data_task = get_candles_data(get_urls_task)
    write_to_db_task = write_to_db(get_candles_data_task)
    trigger_processing = TriggerDagRunOperator(
        task_id='trigger_data_processing',
        trigger_dag_id='process_data_changes'
    )

    chain(get_urls_task, get_candles_data_task, write_to_db_task, trigger_processing)


load_candles_data_dag = load_candles_data()
