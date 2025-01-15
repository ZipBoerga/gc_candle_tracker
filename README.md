## TODO
* Refine bot text answers
* Handle situations when there are too many updates
* Utilize Spark
* Refactor queries to the separate modules
* Reimagine admin access only wrapper

## RUN Commands
Debezium and DB
```commandline
 docker-compose --env-file .env --profile debezium up -d 
```

Airflow
```commandline
 docker-compose --env-file .env --profile airflow up -d 
```

Telegram bot
```commandline
 docker-compose --env-file .env --profile tg_bot up -d 
```

```commandline
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0 --repositories https://repo1.maven.org/maven2/ /opt/bitnami/spark/spark-apps/streaming_data_changes.py
```

### Dev junk
#### for creating test data
```commandline
psql -U admin -d tracker_db -c "\copy (SELECT id, candle_id, url, name, picture_url, array_to_string(ingredients, ', ') AS ingredients, price FROM candles.price_history LIMIT 10) TO 'candles1.csv' CSV HEADER DELIMITER ';'"
```
#### linkies for test data
https://raw.githubusercontent.com/ZipBoerga/gc_candle_tracker/main/testing/candles_initial.csv
https://raw.githubusercontent.com/ZipBoerga/gc_candle_tracker/testing_updates_sorting/testing/candles_modified.csv

{"test_data_url": "https://raw.githubusercontent.com/ZipBoerga/gc_candle_tracker/main/testing/candles_initial.csv"}
{"test_data_url": "https://raw.githubusercontent.com/ZipBoerga/gc_candle_tracker/testing_updates_sorting/testing/candles_modified.csv"}