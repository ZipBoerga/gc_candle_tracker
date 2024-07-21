import logging
from datetime import datetime

from airflow.decorators import dag, task


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


process_data_change_dag = process_data_change()
