import logging
from datetime import datetime

from airflow.decorators import dag, task
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

logging.basicConfig(level=logging.INFO,  # Set the logging level
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dag(
    dag_id='process_data_change_dag',
    schedule=None,
    start_date=datetime(2023, 7, 19),
    is_paused_upon_creation=False,
)
def process_data_change():
    @task
    def process_message(**kwargs):
        message = kwargs['dag_run'].conf['message']
        logger.info(message)

    t2 = TriggerDagRunOperator(
        task_id='trigger_test_dag',
        trigger_dag_id='test_dag',
    )

    process_message_dag = process_message()

    process_message_dag >> t2


process_data_change_dag = process_data_change()
