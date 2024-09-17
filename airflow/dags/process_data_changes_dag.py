import json
from datetime import datetime, timedelta
import random

from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.helpers import chain

from confluent_kafka import DeserializingConsumer
import utils.queries as queries


def deserializer(data, context):
    if data is None:
        return None
    return json.loads(data.decode('utf-8'))


config = {
    'bootstrap.servers': 'broker:29092',
    'group.id': str(random.random()),
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
    'session.timeout.ms': 6000,
    'key.deserializer': None,
    'value.deserializer': deserializer
}


@dag(
    dag_id='process_data_changes',
    schedule='@once',
    start_date=datetime(2023, 7, 19),
    is_paused_upon_creation=True,
    catchup=False
)
def process_data_changes():
    @task()
    def read_changes():
        changes = []
        consumer = DeserializingConsumer(config)
        consumer.subscribe(['candles.public.current_prices'])
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
                consumer.commit()
        return changes

    @task()
    def process_changes(changes: list[dict]):
        new_candles: list[dict] = []
        lowered_prices: list[dict] = []
        raised_prices: list[dict] = []

        pg_hook = PostgresHook(
            postgres_conn_id='candles_db'
        )
        conn = pg_hook.get_conn()
        cursor = conn.cursor()

        for change in changes:
            before = change.get('payload').get('before')
            after = change.get('payload').get('after')

            cursor.execute(queries.history_select_query, (after.get('candle_id')))
            if before is None:
                candle_data = cursor.fetchone()
                new_candles.append(candle_data)
            else:
                candle_data = cursor.fetch()[:-1]
                candle_data = {
                    'candle_id': candle_data['candle_id'],
                    'name': candle_data['name'],
                    'url': candle_data['url'],
                    'picture_url': candle_data['picture_url'],
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


    read_from_kafka_task = read_changes()
    process_changes_task = process_changes(read_from_kafka_task)

    chain(read_from_kafka_task, process_changes_task)


process_data_changes_dag = process_data_changes()
