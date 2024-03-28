from pyspark.ml.feature import Word2Vec as W2V
from pyspark.ml.feature import Word2VecModel
from pyspark.ml.linalg import DenseVector

from pyspark.sql import DataFrame
from pyspark.sql.types import FloatType, ArrayType
from pyspark.sql.window import Window
import pyspark.sql.functions as F

from utils.logger import Logging

logger = Logging("Word2Vec").get_stream_logger()

class Word2Vec:
    def __init__(self, df, spark=None) -> None:
        self.spark = spark
        self.df = df
        self.w2v_model_path = '/opt/spark-data/model_w2v'
        self.inputCol = "preprocessed"
        self.outputCol = "vectorized"

    def train_model(self):
        w2v = W2V(
            vectorSize=100, 
            maxIter=10, 
            minCount=5, 
            seed=42, 
            inputCol=self.inputCol, 
            outputCol=self.outputCol
        )
        model_with_preprocessed_col = w2v.fit(self.df)
        logger.info(
            "Word2Vec model trained successfully. Here's some sample vector: %s",
            model_with_preprocessed_col.getVectors().show()
        )

    """TODO
    로직을 모킹해둔 테스트코드를 작성해서 수정한 코드를 테스트하기 위해 무거운 연산을 다 해보지 않고도 
    간단하게, 가볍게 코드 안정성을 테스트해불 수 있는 환경이 갖춰져있으면 좋을 것 같다. 
    """
    def calculate(self):
        def calculate_with_every_other_records(record):
            similarity_with_record_df = self .calcuate_simiarity(record)
            print(f'calculate each similarity between record and every records\n{similarity_with_record_df}')

            similar_book_with_record_list = self.get_similar_books(similarity_with_record_df)
            print(f'get top 10 similar book lists of record\n{similar_book_with_record_list}')

            return similar_book_with_record_list[:11]
        calculate_with_every_other_records_udf = F.udf(lambda x: calculate_with_every_other_records(x), ArrayType(FloatType()))
        self.spark.udf.register("calculate_with_every_other_records_udf", calculate_with_every_other_records_udf)
        self.df = self.df.withColumn('similar_book_ids', calculate_with_every_other_records_udf(self.outputCol))
        print(self.df)

    def get_vectorized_df(self):
        loaded_w2v = Word2VecModel.load(self.w2v_model_path)
        return loaded_w2v.transform(self.df)
    
    def calcuate_simiarity(self, static_vector: DenseVector) -> DataFrame:
        
        def cos_sim(a,b):
            import numpy as np
            return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
        
        return self.df.withColumn(
            "coSim", 
            F.udf(cos_sim, FloatType())(
                F.col(self.outputCol),
                F.array([F.lit(v) for v in static_vector])
            )
        )
    
    def get_similar_books(self, df_with_cos_sim: DataFrame) -> list:
        window_with_category = (
            Window
            .partitionBy(df_with_cos_sim['category'])
            .orderBy(df_with_cos_sim['coSim'].desc())
        )
        result = (
            df_with_cos_sim
            .select('*', F.rank().over(window_with_category).alias('similarity_rank'))
            .filter(
                (F.col('similarity_rank') > 1) & (F.col('similarity_rank') <= 6)
            )
        )
        return result.select('bid').rdd.flatMap(lambda x: x).collect()

