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
        
    def get_vectorized_df(self):
        loaded_w2v = Word2VecModel.load(self.w2v_model_path)
        return loaded_w2v.transform(self.df)

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
            .select(vectorized_df["id"],
                    vectorized_df["bid"],
                    dot_df["most_similar_idx"])
        )
        
        return vectorized_df
