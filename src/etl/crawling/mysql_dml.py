import pymysql

db = pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db='Book', charset='utf8')
cursor = db.cursor()

def save_data(item_info):
    sql = """INSERT INTO items VALUES('""" + item_info['bid'] + """',
    '""" + item_info['title'] + """', 
    """ + item_info['author'] + """, 
    """ + item_info['image'] + """, 
    '""" + item_info['rank'] + """',
    '""" + item_info['description'] + """',
    '""" + item_info['category'] + """',
    now()
    );"""
    print (sql) #TODO print to logging system
    cursor.execute(sql)

    db.commit()