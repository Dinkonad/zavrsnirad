from transform.dimensions.dim_creator import transform_creator_dim
from transform.dimensions.dim_content import transform_content_dim
from transform.dimensions.dim_time import transform_time_dim
from transform.dimensions.dim_platform import transform_platform_dim
from transform.dimensions.dim_location import transform_location_dim
from transform.dimensions.dim_device import transform_device_dim

from transform.facts.fact_engagement import transform_engagement_fact


def run_transformations(raw_data):

    video_df = raw_data["video"]
    csv_df = raw_data.get("csv_video")

    creator_dim = transform_creator_dim(video_df, csv_df)
    print("1️⃣ Dimenzija kreatora završena")

    content_dim = transform_content_dim(video_df, csv_df)
    print("2️⃣ Dimenzija sadržaja završena")

    platform_dim = transform_platform_dim(video_df, csv_df)
    print("3️⃣ Dimenzija platforme završena")

    location_dim = transform_location_dim(video_df, csv_df)
    print("4️⃣ Dimenzija lokacije završena")

    device_dim = transform_device_dim(video_df, csv_df)
    print("5️⃣ Dimenzija uređaja završena")

    time_dim = transform_time_dim(video_df, csv_df)
    print("6️⃣ Dimenzija vremena završena")


    fact_engagement = transform_engagement_fact(
        raw_data,
        creator_dim,
        content_dim,
        time_dim,
        platform_dim,
        location_dim,
        device_dim
    )
    print("7️⃣ Tablica činjenica fact_engagement završena")

    return {
        "dim_creator": creator_dim,
        "dim_content": content_dim,
        "dim_platform": platform_dim,
        "dim_location": location_dim,
        "dim_device": device_dim,
        "dim_time": time_dim,
        "fact_engagement": fact_engagement
    }
