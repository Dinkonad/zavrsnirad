from pyspark.sql.functions import col, trim, row_number
from pyspark.sql.window import Window
from spark_session import get_spark_session

def transform_content_dim(video_df, csv_data=None):

    spark = get_spark_session()
    print("Obrada dimenzije sadržaja...")

    JOIN_KEYS = ["category", "genre", "hashtag"]

    base_df = video_df.select(
        trim(col("category")).alias("category"),
        trim(col("genre")).alias("genre"),
        trim(col("hashtag")).alias("hashtag"),
        trim(col("tags")).alias("tags")
    )

    if csv_data:
        csv_df = csv_data.select(
            trim(col("category")).alias("category"),
            trim(col("genre")).alias("genre"),
            trim(col("hashtag")).alias("hashtag"),
            trim(col("tags")).alias("tags")
        )
        base_df = base_df.unionByName(csv_df)

    deduped_df = (
        base_df
        .withColumn(
            "_rn",
            row_number().over(
                Window
                .partitionBy(JOIN_KEYS)
                .orderBy(col("tags").asc_nulls_last())
            )
        )
        .filter(col("_rn") == 1)
        .drop("_rn")
    )

    final_df = deduped_df.withColumn(
        "content_tk",
        row_number().over(
            Window.orderBy("category", "genre", "hashtag")
        )
    ).select(
        "content_tk",
        "category",
        "genre",
        "hashtag",
        "tags"
    )

    total = final_df.count()
    unique = final_df.dropDuplicates(JOIN_KEYS).count()
    if total != unique:
        raise ValueError(f"❌ dim_content nije unique po {JOIN_KEYS}!")
    print(f"✅ dim_content: {total} unique redaka")

    return final_df
