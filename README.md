```commandline
 docker-compose --env-file .env --profile debezium up -d 
```

```commandline
 docker-compose --env-file .env --profile airflow up -d 
```

```commandline
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0 --repositories https://repo1.maven.org/maven2/ /opt/bitnami/spark/spark-apps/streaming_data_changes.py
```