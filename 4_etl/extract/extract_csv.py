from pyspark.sql.functions import col, date_format
from spark_session import get_spark_session

def extract_from_csv(file_path):

    spark = get_spark_session("ETL_Extract_CSV")

    print(f"Dohvaćanje podataka iz CSV-a: {file_path}")

    df = spark.read \
        .option("header", True) \
        .option("inferSchema", True) \
        .csv(file_path)


    if "year_month" in df.columns and dict(df.dtypes)["year_month"] != "string":
        df = df.withColumn("year_month", date_format(col("year_month"), "yyyy-MM"))

    print(f"Dohvaćeno {df.count()} redaka iz CSV-a")

    return df



