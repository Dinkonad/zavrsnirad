import sys
sys.stdout.reconfigure(encoding='utf-8')

from extract.extract_mysql import extract_video_table
from extract.extract_csv import extract_from_csv
from transform.pipeline import run_transformations
from spark_session import get_spark_session
from load.run_loading import write_spark_df_to_mysql
import os


os.environ.pop("SPARK_HOME", None)


def main():

    spark = get_spark_session()
    spark.sparkContext.setLogLevel("ERROR")
    spark.catalog.clearCache()

    spark.sparkContext._jsc.addJar("connectors/mysql-connector-j-9.2.0.jar")

    print("🚀 Pokretanje ekstrakcije podataka")

    video_from_db = extract_video_table()
    video_from_csv = extract_from_csv(
        "../2_relacijski_model/social_media_trends_PROCESSED_20.csv"
    )

    raw_data = {
        "video": video_from_db,
        "csv_video": video_from_csv
    }

    print("✅ Ekstrakcija podataka završena")

    print("🚀 Pokretanje transformacije podataka")

    transformed_data = run_transformations(raw_data)

    print("✅ Transformacija podataka završena")

    print("🚀 Pokretanje učitavanja podataka")

    for table_name, df in transformed_data.items():
        print(f"Učitavanje {table_name}...")
        write_spark_df_to_mysql(df, table_name)

    print("👏 Učitavanje podataka završeno")

if __name__ == "__main__":
    main()
