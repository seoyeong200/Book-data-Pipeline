##전체 카테고리 정보를 딕셔너리 형태로 (상하위 카테고리 정보를 담아서) 저장
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import time
import csv

url = 'https://book.naver.com/category/index.nhn?cate_code=180020&tab=top100&list_type=list&sort_type=publishday&page=5'
request = requests.get(url)
request.encoding = 'utf-8'
bs=BeautifulSoup(request.text,'html.parser')

category = [] #lc_100, lc_110 ..
category_name = [] #소설, 시/에세이
a = bs.find(id='left_category').find_all('a')

for i in range(len(a)):
  temp = a[i].get('name')
  if (temp):
    category.append(temp)
    category_name.append(a[i].span.string)

for i in range(len(category)):
  category[i] = category[i][3:]

# 딕셔너리로 모든 카테고리의 이름 저장
book_cat = {} 
s_sub_cat = []
#s_sub_cat_name = []
for i in range(len(category)):
  name = category_name[i] #소설
  code = category[i] 
  b_temp = {}
  x = []
  
  url = 'https://book.naver.com/category/index.nhn?cate_code={code}'.format(code = code)
  request = requests.get(url)
  request.encoding = 'utf-8'
  bs=BeautifulSoup(request.text,'html.parser')

  temp = bs.find_all(class_='category_detail_inner')
  
  for j in range(len(temp)): 
    temp2 = temp[j].find_all("a")
    if len(temp2)==1: #중간 카테고리가 없는 애들; x
      x.append(temp2[0].string)
    else:
      s_sub_cat_name = []
      for k in range(len(temp2)-1): # 1부터 마지막 원소까지 돌아야함
        s_sub_cat.append(temp2[k+1].get("href"))
        s_sub_cat_name.append(temp2[k+1].string) #가장 하위 카테고리 이름
      b_temp[temp[j].find("a").string] = s_sub_cat_name

  if len(temp2)==1:
    book_cat[name] = x
  else:
    book_cat[name] = b_temp