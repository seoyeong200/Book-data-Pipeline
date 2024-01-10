FROM sykim98/aws-lambda-python-web-scrapping:0.1.0
RUN pip install requests \ 
    pip install boto3
COPY etl ${LAMBDA_TASK_ROOT}/etl
COPY etl/handler.py ${LAMBDA_TASK_ROOT}/handler.py
CMD [ "handler.handler" ]