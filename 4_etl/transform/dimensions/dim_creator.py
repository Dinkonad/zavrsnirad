from pyspark.sql.functions import col, trim, row_number, lit
from pyspark.sql.window import Window
from spark_session import get_spark_session

def transform_creator_dim(video_df, csv_data=None):

    spark = get_spark_session()
    print("Obrada dimenzije kreatora...")

    JOIN_KEY = ["author_handle"]

    base_df = video_df.select(
        trim(col("author_handle")).alias("author_handle"),
        trim(col("creator_tier")).alias("creator_tier"),
        col("creator_avg_views").cast("double").alias("creator_avg_views"),
        lit(1).alias("_source_priority")  # MySQL = prioritet 1 (viši)
    )

    if csv_data:
        csv_df = csv_data.select(
            trim(col("author_handle")).alias("author_handle"),
            trim(col("creator_tier")).alias("creator_tier"),
            col("creator_avg_views").cast("double").alias("creator_avg_views"),
            lit(2).alias("_source_priority")  
        )
        base_df = base_df.unionByName(csv_df)

    deduped_df = (
        base_df
        .withColumn(
            "_rn",
            row_number().over(
                Window
                .partitionBy(JOIN_KEY)
                .orderBy(col("_source_priority").asc())
            )
        )
        .filter(col("_rn") == 1)
        .drop("_rn", "_source_priority")
    )

    final_df = deduped_df.withColumn(
        "creator_tk",
        row_number().over(Window.orderBy("author_handle"))
    ).select(
        "creator_tk",
        "author_handle",
        "creator_tier",
        "creator_avg_views"
    )
    total = final_df.count()
    unique = final_df.dropDuplicates(JOIN_KEY).count()
    if total != unique:
        raise ValueError(f"❌ dim_creator nije unique po {JOIN_KEY}!")
    print(f"✅ dim_creator: {total} unique redaka")

    return final_df







