from spark_session import get_spark_session

spark = get_spark_session("SocialMedia_ETL_Extract_MySQL")

def extract_video_table():
    jdbc_url = "jdbc:mysql://127.0.0.1:3306/zavrsni_rad?useSSL=false&allowPublicKeyRetrieval=true"

    connection_properties = {
        "user": "root",
        "password": "root",
        "driver": "com.mysql.cj.jdbc.Driver"
    }

    query = """
        SELECT
            v.row_id, p.name AS platform, c.name AS country, c.region AS region,
            l.name AS language, cat.name AS category, g.name AS genre,
            v.hashtag, v.tags, dt.name AS device_type, dt.brand AS device_brand,
            v.traffic_source, v.sound_type, v.music_track, tt.name AS trend_type,
            a.author_handle, a.creator_tier, v.creator_avg_views, s.name AS season,
            v.year_month, v.week_of_year, v.publish_dayofweek, v.upload_hour,
            v.duration_sec, v.views, v.likes, v.comments, v.shares, v.saves,
            v.engagement_rate, v.avg_watch_time_sec, v.completion_rate
        FROM video v
        JOIN platform p ON v.platform_fk = p.id
        JOIN country c ON v.country_fk = c.id
        JOIN language l ON v.language_fk = l.id
        JOIN category cat ON v.category_fk = cat.id
        JOIN genre g ON v.genre_fk = g.id
        JOIN device_type dt ON v.device_type_fk = dt.id
        JOIN trend_type tt ON v.trend_type_fk = tt.id
        JOIN author a ON v.author_fk = a.id
        JOIN season s ON v.season_fk = s.id
    """
    print("🚀 Dohvaćanje podataka o videima iz relacijskog modela (baza 'zavrsni_rad')...")
    df = spark.read.jdbc(
        url=jdbc_url,
        table=f"({query}) AS video_flat",
        properties=connection_properties
    )
    print(f"✅ Dohvaćeno {df.count()} redaka iz relacijskog modela")
    return df




