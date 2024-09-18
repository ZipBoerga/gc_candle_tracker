from datetime import datetime

import requests
import pandas as pd


def fetch_test_data(url) -> list[dict]:
    response = requests.get(url)
    response.raise_for_status()

    df = pd.read_csv(url, delimiter=';')
    df = df.replace({pd.NA: None, float('nan'): None})
    df['ingredients'] = df['ingredients'].str.split(',')
    df['processing_date'] = int(datetime.now().timestamp())
    data = df.to_dict(orient='records')

    return data
