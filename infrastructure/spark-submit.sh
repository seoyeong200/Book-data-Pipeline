MASTER_DOCKER="infrastructure-spark-master-1"
WORKER_DOCKER="infrastructure-spark-worker-a-1"

# build image
# docker build -t book-data-pipeline-spark:0.1.0 .

docker-compose up -d

CMD="/opt/spark/bin/spark-submit --master spark://spark-master:7077 \
--driver-memory 1G \
--executor-memory 1G \
/opt/spark-apps/test.py"

docker exec -it "${WORKER_DOCKER}" /bin/bash -c "${CMD}"
