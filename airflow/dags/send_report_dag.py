import logging
import os

from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.http.hooks.http import HttpHook
from airflow.operators.empty import EmptyOperator
from airflow.utils.helpers import chain

import utils.queries as queries

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@dag(
    dag_id='send_report',
    schedule_interval=None,
    is_paused_upon_creation=True,
    catchup=False
)
def send_report():
    @task()
    def get_report_from_db():
        pg_hook = PostgresHook(
            postgres_conn_id='tracker_db'
        )
        conn = pg_hook.get_conn()
        cursor = conn.cursor()

        try:
            cursor.execute(queries.last_report_select)
            result = cursor.fetchone()
            return result[1]
        except Exception as e:
            logger.error(e)

    @task()
    def send_to_bot(report):
        pg_hook = PostgresHook(
            postgres_conn_id='tracker_db'
        )
        conn = pg_hook.get_conn()
        cursor = conn.cursor()

        try:
            cursor.execute(queries.users_select)
            result = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            raise e

        http_hook = HttpHook(http_conn_id='bot_api', method='GET')
        endpoint = f'/bot{os.environ["TELEGRAM_BOT_TOKEN"]}/sendMessage'

        for user in result:
            params = {
                'chat_id': user[1],
                'text': 'Stub for the messages!'
            }
            response = http_hook.run(endpoint=endpoint, data=params)

            if response.status_code != 200:
                logger.error(response.text())

    get_report_from_db_task = get_report_from_db()
    # stub_task = EmptyOperator(task_id='send_to_bot')
    send_to_bot_task = send_to_bot(get_report_from_db_task)

    chain(get_report_from_db_task, send_to_bot_task)


send_report_dag = send_report()
