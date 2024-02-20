from pyspark.ml.feature import Word2Vec as W2V
from pyspark.ml.feature import Word2VecModel
from pyspark.ml.linalg import DenseVector

from pyspark.sql import DataFrame
from pyspark.sql.types import FloatType
from pyspark.sql.window import Window
import pyspark.sql.functions as F

class Word2Vec:
    def __init__(self, df) -> None:
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
        print(model_with_preprocessed_col.getVectors().show())
        model_with_preprocessed_col.save(self.w2v_model_path)    

    def calculate(self):
        #TODO iterate each vectorized_df row = record
        record = self.df.first()
        print(f"take one record\n{record}")
        similarity_with_record_df = self.calcuate_simiarity(record[self.outputCol])
        print(f'calculate each similarity between record and every records\n{similarity_with_record_df}')
        similar_book_with_record_list = self.get_similar_books(similarity_with_record_df)
        print(f'get top 10 similar book lists of record\n{similar_book_with_record_list}')
        return similar_book_with_record_list

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

