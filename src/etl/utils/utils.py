def is_same_week(dateString: str) -> bool:
    """
    Return whether input dateString is in the same week
    as the date of this function called.
    """
    import datetime

    d1 = datetime.datetime.strptime(dateString,'%Y-%m-%d')
    d2 = datetime.datetime.today()
    print(f"input date={d1}, today={d2}")
    return d1.isocalendar()[1] == d2.isocalendar()[1] \
              and d1.year == d2.year


def init_spark():
  import os
  from pyspark.sql import SparkSession

  aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
  aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

  spark = SparkSession.builder\
    .appName("book_data_pipeline-spark")\
    .config('spark.hadoop.fs.s3a.access.key', aws_access_key)\
    .config('spark.hadoop.fs.s3a.secret.key', aws_secret_key)\
    .config('spark.hadoop.fs.s3a.aws.credentials.provider', 'org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider')\
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")\
    .config('spark.jars.packages', '/opt/spark/jars/hadoop-aws-3.2.0.jar')\
    .config('spark.jars.packages', '/opt/spark/jars/aws-java-sdk-bundle-1.11.375.jar')\
    .config('spark.jars.packages', '/opt/spark/jars/postgresql-42.7.3.jar')\
    .getOrCreate()
  return spark


def write_local(df, df_name):
   df.write.parquet(f'/opt/spark-data/{df_name}.parquet')


def write_s3(df):
   import os
   s3_uri = os.path.join(os.environ['AWS_S3_PATH'], 'processed_data')
   
   df.write \
    .mode('overwrite') \
    .parquet(path=s3_uri)
   


def write_postgre(df, tablename):
   import os
  
   username, password, dbname = os.environ['POSTGRES_USER'], os.environ['POSTGRES_PASSWORD'], os.environ['POSTGRES_DB']
   
   df.select("*")\
      .write \
      .format("jdbc") \
      .option("url", f"jdbc:postgresql://postgreDB:5432/{dbname}") \
      .option("driver", "org.postgresql.Driver") \
      .option("dbtable", tablename) \
      .option("user", username) \
      .option("password", password) \
      .save() 


def get_args():
  import argparse

  argument_parser = argparse.ArgumentParser(description="argument that indicate which process is this work needs to do, training model or calculate similarities between each of the book.")
  argument_parser.add_argument(
    '--process', 
    type=str, 
    choices=['train', 'calculate'], 
    default='calculate',
    help='`train` stands for retraining the Word2Vec model, `calculate` stands for make each book a list of similar book'
  )
  args, unknown = argument_parser.parse_known_args()
  return vars(args)