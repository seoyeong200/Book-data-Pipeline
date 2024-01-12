from selenium import webdriver

from src.etl.handler import handler

driver = webdriver.Chrome()
event = {
    'category' : '소설'
}

response = handler(event=event, context=None, chrome=driver)
print(response)