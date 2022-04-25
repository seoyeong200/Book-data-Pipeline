from symbol import small_stmt
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import pymysql


# 카테고리 파일 새로 만든건 카테고리 긁고 이걸로 책 정보 긁을때 오류나면 이 카테고리 새로 긁는거 짜증나서였음
# 책 긁을 때 오류처리 빡세게 해놓으면 파일 괜히 만들지 않아도 됨 
def get_category():
  # file1 = open('category_link.txt', 'w')
  # file2 = open('category_name.txt', 'w')

  url = 'https://book.naver.com/category/index.nhn?cate_code=180020&tab=top100&list_type=list&sort_type=publishday&page=5'
  request = requests.get(url)
  request.encoding = 'utf-8'
  bs=BeautifulSoup(request.text,'html.parser')

  category = {} #lc_100, lc_110 ..
  category_name = [] #소설, 시/에세이
  a = bs.find(id='left_category').find_all('a')

  for i in range(len(a)):
    temp = a[i].get('cate')
    if (temp):
    #   category.append(temp)
    #   category_name.append(a[i].string); print('cate: ', temp, " ", a[i].string)
      category[a[i].string]='https://book.naver.com/category/index.nhn?cate_code={code}'.format(code = temp)

#   for i in range(len(category)):
#     category[i] = category[i][3:]
  print(category)
  print(category[0])
  # for i in category:

  # url = 'https://book.naver.com/category/index.nhn?cate_code={code}'.format(code = code)

  cate_dict={}
  s_sub_cat = []; s_sub_cat_name = []
  for i in range(len(category)):  
    code = category[i]
    url = 'https://book.naver.com/category/index.nhn?cate_code={code}'.format(code = code)
    request = requests.get(url)
    request.encoding = 'utf-8'
    bs=BeautifulSoup(request.text,'html.parser')

    temp = bs.find_all(class_='category_detail_inner')
    
    for j in range(len(temp)): 
      if j >=3:
        break
      temp2 = temp[j].find_all("a")
      for k in range(len(temp2)-1): # 1부터 마지막 원소까지 돌아야함
        s_sub_cat.append(temp2[k+1].get("href"))
        # file1.write(temp2[k+1].get("href")+'\n')
        s_sub_cat_name.append(category_name[i])
        # file2.write(category_name[i]+'\n')
        cate_dict[category_name[i]] = temp2[k+1].get("href")

# get_category() 
# print(datetime.today().strftime('%Y-%m-%d'))