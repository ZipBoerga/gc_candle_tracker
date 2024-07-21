import logging
from datetime import datetime

from airflow.decorators import dag, task

logging.basicConfig(level=logging.INFO,  # Set the logging level
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dag(
    dag_id='test_dag',
    schedule=None,
    start_date=datetime(2023, 7, 19),
    is_paused_upon_creation=False,
)
def test_dag():
    @task
    def test(**kwargs):
        logger.info('Test test test dag')


t_dag = test_dag()
