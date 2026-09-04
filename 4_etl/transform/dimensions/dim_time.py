from pyspark.sql.functions import col, lit, row_number
from pyspark.sql.window import Window
from spark_session import get_spark_session

def transform_time_dim(video_df, csv_data=None):

    spark = get_spark_session()
    print("Obrada dimenzije vremena...")

    JOIN_KEYS = ["year_month", "week_of_year", "publish_dayofweek", "upload_hour"]

    def select_time_cols(df, priority):
        return df.select(
            col("year_month").cast("string").alias("year_month"),
            col("week_of_year").cast("int").alias("week_of_year"),
            col("publish_dayofweek").cast("string").alias("publish_dayofweek"),
            col("upload_hour").cast("int").alias("upload_hour"),
            lit(priority).alias("_source_priority")
        )
    combined_df = select_time_cols(video_df, 1)
    if csv_data:
        csv_df = select_time_cols(csv_data, 2)
        combined_df = combined_df.unionByName(csv_df)

    combined_df = combined_df.dropna(subset=JOIN_KEYS)

    deduped_df = (
        combined_df
        .withColumn(
            "_rn",
            row_number().over(
                Window
                .partitionBy(JOIN_KEYS)
                .orderBy(col("_source_priority").asc())
            )
        )
        .filter(col("_rn") == 1)
        .drop("_rn", "_source_priority")
    )
    final_df = (
        deduped_df
        .withColumn(
            "time_tk",
            row_number().over(
                Window.orderBy(
                    "year_month",
                    "week_of_year",
                    "publish_dayofweek",
                    "upload_hour"
                )
            )
        )
        .select(
            "time_tk",
            "year_month",
            "week_of_year",
            "publish_dayofweek",
            "upload_hour"
        )
    )

    total = final_df.count()
    unique = final_df.dropDuplicates(JOIN_KEYS).count()
    if total != unique:
        raise ValueError(f"❌ dim_time nije unique po {JOIN_KEYS}!")
    print(f"✅ dim_time: {total} unique redaka")

    return final_df












