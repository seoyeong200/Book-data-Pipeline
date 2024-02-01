from pyspark.ml.feature import HashingTF as MLHashingTF
from pyspark.ml.feature import IDF as MLIDF

def tfidf(df):
    tfidf_df = (
        df.rdd
        .map(lambda x: (x.title, x.remove_noise.split(" ")))
        .toDF()
        .withColumnRenamed("_1","remove_noise")
        .withColumnRenamed("_2","features")
    )

    htf = MLHashingTF(inputCol="features", outputCol="tf")
    tf = htf.transform(tfidf_df)

    idf = MLIDF(inputCol="tf", outputCol="idf")
    tfidf = idf.fit(tf).transform(tf)

    res = tfidf.rdd.map(
            lambda x : (
                x.remove_noise, x.features, x.tf, x.idf, (
                    None if x.idf is None else x.idf.values.sum()
                )
            )
        )
    
    return res
