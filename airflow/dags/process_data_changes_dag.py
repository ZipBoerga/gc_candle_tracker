import json
from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.utils.helpers import chain


@dag(
    dag_id='process_data_changes',
    schedule='@once',
    start_date=datetime(2023, 7, 19),
    is_paused_upon_creation=True,
    catchup=False
)
def process_data_changes():
    @task()
    def test_output():
        print('Hello')

    @task()
    def test_output2():
        print('Hello2')

    test_output_task = test_output()
    test_output2_task = test_output2()

    chain(test_output_task, test_output2_task)


process_data_changes_dag = process_data_changes()
