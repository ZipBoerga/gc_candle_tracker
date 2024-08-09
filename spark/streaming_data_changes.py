from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    TimestampType,
)
import pyspark.sql.functions as F

KAFKA_SERVER = 'broker:29092'

if __name__ == '__main__':
    spark = SparkSession.builder.appName('Candle Price Tracking').getOrCreate()

    price_changes_df = (
        spark.readStream.format('kafka')
        .option('kafka.bootstrap.servers', KAFKA_SERVER)
        .option('subscribe', 'candles.candles.public.current_prices')
        .option('startingOffsets', 'earliest')
        .load()
        .selectExpr('CAST(value AS STRING) as value')
    )

    # .option('data_generating.bootstrap.servers', KAFKA_SERVER)
    # .option('topic', 'turnout_by_location')
    # .option('checkpointLocation', '/opt/checkpoints/turnout_by_location')
    # .outputMode('append')
    price_changes_output_df = (
        price_changes_df.select('value')
        .writeStream.format('console')
        .option('truncate', 'false')
        .start()
    )

    price_changes_output_df.awaitTermination()
