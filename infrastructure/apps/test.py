from pyspark.sql import SparkSession
from pyspark.sql.functions import col,date_format

import os

"""TODO
1. connect s3
2. read book data from s3 
3. preprocessing
4. training W2V or D2V or BERT
5. get some kind of result or whatever
"""
def init_spark():
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
    .getOrCreate()
  return spark


if __name__ == "__main__":
  spark = init_spark()
  s3_middle_path = "01706192738584-572ab4dc"
  s3_uri=f"s3://book-data-pipeline-prod-serverlessdeploymentbucket-bjra5omsi63o/AWSDynamoDB/{s3_middle_path}/data"
#   files = '*.json.gz'
  files = 'd44l3vkmeyyidfsfvf4zjuwilm.json.gz'
  df = spark.read.format('json').load(os.path.join(s3_uri, files))
  print(df.printSchema())