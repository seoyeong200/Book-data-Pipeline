from pyspark.ml.feature import Word2Vec as W2V, Word2VecModel, Normalizer
from pyspark.ml.linalg import DenseVector
from pyspark.mllib.linalg.distributed import IndexedRow, IndexedRowMatrix

from pyspark.sql import DataFrame
from pyspark.sql.types import FloatType, ArrayType
from pyspark.sql.window import Window
import pyspark.sql.functions as F

import numpy as np

from etl.utils.logger import Logging

logger = Logging("Word2Vec").get_logger()

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


    def calculate(self):
        self.df.createOrReplaceTempView('vectorized_df')
        incremental_idx_colname = 'id'
        normalized_vector_colname = 'norm'
        # make incremental id column starts from 1 (n=number of record of vectorized_df)
        vectorized_df = self.spark.sql(f"""
                                select row_number() over (order by bid) as {incremental_idx_colname}, * 
                                from vectorized_df"""
                            )
        logger.info(
            "vectorized_df: %s",
            vectorized_df.show()
        )
        
        # calculate each outputCol vector's L2 norm
        normalizer = Normalizer(inputCol=self.outputCol, outputCol=normalized_vector_colname)
        normalized_vector_df = normalizer.transform(vectorized_df)
        logger.info(
            "normalized_vector_df: %s",
            normalized_vector_df.show()
        )

        # make n*n cosine similarity matrix
        mat = (
            IndexedRowMatrix(
                normalized_vector_df
                    .select(incremental_idx_colname, normalized_vector_colname)
                    .rdd.map(lambda row: IndexedRow(row.id, row.norm.toArray()))
            )
            .toBlockMatrix()
        )
        dot = mat.multiply(mat.transpose()) # BlockMatrix object  
        logger.info(
            "cosine similaity vector is calculated."
        )
        
        # get the most similar description based on cosine similarties matrix
        dot_df = dot.toIndexedRowMatrix().rows.toDF()
        def top_elements(vector):
            """
            vector : cosine similaity vector between book x and every other book

            return top 10 value and in index of the values in the vector
            """
            return np.argsort(vector)[-11:-1][::-1].tolist()

        top_elements_udf = F.udf(top_elements)

        dot_df = dot_df.withColumn("most_similar_idx", top_elements_udf(F.col("vector")))

        vectorized_df = (
            vectorized_df
            .join(
                dot_df, vectorized_df[incremental_idx_colname] == dot_df["index"] + 1, "inner"
            )
            .select(vectorized_df["*"],dot_df["most_similar_idx"])
        )
        
        vectorized_df.write.parquet("./vectorized_df_sim.parquet")
        logger.info(
            "vectorized_df after getting the indices of the most similar book%s",
            vectorized_df.show()
        )



    """TODO
    로직을 모킹해둔 테스트코드를 작성해서 수정한 코드를 테스트하기 위해 무거운 연산을 다 해보지 않고도 
    간단하게, 가볍게 코드 안정성을 테스트해불 수 있는 환경이 갖춰져있으면 좋을 것 같다. 
    """
    def __calculate(self):
        def calculate_with_every_other_records(record):
            similarity_with_record_df = self.calcuate_simiarity(record)
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

