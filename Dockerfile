FROM sykim98/aws-lambda-python-web-scrapping:0.1.0
RUN pip install requests
COPY etl/* ${LAMBDA_TASK_ROOT}
CMD [ "handler.handler" ]