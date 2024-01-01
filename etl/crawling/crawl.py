from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.common.keys import Keys
import datetime
import pymysql
import re
import traceback

db = pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db='Book', charset='utf8')
cursor = db.cursor()

# 카테고리 파일 새로 만든건 카테고리 긁고 이걸로 책 정보 긁을때 오류나면 이 카테고리 새로 긁는거 짜증나서였음
# 책 긁을 때 오류처리 빡세게 해놓으면 파일 괜히 만들지 않아도 됨 
def get_category():
  url = 'https://book.naver.com/category/index.nhn?cate_code=180020&tab=top100&list_type=list&sort_type=publishday&page=5'
  request = requests.get(url)
  request.encoding = 'utf-8'
  bs=BeautifulSoup(request.text,'html.parser')

  category = {} 
  a = bs.find(id='left_category').find_all('a')
  print("1. a: ",a)

  for i in range(len(a)):
    temp = a[i].get('cate')
    if (temp):
      category[a[i].string]='https://book.naver.com/category/index.nhn?cate_code={code}'.format(code = temp)
  return category


def get_book_page_urls(bsObject):
  # 책의 상세 웹페이지 주소를 추출하여 저장하는 리스트
  book_page_urls = []
  for index in range(0, 20): 
    dl_data = bsObject.find('dt', {'id':"book_title_"+str(index)})
    if dl_data==None or dl_data.find('img',{'class':"adult"}) : #성인 인증 도서
          break #건너뛰기
    link = dl_data.select('a')[0].get('href')
    book_page_urls.append(link)

  return book_page_urls


def get_book_data(bsObject):
  title, image, description = get_book_data_title_image_description(bsObject)
  url = bsObject.find('meta', {'property':'og:url'}).get('content')
  author = get_book_data_author(bsObject)
  return title, image, description, url, author


def get_book_data_title_image_description(bsObject):
    title = bsObject.find('meta', {'property':'og:title'}).get('content')
    image = bsObject.find('meta', {'property':'og:image'}).get('content')
    try:
        description = bsObject.find(id='bookIntroContent').p.string
        if description == None:
            description = str(bsObject.find(id='bookIntroContent').p)
            while True:
                if description.find('<') == -1:
                    break
                start = description.find('<'); end = description.find('>')
                description = description.replace(description[start:end+1], '')
        description = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', description)
        if len(description) > 3000:
            description = description[:3000]    
        return title, image, description  
    
    except Exception as e:
        print("e ") #TODO to logging system


def get_book_data_author(bsObject):
  try:
    author = bsObject.find('dt', text='저자').find_next_siblings('dd')[0].text.strip()
  except:
    author = '저자정보없음'
  return author
   

def crawl_books():
  driver = webdriver.Chrome(ChromeDriverManager().install())
  driver.implicitly_wait(30)

  category = get_category()

  for code in category:
    # if code=='소설': continue
    print (f"현재 카테고리 이름: {code}")
    for page in range(1,3):
        url = category[code]+'&tab=top100&list_type=list&sort_type=publishday&page={page}'.format(page=page)
        # 네이버의 베스트셀러 웹페이지 정보
        driver.get(url)
        bsObject = BeautifulSoup(driver.page_source, 'html.parser')

        book_page_urls = get_book_page_urls(bsObject)
        
        #리스트로 받아온 책의 각 세부 url 안에 들어가서 순위, 제목, 저자, 이미지, 책내용 받아오기
        for index, book_page_url in enumerate(book_page_urls):
            driver.get(book_page_url)
            bid = book_page_url.split("bid=")[1]

            sql = """SELECT COUNT(*) FROM items WHERE book_id = '""" + bid + """';"""
            cursor.execute(sql)
            result = cursor.fetchone()

            if result[0] == 0: # bid가 sql에 이미 저장되어있지 않으면 세부내용스크래핑 start
                bsObject = BeautifulSoup(driver.page_source, 'html.parser')
                title, image, description, url, author = get_book_data(bsObject)
                try:
                  save_data({'bid':bid, 
                             'title':title, 
                             'author':"'"+author+"'", 
                             'image':"'"+image+"'", 
                             'rank':str(20*(page-1)+index+1), 
                             'description':description, 
                             'category':code})
                except:
                  print(title, "sql 실패")


# mysql에 책 하나 저장
def save_data(item_info):
    # print (item_info)
    # COUNT : item_code 중복으로 인한 오류 예방 : item_code가 이미 존재하면 해당 책은 insert하지 않음
    # sql = """SELECT COUNT(*) FROM items WHERE book_id = '""" + item_info['bid'] + """';"""
    # cursor.execute(sql)
    # result = cursor.fetchone()
    # if result[0] == 0:
    sql = """INSERT INTO items VALUES('""" + item_info['bid'] + """',
    '""" + item_info['title'] + """', 
    """ + item_info['author'] + """, 
    """ + item_info['image'] + """, 
    '""" + item_info['rank'] + """',
    '""" + item_info['description'] + """',
    '""" + item_info['category'] + """',
    now()
    );"""
    print (sql)
    cursor.execute(sql)

    db.commit()


if __name__=="__main__":
  crawl_books()



'''
def login():
  driver.get('https://www.naver.com/')
  time.sleep(1)

  # 로그인 버튼을 찾고 클릭합니다
  login_btn = driver.find_element_by_class_name('link_login')
  login_btn.click()
  time.sleep(1)

  # id, pw 입력할 곳을 찾습니다.
  tag_id = driver.find_element_by_name('id')
  tag_pw = driver.find_element_by_name('pw')
  tag_id.clear()
  time.sleep(1)

  # id 입력
  tag_id.click()
  pyperclip.copy('아이디')
  tag_id.send_keys(Keys.CONTROL, 'v')
  time.sleep(1)

  # pw 입력
  tag_pw.click()
  pyperclip.copy('비번#')
  tag_pw.send_keys(Keys.CONTROL, 'v')
  time.sleep(1)

  # 로그인 버튼을 클릭합니다
  login_btn = driver.find_element_by_id('log.login')
  login_btn.click()
'''