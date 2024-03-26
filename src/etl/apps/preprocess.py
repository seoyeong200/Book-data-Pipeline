import cld3, nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
from konlpy.tag import Okt

from pyspark.sql.types import StringType, ArrayType
from pyspark.sql import functions as F

# /opt/spark/bin/spark-submit --master spark://spark-master:7077 /opt/spark-apps/test.py

def remove_noise(text):
    import re
    text = re.sub(r'[^\w\s]', '', text)  # 특수 문자 제거
    text = re.sub(r'\d+', '', text)      # 숫자 제거
    return text

def clean(s):
    """ 
    Detect the language of the given column value s.
    - lower case and remove stopwords if its' english.
    - otherwise, regard it as korean and do speech tagging job 
    (remaining only nown, verb, adjective)
    """
    try:
        language = cld3.get_language(s)
        if language.language == 'en':
            s = s.lower()
            nltk.download('stopwords')
            def remove_stopwords(text):
                stop_words = set(stopwords.words('english'))
                word_tokens = text.split()
                clean_words = [word for word in word_tokens if word not in stop_words]
                return clean_words
            return remove_stopwords(s)
        else:
            def speech_tagging(text):
                okt = Okt()
                clean_words = []
                for word in okt.pos(text, stem=True):
                    if word[1] in ['Noun', 'Verb', 'Adjective']:
                        clean_words.append(word[0])
                return clean_words
            return speech_tagging(s)
    except:
        return []

            
def preprocess(spark, df):
    df = df.select(F.col("Item.bid.S").alias('bid'),
                    F.col("Item.title.S").alias('title'),
                    F.col("Item.subtitle.S").alias('subtitle'),
                    F.col("Item.author.S").alias('author'),
                    F.col("Item.category.S").alias('category'),
                    F.col("Item.description.S").alias('description'),
                    F.col("Item.image.S").alias('image'),
                    F.col("Item.rank.S").alias('rank')
                )
    
    # null 컬럼 제거 - description not exists, or scrapping failure
    df = df.filter(F.col('description') != "")

    # data preprocessing - 특수문자, 숫자 제거
    cols_remove_noise = F.udf(lambda z : remove_noise(z), StringType())
    spark.udf.register("cols_remove_noise", cols_remove_noise)
    df = df.withColumn('preprocessed', cols_remove_noise('description'))


    # data preprocessing - 명사, 동사, 형용사만 남기기
    colsClean = F.udf(lambda z : clean(z), ArrayType(StringType()))
    spark.udf.register("colsClean", colsClean)
    df = df.withColumn('preprocessed', colsClean('preprocessed'))

    return df
