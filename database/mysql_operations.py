from db_config import get_db_connection
import pymysql
import json

def insert_user(username, password, remember_me=False):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO users (username, password, remember_me) VALUES (%s, %s, %s)
        ''', (username, password, remember_me))
        conn.commit()
        print("用户已添加。")
    except pymysql.IntegrityError:
        print("用户名已存在。")
    finally:
        cursor.close()
        conn.close()

def get_user(username):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM users WHERE username = %s
    ''', (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def update_user_password(username, password, remember_me):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE users SET password = %s, remember_me = %s WHERE username = %s
        ''', (password, remember_me, username))
        conn.commit()
        print("用户密码已更新。")
    finally:
        cursor.close()
        conn.close()

def get_remembered_user():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM users WHERE remember_me = TRUE
    ''')
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def insert_or_update_class_data_from_json(json_file):
    # 读取JSON文件
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 连接数据库
    conn = get_db_connection()
    cursor = conn.cursor()

    # 插入或更新数据
    query = """
    INSERT INTO class_info (serial_number, class_number, class_name, campus, department, major_name, education_level, 
                            registration_number, academic_year, major_code, class_size, actual_size, fixed_classroom, 
                            contact_number, valid_status, official_major_name, official_major_code, discipline_category, 
                            operation_link)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        class_name = VALUES(class_name),
        campus = VALUES(campus),
        department = VALUES(department),
        major_name = VALUES(major_name),
        education_level = VALUES(education_level),
        registration_number = VALUES(registration_number),
        academic_year = VALUES(academic_year),
        major_code = VALUES(major_code),
        class_size = VALUES(class_size),
        actual_size = VALUES(actual_size),
        fixed_classroom = VALUES(fixed_classroom),
        contact_number = VALUES(contact_number),
        valid_status = VALUES(valid_status),
        official_major_name = VALUES(official_major_name),
        official_major_code = VALUES(official_major_code),
        discipline_category = VALUES(discipline_category),
        operation_link = VALUES(operation_link)
    """

    try:
        for entry in data:
            cursor.execute(query, (
                int(entry.get('serial_number') or 0),  # 将空字符串转换为0
                entry.get('class_number'),
                entry.get('class_name'),
                entry.get('campus'),
                entry.get('department'),
                entry.get('major_name'),
                entry.get('education_level'),
                entry.get('registration_number'),
                entry.get('academic_year'),
                entry.get('major_code'),
                int(entry.get('class_size') or 0),  # 将空字符串转换为0
                int(entry.get('actual_size') or 0),  # 将空字符串转换为0
                entry.get('fixed_classroom'),
                entry.get('contact_number'),
                entry.get('valid_status'),
                entry.get('official_major_name'),
                entry.get('official_major_code'),
                entry.get('discipline_category'),
                entry.get('operation_link')
            ))
        conn.commit()
        print("数据已成功插入或更新到数据库。")
    except pymysql.MySQLError as e:
        print(f"插入或更新数据时发生错误：{e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # 示例：插入用户
    insert_user('example_user', 'example_password', True)

    # 示例：查询用户
    user = get_user('example_user')
    if user:
        print(f"用户信息：ID={user['id']}, 用户名={user['username']}, 密码={user['password']}")
    else:
        print("用户不存在。") 