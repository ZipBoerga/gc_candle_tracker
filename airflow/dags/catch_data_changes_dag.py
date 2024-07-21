import json
from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow_provider_kafka.operators.event_triggers_function import EventTriggersFunctionOperator


@dag(
    dag_id='catch_data_changes',
    schedule='@once',
    start_date=datetime(2023, 7, 19),
    is_paused_upon_creation=False,
    catchup=False
)
# This pattern seems to be quite controversial. It doesn't generate dag-runs of the triggered dag,
# the other dag runs are all parts of THIS dag run. Not clean!
# Suggestion: CDC in Spark, Spark calls airflow in the to send a message in a telegram or sends message itself.
# option 2: check if this propagates to the dag triggered by this triggered dag
# checked. It is bad. Will use a container with a consumer to replace it.
def catch_data_changes():
    def trigger_change_processing_dag(message, **context):
        if message:
            trigger = TriggerDagRunOperator(
                task_id='trigger_process_data_change_dag',
                trigger_dag_id='process_data_change_dag',
                conf={'message': message}
            )
            trigger.execute(context)

    read_from_kafka = EventTriggersFunctionOperator(
        task_id='consume_price_changes',
        topics=['candles.public.current_prices'],
        apply_function='utils.await_function.await_function',
        kafka_config={
            'bootstrap.servers': 'broker:29092',
            'group.id': 'price_cdc',
            # Change to true after
            'enable.auto.commit': False,
            "auto.offset.reset": "earliest",
        },
        event_triggered_function=trigger_change_processing_dag,
        execution_timeout=timedelta(days=2),
    )


cdc_dag = catch_data_changes()
