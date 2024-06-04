MASTER_DOCKER="infrastructure-spark-master-1"
WORKER_DOCKER="infrastructure-spark-worker-a-1"

"""
PROCESS_ARG = train means training Word2Vec model from scratch
PROCESS_ARG = calculate means vectorize description string using pretrained W2V model.
"""
PROCESS_ARG=$1 # 'train', 'calculate'

CMD="python /opt/spark-apps/src/setup.py bdist_wheel && \
/opt/spark/bin/spark-submit --master spark://spark-master:7077 \
--driver-memory 1G \
--executor-memory 1G \
--py-files /opt/spark-apps/src/etl/apps/preprocess.py \
/opt/spark-apps/src/etl/apps/main.py --process ${PROCESS_ARG}" 

docker exec -it "${WORKER_DOCKER}" /bin/bash -c "${CMD}"
