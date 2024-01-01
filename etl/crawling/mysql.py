# mysql 테이블 스키마 
import pymysql


db = pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db='Book', charset='utf8')
cursor = db.cursor()

# sql = '''
# create table items(
#     book_id INT not null primary key,
#     title VARCHAR(200) not null,
#     author VARCHAR(150),
#     image VARCHAR(200),
#     ranking INT,
#     description VARCHAR(3000)
# );
# '''
# cursor.execute(sql)


# sql = '''
# create table user(
#     user_id INT not null primary key,
#     name VARCHAR(10) not null
# );
# '''
# cursor.execute(sql)

# sql = '''
# create table user_likes(
#     user_id INT not null,
#     book_id INT not null,
#     primary key (user_id, book_id),
#     foreign key (user_id) references user (user_id),
#     foreign key (book_id) references items (book_id)
# );
# '''
# cursor.execute(sql)

# author = "alter table items change author author VARCHAR(150);"
# image = "alter table items change image image VARCHAR(200);"
# ranking = "alter table items change ranking ranking INT;"
# descr = "alter table items change description description VARCHAR(3000);"
# cursor.execute(author);cursor.execute(image);cursor.execute(ranking);cursor.execute(descr)

# item_date_add = "alter table items add date TIMESTAMP;"
# cursor.execute(item_date_add)

db.commit()
db.close()