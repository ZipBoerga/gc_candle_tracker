import json
from datetime import datetime, timedelta
import random

from airflow.decorators import dag, task
from airflow.utils.helpers import chain

from confluent_kafka import DeserializingConsumer


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
        new_candles = []
        updated_prices = []

        for change in changes:
            before = change.get('payload').get('before')
            after = change.get('payload').get('after')


    read_from_kafka_task = read_changes()
    test_output2_task = process_changes()

    chain(read_from_kafka_task, test_output2_task)


process_data_changes_dag = process_data_changes()
