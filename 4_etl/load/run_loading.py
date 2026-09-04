from pyspark.sql import DataFrame

def write_spark_df_to_mysql(spark_df: DataFrame, table_name: str, mode: str = "append"):
    jdbc_url = "jdbc:mysql://127.0.0.1:3306/zavrsni_rad_starshema?useSSL=false&allowPublicKeyRetrieval=true"

    connection_properties = {
        "user": "root",
        "password": "root",
        "driver": "com.mysql.cj.jdbc.Driver"
    }

    print(f"Upisivanje {spark_df.count()} redaka u `{table_name}` (način={mode})")
    print(f"Baza podataka: {jdbc_url}")

    try:
        spark_df.coalesce(1).write.jdbc(
            url=jdbc_url,
            table=table_name,
            mode=mode,
            properties=connection_properties
        )

        print(f"✅ Uspješno upisano u `{table_name}`")

    except Exception as e:
        print(f"❌ Greška pri upisu u `{table_name}`: {str(e)}")
        raise







