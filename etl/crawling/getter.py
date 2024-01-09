from bs4 import BeautifulSoup


# 카테고리 파일 새로 만든건 카테고리 긁고 이걸로 책 정보 긁을때 오류나면 이 카테고리 새로 긁는거 짜증나서였음
# 책 긁을 때 오류처리 빡세게 해놓으면 파일 괜히 만들지 않아도 됨 
def get_category():
  import requests
  url = 'https://book.naver.com/category/index.nhn?cate_code=180020&tab=top100&list_type=list&sort_type=publishday&page=5'
  request = requests.get(url)
  request.encoding = 'utf-8'
  bs=BeautifulSoup(request.text,'html.parser')

  category = {} 
  a = bs.find(id='left_category').find_all('a')

  for i in range(len(a)):
    temp = a[i].get('cate')
    if temp and len(temp) > 3:
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
    # import re
    with open("tmp.txt", 'w') as f:
       f.write(str(bsObject))
    title = bsObject.find('h2', {'class': 'bookTitle_book_name__JuBQ2'}).text
    subtitle = bsObject.find('span', {'class': 'bookTitle_sub_title__B0uMS'}).text
    author = bsObject.find('span', {'class': 'bookTitle_inner_content__REoK1'}).text
    description = bsObject.find('div', {'class': 'bookIntro_introduce_area__NJbWv'}).text
    image = bsObject.find('div', {'class': 'bookImage_img_wrap__HWUgc'}).find('img')['src']

    return [title, subtitle, author, description, image]  


   
