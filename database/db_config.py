import pymysql
import json

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def get_db_connection():
    config = load_config()
    return pymysql.connect(
        host=config['mysql']['host'],
        user=config['mysql']['user'],
        password=config['mysql']['password'],
        database=config['mysql']['database'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    ) 

def execute_query(query, params=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    cursor.close()
    conn.close() 