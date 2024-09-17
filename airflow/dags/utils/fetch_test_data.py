import csv
import requests
from io import StringIO


def fetch_test_data(url) -> list[dict]:
    response = requests.get(url)
    response.raise_for_status()

    file = StringIO(response.text)
    reader = csv.DictReader(file)
    data = [row for row in reader]
    return data
