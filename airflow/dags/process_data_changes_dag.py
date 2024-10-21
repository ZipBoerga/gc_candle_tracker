import json
from datetime import datetime
import random
import logging

from airflow.decorators import dag, task
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.helpers import chain
from confluent_kafka import DeserializingConsumer
import utils.queries as queries

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def deserializer(data, context):
    if data is None:
        return None
    return json.loads(data.decode('utf-8'))


kafka_sub_config = {
    'bootstrap.servers': 'broker:29092',
    # 'group.id': str(random.random()),
    'group.id': 'stable-test-group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
    'session.timeout.ms': 6000,
    'key.deserializer': None,
    'value.deserializer': deserializer
}


@dag(
    dag_id='process_data_changes',
    schedule_interval=None,
    start_date=datetime(2023, 7, 19),
    is_paused_upon_creation=True,
    catchup=False
)
def process_data_changes():
    @task()
    def read_changes():
        changes = []
        consumer = DeserializingConsumer(kafka_sub_config)
        consumer.subscribe(['tracker_db.candles.current_prices'])
        while True:
            msg = consumer.poll(6)
            if msg is None:
                print('All messages are processed.')
                break
            if msg.error():
                print(f'Error while consuming the message: {msg.error()}')
                continue
            else:
                changes.append(msg.value())
                print(f'The message\'s type {type(msg.value().get("payload").get("before"))}')
                print(f'The message itself {msg.value().get("payload").get("before")}')
                consumer.commit()
        return changes

    @task()
    def process_changes(changes: list[dict]):
        new_candles: list[dict] = []
        lowered_prices: list[dict] = []
        raised_prices: list[dict] = []

        pg_hook = PostgresHook(
            postgres_conn_id='tracker_db'
        )
        conn = pg_hook.get_conn()
        cursor = conn.cursor()

        for change in changes:
            before = change.get('payload').get('before')
            after = change.get('payload').get('after')

            cursor.execute(queries.candle_select, (after.get('candle_id'),))
            candle_data = cursor.fetchone()

            if before is None:
                new_candles.append({
                    'candle_id': candle_data[0],
                    'name': candle_data[1],
                    'url': candle_data[2],
                    'picture_url': candle_data[3],
                    'ingredients': candle_data[4],
                    'price': after['price']
                })
            else:
                candle_data = {
                    'candle_id': candle_data[0],
                    'name': candle_data[1],
                    'url': candle_data[2],
                    'picture_url': candle_data[3],
                    'ingredients': candle_data[4],
                    'old_price': before['price'],
                    'new_price': after['price']
                }
                if float(candle_data['old_price']) > float(candle_data['new_price']):
                    lowered_prices.append(candle_data)
                else:
                    raised_prices.append(candle_data)

        return {
            'new_candles': new_candles,
            'lowered_prices': lowered_prices,
            'raised_prices': raised_prices
        }

    @task()
    def write_report_to_db(report: dict):
        pg_hook = PostgresHook(
            postgres_conn_id='tracker_db'
        )
        conn = pg_hook.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(queries.report_insert, (datetime.utcnow(), json.dumps(report)))
            conn.commit()
        except Exception as e:
            logger.error(e)

    trigger_send_report = TriggerDagRunOperator(
        task_id='trigger_send_report',
        trigger_dag_id='send_report'
    )

    read_from_kafka_task = read_changes()
    process_changes_task = process_changes(read_from_kafka_task)
    write_report_to_db_task = write_report_to_db(process_changes_task)

    chain(read_from_kafka_task, process_changes_task, write_report_to_db_task, trigger_send_report)


process_data_changes_dag = process_data_changes()
