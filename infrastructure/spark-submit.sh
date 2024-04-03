MASTER_DOCKER="infrastructure-spark-master-1"
WORKER_DOCKER="infrastructure-spark-worker-a-1"

# build image
# docker build -t book-data-pipeline-spark:0.1.0 .

docker-compose up -d

"""
PROCESS_ARG = train means training Word2Vec model from scratch
PROCESS_ARG = calculate means vectorize description string using pretrained W2V model.
"""
#TODO PROCESS_ARG 여기서 하드코딩으로 주지말고 shell script argument로 주고 동작하도록 수정

PROCESS_ARG="train" # 'train', 'calculate'
# CMD="pip3 install -e /opt/spark-apps/src && \
CMD="python /opt/spark-apps/src/setup.py bdist_wheel && \
/opt/spark/bin/spark-submit --master spark://spark-master:7077 \
--driver-memory 1G \
--executor-memory 1G \
--py-files /opt/spark-apps/src/etl/apps/preprocess.py \
/opt/spark-apps/src/etl/apps/main.py --process ${PROCESS_ARG}" 

"""dev tmp
export PROCESS_ARG="calculate"
python /opt/spark-apps/src/setup.py bdist_wheel && \
/opt/spark/bin/spark-submit --master spark://spark-master:7077 \
--driver-memory 1G \
--executor-memory 1G \
--py-files /opt/spark-apps/src/etl/apps/preprocess.py \
/opt/spark-apps/src/etl/apps/main.py --process $PROCESS_ARG
"""

docker exec -it "${WORKER_DOCKER}" /bin/bash -c "${CMD}"
