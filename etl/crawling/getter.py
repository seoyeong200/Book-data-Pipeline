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
    import re

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
   
