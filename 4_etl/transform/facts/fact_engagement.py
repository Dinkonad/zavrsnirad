from pyspark.sql.functions import col, trim, row_number, when, lit
from pyspark.sql.window import Window
from spark_session import get_spark_session


def transform_engagement_fact(
    raw_data,
    dim_creator_df,
    dim_content_df,
    dim_time_df,
    dim_platform_df,
    dim_location_df,
    dim_device_df
):

    spark = get_spark_session("SocialMedia_Fact_Transform")

    print("🚀 Obrada tablice činjenica fact_engagement...")

    video_df = raw_data["video"]
    csv_df = raw_data.get("csv_video")

    cleaned_video = (
        video_df
        .select(
            col("row_id"),

            trim(col("author_handle")).alias("author_handle"),
            trim(col("category")).alias("category"),
            trim(col("genre")).alias("genre"),
            trim(col("hashtag")).alias("hashtag"),
            trim(col("tags")).alias("tags"),

            col("platform").alias("platform"),
            col("country").alias("country"),
            col("region").alias("region"),
            col("language").alias("language"),
            col("device_type").alias("device_type"),
            col("device_brand").alias("device_brand"),
            col("traffic_source").alias("traffic_source"),

            col("year_month"),
            col("week_of_year"),
            col("publish_dayofweek"),
            col("upload_hour"),

            col("duration_sec").cast("int"),

            col("views").cast("long"),
            col("likes").cast("long"),
            col("comments").cast("long"),
            col("shares").cast("long"),
            col("saves").cast("long"),

            col("engagement_rate").cast("double"),
            col("avg_watch_time_sec").cast("double"),
            col("completion_rate").cast("double")
        )
    )

    print(f"Zapisi iz videa (MySQL): {cleaned_video.count()}")

    if csv_df:
        cleaned_csv = (
            csv_df
            .select(
                trim(col("author_handle")).alias("author_handle"),
                trim(col("category")).alias("category"),
                trim(col("genre")).alias("genre"),
                trim(col("hashtag")).alias("hashtag"),
                trim(col("tags")).alias("tags"),

                col("platform"),
                col("country"),
                col("region"),
                col("language"),
                col("device_type"),
                col("device_brand"),
                col("traffic_source"),

                col("year_month"),
                col("week_of_year"),
                col("publish_dayofweek"),
                col("upload_hour"),

                col("duration_sec").cast("int"),

                col("views").cast("long"),
                col("likes").cast("long"),
                col("comments").cast("long"),
                col("shares").cast("long"),
                col("saves").cast("long"),

                col("engagement_rate").cast("double"),
                col("avg_watch_time_sec").cast("double"),
                col("completion_rate").cast("double"),

                col("row_id")
            )
        )
        print(f"Zapisi iz CSV-a: {cleaned_csv.count()}")
    else:
        cleaned_csv = None

    fact_base = cleaned_video

    if cleaned_csv:
        fact_base = fact_base.unionByName(cleaned_csv)

    print(f"Ukupno spojenih zapisa: {fact_base.count()}")


    fact_df = (
        fact_base.alias("f")

        .join(dim_creator_df.alias("c"),
              col("f.author_handle") == col("c.author_handle"), "left")

        .join(dim_content_df.alias("co"),
              (col("f.category") == col("co.category")) &
              (col("f.genre") == col("co.genre")) &
              (col("f.hashtag") == col("co.hashtag")), "left")

        .join(dim_platform_df.alias("p"),
              col("f.platform") == col("p.platform"), "left")

        .join(dim_location_df.alias("l"),
              (col("f.country") == col("l.country")) &
              (col("f.region") == col("l.region")) &
              (col("f.language") == col("l.language")), "left")

        .join(dim_device_df.alias("d"),
              (col("f.device_type") == col("d.device_type")) &
              (col("f.device_brand") == col("d.device_brand")) &
              (col("f.traffic_source") == col("d.traffic_source")), "left")

        .join(dim_time_df.alias("t"),
              (col("f.year_month") == col("t.year_month")) &
              (col("f.week_of_year") == col("t.week_of_year")) &
              (col("f.publish_dayofweek") == col("t.publish_dayofweek")) &
              (col("f.upload_hour") == col("t.upload_hour")), "left")

        .select(
            col("c.creator_tk").alias("creator_tk"),
            col("co.content_tk").alias("content_tk"),
            col("t.time_tk").alias("time_tk"),
            col("p.platform_tk").alias("platform_tk"),
            col("l.location_tk").alias("location_tk"),
            col("d.device_tk").alias("device_tk"),

            col("f.row_id"),

            col("f.duration_sec"),

            col("f.views"),
            col("f.likes"),
            col("f.comments"),
            col("f.shares"),
            col("f.saves"),

            col("f.engagement_rate"),
            col("f.avg_watch_time_sec"),
            col("f.completion_rate")
        )
    )

    fact_enhanced = (
        fact_df
        .withColumn("engagement_total",
                    col("likes") + col("comments") + col("shares") + col("saves"))

        .withColumn("like_rate",
                    col("likes") / (col("views") + 1))

        .withColumn("share_rate",
                    col("shares") / (col("views") + 1))

        .withColumn("comment_rate",
                    col("comments") / (col("views") + 1))

        .withColumn("is_high_engagement",
                    when(col("engagement_rate") > 0.1, 1).otherwise(0))
    )

    fact_final = fact_enhanced.withColumn(
        "fact_tk",
        row_number().over(Window.orderBy("creator_tk", "content_tk", "time_tk"))
    ).select(
        "fact_tk",
        "creator_tk",
        "content_tk",
        "time_tk",
        "platform_tk",
        "location_tk",
        "device_tk",

        "row_id",
        "duration_sec",
        "views",
        "likes",
        "comments",
        "shares",
        "saves",

        "engagement_total",
        "engagement_rate",
        "avg_watch_time_sec",
        "completion_rate",

        "like_rate",
        "share_rate",
        "comment_rate",
        "is_high_engagement"
    )

    total = fact_final.count()

    valid = fact_final.filter(
        col("creator_tk").isNotNull() &
        col("content_tk").isNotNull() &
        col("time_tk").isNotNull()
    ).count()

    print(f"Konačan broj redaka: {total}")
    print(f"Ispravnih redaka: {valid}")
    print(f"Kvaliteta podataka: {(valid/total*100):.2f}%")

    return fact_final
