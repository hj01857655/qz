import pymysql
from db_config import load_config

def create_database():
    config = load_config()
    
    # 连接到MySQL服务器
    conn = pymysql.connect(
        host=config['mysql']['host'],
        user=config['mysql']['user'],
        password=config['mysql']['password']
    )
    cursor = conn.cursor()

    # 创建数据库
    cursor.execute("CREATE DATABASE IF NOT EXISTS academic_system")

    # 使用数据库
    cursor.execute("USE academic_system")

    # 创建一个表来存储账号和密码
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        )
    ''')

    # 创建学生信息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE,
            enrollment_date DATE
        )
    ''')

    # 提交更改并关闭连接
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_database()
    print("数据库和表已创建。") 