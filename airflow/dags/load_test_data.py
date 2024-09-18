from datetime import datetime

from airflow.decorators import dag, task
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.helpers import chain

from utils.store_candles_data import write_price_updates_to_db
from utils.fetch_test_data import fetch_test_data


@dag(
    dag_id='load_test_data',
    schedule='0 13 * * *',
    start_date=datetime(2023, 7, 19),
    is_paused_upon_creation=True,
    catchup=False
)
def load_test_data():
    @task()
    def get_test_data(**kwargs):
        data_url = kwargs['dag_run'].conf.get('test_data_url')
        test_data: list[dict] = fetch_test_data(data_url)
        return test_data

    @task()
    def write_to_db(candles: list[dict]) -> None:
        write_price_updates_to_db(candles)

    get_test_data_task = get_test_data()
    write_to_db_task = write_to_db(get_test_data_task)
    trigger_processing = TriggerDagRunOperator(
        task_id='trigger_data_processing',
        trigger_dag_id='process_data_changes'
    )

    chain(get_test_data_task, write_to_db_task, trigger_processing)


load_test_data_dag = load_test_data()
