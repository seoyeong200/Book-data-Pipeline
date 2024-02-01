from pyspark.ml.feature import Word2Vec
from pyspark.ml.feature import Word2VecModel
from pyspark.sql.types import FloatType
from pyspark.sql.window import Window
import pyspark.sql.functions as F

class Word2Vec:
    def __init__(self, df) -> None:
        self.df = df
        self.w2v_model_path = './model_w2v' #TODO make it to absolute path
        self.inputCol = "preprocessed"
        self.outputCol = "vectorized"

    def train_model(self):
        w2v = Word2Vec(
            vectorSize=100, 
            maxIter=10, 
            minCount=5, 
            seed=42, 
            inputCol=self.inputCol, 
            outputCol=self.outputCol
        )
        model_with_preprocessed_col = w2v.fit(self.df)
        model_with_preprocessed_col.save(self.w2v_model_path)    

    def get_vectorized_df(self):
        loaded_w2v = Word2VecModel.load(self.w2v_model_path)
        return loaded_w2v.transform(self.df)
    
    def calcuate_simiarity(self, static_vector):
        
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
    
    def get_similar_books(self, df_with_cos_sim):
        window_with_category = (
            Window
            .partitionBy(df_with_cos_sim['category'])
            .orderBy(df_with_cos_sim['coSim'].desc())
        )
        result = (
            df_with_cos_sim
            .select('*', F.rank().over(window_with_category).alias('similarity_rank'))
            .filter(
                (F.col('similarity_rank') > 1) & (F.col('similarity_rank') <= 11)
            )
        )
        return result.select('bid')

