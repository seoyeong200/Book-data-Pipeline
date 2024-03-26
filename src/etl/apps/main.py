from pyspark.sql import SparkSession
from pyspark.sql.functions import col,date_format

import os
import argparse

from preprocess import *
# from tfidf import tfidf
from word2vec import Word2Vec
from utils.logger import Logging

logger = Logging("SparkMain").get_logger()

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

def get_args():
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


if __name__ == "__main__":
  spark = init_spark()
  s3_middle_path = os.environ.get('AWS_S3_PATH')
  s3_uri=f"{s3_middle_path}/data"
  files = '*.json.gz'
  df = spark.read.format('json').load(os.path.join(s3_uri, files))

  preprocessed_df = preprocess(spark, df)

  arg = get_args()
  if arg['process'] == 'train':
    Word2Vec(preprocessed_df).train_model()
  elif arg['process'] == 'calculate':
    vectorized_df = Word2Vec(preprocessed_df).get_vectorized_df()
    _ = Word2Vec(vectorized_df, spark).calculate()
  else:
    print("wrong argument. please try again with `--process train` or `--process calculate`")

  