from flask import Flask, request, jsonify
import psycopg2
import os

from etl.utils.logger import Logging

app = Flask(__name__)
logger = Logging("API").get_logger()

DB_HOST = os.environ['POSTGRES_HOST']
DB_NAME = os.environ['POSTGRES_DB']
DB_USER = os.environ['POSTGRES_USER']
DB_PASS = os.environ['POSTGRES_PASSWORD']

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn

@app.route('/api/similar_id/<int:check_id>', methods=['GET'])
def get_similar_id(check_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = 'SELECT most_similar_idx FROM book_with_similar_bid_list WHERE id = %s'
    cursor.execute(query, (check_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if result:
        return jsonify({"similar_id": result[0]})
    else:
        return jsonify({"error": "ID not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
