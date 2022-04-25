from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.common.keys import Keys
import pymysql
import re

db = pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db='Book', charset='utf8')
cursor = db.cursor()

def get_book_url_lists():
    platforms = {'yes24':6, 'kyobo':6, 'aladdin':4, 'bookpark':6, 'ypbooks':4}
    book_url_list = []
    file = open('book_url_list.txt','w')
    for cp in platforms:
        page = platforms[cp]
        rank = 1
        for i in range(page):
            url = 'https://book.naver.com/bestsell/bestseller_body.naver?cp={cp}&cate=total&bestWeek=2022-01-4&indexCount=&type=list&page={page}'.format(cp=cp, page=i)
            request = requests.get(url)
            request.encoding = 'utf-8'
            bs = BeautifulSoup(request.text, 'html.parser')

            tmp = bs.find_all(class_='thumb_type')
            for t in tmp:
                # book_url_list.append(t.find("a").get("href"))
                href = t.find("a").get("href"); 
                if href!=None:
                    file.write(str(rank)+'\t'+href+'\n') 
                    rank+=1

    print("total book number: ", len(book_url_list))
    file.close()

def crawl_books(book_url_list):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.implicitly_wait(30)

    for line in book_url_list.split('\n')[90:]:
        rank = line.split('\t')[0]; url = line.split('\t')[1]
        try:
            driver.get(url)
            bid = url.split("bid=")[1]
            bsObject = BeautifulSoup(driver.page_source, 'html.parser')

            title = bsObject.find('meta', {'property':'og:title'}).get('content')
            image = bsObject.find('meta', {'property':'og:image'}).get('content')
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
            print(description)
            
            url = bsObject.find('meta', {'property':'og:url'}).get('content')
            try:
                author = bsObject.find('dt', text='저자').find_next_siblings('dd')[0].text.strip()
            except:
                author = '저자정보없음'

            print(bid, title)
            save_data({'bid':bid, 'title':title, 'author':"'"+author+"'", 'image':"'"+image+"'", 'rank':rank, 'description':description})
        except WebDriverException:
            print("page down")

def save_data(item_info):
    # print (item_info)
    # COUNT : item_code 중복으로 인한 오류 예방 : item_code가 이미 존재하면 해당 책은 insert하지 않음
    sql = """SELECT COUNT(*) FROM items WHERE book_id = '""" + item_info['bid'] + """';"""
    cursor.execute(sql)
    result = cursor.fetchone()
    desc_limit=3000
    # items 테이블 date insert
    # desc_len = len(item_info['description'])
    # if desc_len > desc_limit: # desc 너무 길면 스키마 조정
    #     sql = """ALTER TABLE items change description description VARCHAR("""+str(desc_len)+""") NOT NULL;"""
    #     cursor.execute(sql)
    #     desc_limit = desc_len
    if result[0] == 0:
        sql = """INSERT INTO items VALUES('""" + item_info['bid'] + """',
        '""" + item_info['title'] + """', 
        """ + item_info['author'] + """, 
        """ + item_info['image'] + """, 
        """ + item_info['rank'] + """,
        '""" + item_info['description'] + """');"""
        print (sql)
        cursor.execute(sql)

    db.commit()
   


# get_book_url_lists()
file = open('book_url_list.txt', 'r')
crawl_books(file.read())
file.close()
db.close()















