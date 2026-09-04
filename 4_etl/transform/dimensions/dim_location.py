from pyspark.sql.functions import col, trim, lit, row_number
from pyspark.sql.window import Window
from spark_session import get_spark_session

def transform_location_dim(video_df, csv_data=None):

    spark = get_spark_session()
    print("Obrada dimenzije lokacije...")

    JOIN_KEYS = ["country", "region", "language"]

    mysql_df = (
        video_df
        .select(
            trim(col("country")).alias("country"),
            trim(col("region")).alias("region"),
            trim(col("language")).alias("language"),
            lit(1).alias("_source_priority")
        )
    )

    if csv_data:
        csv_df = (
            csv_data
            .select(
                trim(col("country")).alias("country"),
                trim(col("region")).alias("region"),
                trim(col("language")).alias("language"),
                lit(2).alias("_source_priority")
            )
        )
        combined_df = mysql_df.unionByName(csv_df)
    else:
        combined_df = mysql_df

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
            "location_tk",
            row_number().over(
                Window.orderBy("country", "region", "language")
            )
        )
        .select(
            "location_tk",
            "country",
            "region",
            "language"
        )
    )

    total = final_df.count()
    unique = final_df.dropDuplicates(JOIN_KEYS).count()
    if total != unique:
        raise ValueError(f"❌ dim_location nije unique po {JOIN_KEYS}!")
    print(f"✅ dim_location: {total} unique redaka")

    return final_df
