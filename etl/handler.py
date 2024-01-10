from selenium import webdriver
from selenium.webdriver.common.by import By
from tempfile import mkdtemp

import boto3
from botocore.exceptions import ClientError
import json
import os

from etl.crawling.crawl import BookDataScrapper

os.environ['AWS_DEFAULT_REGION'] = "ap-northeast-2"
os.environ['TABLE_NAME'] = "ingested_book_table"

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)

def handler(event=None, context=None):
    options = webdriver.ChromeOptions()
    service = webdriver.ChromeService("/opt/chromedriver")

    options.binary_location = '/opt/chrome/chrome'
    options.add_argument("--headless=new")
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument(f"--user-data-dir={mkdtemp()}")
    options.add_argument(f"--data-path={mkdtemp()}")
    options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    options.add_argument("--remote-debugging-port=9222")

    chrome = webdriver.Chrome(options=options, service=service)
    chrome.get("https://example.com/")

    scrapper = BookDataScrapper(chrome)
    book_info = scrapper.crawl_books()
    print(book_info)

    table.put_item(Item=book_info)

    table.get_item(Key={"bid": "18123571"})

    return book_info
    # return chrome.find_element(by=By.XPATH, value="//html").text

