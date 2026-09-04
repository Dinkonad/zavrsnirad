import os
import logging
from pathlib import Path
from pyspark.sql import SparkSession


def get_spark_session(app_name="SocialMedia_ETL"):

    current_dir = Path(__file__).parent.absolute()

    os.environ["JAVA_HOME"] = os.getenv("JAVA_HOME", "")

    hadoop_home = os.path.join(current_dir, "hadoop")
    os.environ["HADOOP_HOME"] = hadoop_home

    connector_dir = os.path.join(current_dir, "connectors")
    connector_path = os.path.join(connector_dir, "mysql-connector-j-9.2.0.jar")

    if not os.path.exists(connector_path):
        raise FileNotFoundError(
            f"MySQL connector not found: {connector_path}"
        )

    spark = (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")

        .config("spark.jars", connector_path)
        .config("spark.driver.extraClassPath", connector_path)

        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.warehouse.dir",
                os.path.join(current_dir, "spark-warehouse"))

        .config("spark.driver.host", "localhost")
        .config("spark.ui.showConsoleProgress", "false")

        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")

    return spark
