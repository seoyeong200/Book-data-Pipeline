FROM sykim98/aws-lambda-python-web-scrapping:0.1.0
RUN pip install requests \ 
    pip install boto3 \
    pip install ratelimit
COPY src ${LAMBDA_TASK_ROOT}/src
COPY src/etl/handler.py ${LAMBDA_TASK_ROOT}/handler.py
CMD [ "handler.handler" ]