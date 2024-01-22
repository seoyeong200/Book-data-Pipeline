from selenium import webdriver
from selenium.webdriver.common.by import By
from tempfile import mkdtemp

import boto3
from botocore.exceptions import ClientError
import json
import os

from etl.crawling.book_data_scrapper import BookDataScrapper
from etl.crawling.book_url_getter import BookURLGetter

os.environ['AWS_DEFAULT_REGION'] = "ap-northeast-2"
os.environ['TABLE_NAME'] = "ingested_book_table"

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)

def handler(event=None, context=None, chrome=None):

    def driver_getter(chrome=None):
        if chrome is None:
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
            options.add_argument("--user-agent='Mozilla/5.0")

            return webdriver.Chrome(options=options, service=service)
        return chrome

    url_getter = BookURLGetter(driver_getter(), event['category'])
    url_getter.get_book_page_urls_scrapper()
    book_page_url = url_getter.get_book_page_url()
    
    scrapper = BookDataScrapper(driver_getter(), book_page_url)
    for book_info in scrapper.crawl_books():
        print(book_info)
        table.put_item(Item=book_info)

    return


if __name__ == '__main__':
    # handler(event={'category' : '소설'}, context=None, chrome=None)
    handler(event={'category' : '시'}, context=None, chrome=None)
    handler(event={'category' : '에세이1'}, context=None, chrome=None)
    handler(event={'category' : '에세이2'}, context=None, chrome=None)