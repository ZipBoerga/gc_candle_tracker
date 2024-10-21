import logging
import os
import re

from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.http.hooks.http import HttpHook
from airflow.utils.helpers import chain

import utils.queries as queries
import utils.form_report_messages as report_utils

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
            cursor.execute(queries.users_with_sub_select)
            result = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            raise e

        http_hook = HttpHook(http_conn_id='bot_api', method='GET')
        endpoint = f'/bot{os.environ["TELEGRAM_BOT_TOKEN"]}/sendMessage'

        for message in report_utils.get_report_messages(report):
            if message is None:
                continue

            for user in result:
                new_params = {
                    'chat_id': user[1],
                    'text': message,
                    'parse_mode': 'HTML'
                }
                response = http_hook.run(endpoint=endpoint, data=new_params)
                if response.status_code != 200:
                    logger.error(response.text())

    get_report_from_db_task = get_report_from_db()
    send_to_bot_task = send_to_bot(get_report_from_db_task)

    chain(get_report_from_db_task, send_to_bot_task)


send_report_dag = send_report()
