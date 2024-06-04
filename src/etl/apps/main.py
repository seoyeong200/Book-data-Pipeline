import os

from preprocess import *
# from tfidf import tfidf
from word2vec import Word2Vec
from etl.utils.logger import Logging
from etl.utils.utils import init_spark, get_args, write_postgre, write_s3, write_local

logger = Logging("SparkMain").get_logger()

def etl():

  def _read(spark):
    s3_middle_path = os.environ.get('AWS_S3_PATH')
    s3_uri=f"{s3_middle_path}/data"
    files = '*.json.gz'
    df = spark.read.format('json').load(os.path.join(s3_uri, files))
    return df
    

  def transform(spark, df):
    preprocessed_df = preprocess(spark, df)
    logger.info(
      "final preprocessed dataframe\n%s",
      preprocessed_df.show()
    )

    arg = get_args()
    if arg['process'] == 'train':
      Word2Vec(preprocessed_df).train_model()
      logger.info(
        "Word2Vec model is recently trained"
      )

    elif arg['process'] == 'calculate':
      vectorized_df = Word2Vec(preprocessed_df).get_vectorized_df()
      try:
        write_s3(vectorized_df)
      except:
        write_local(vectorized_df, 'vectorized_df')

      df_transformed = Word2Vec(vectorized_df, spark).calculate()
      try:
        write_postgre(df_transformed, "book_with_similar_bid_list")
      except:
        write_local(df_transformed, 'df_transformed')

    else:
      logger.warn(
        "wrong argument. please try again with `--process train` or `--process calculate`"
      )


  spark = init_spark()
  df = _read(spark)
  transform(spark, df)


if __name__ == "__main__":
  etl()

  

  