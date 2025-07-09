import pymysql
import json
import os
from pathlib import Path

def load_config():
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    config_file = project_root / 'config' / 'config.json'

    # 如果config.json不存在，尝试使用模板文件
    if not config_file.exists():
        template_file = project_root / 'config' / 'config.json.template'
        if template_file.exists():
            print(f"⚠️  配置文件不存在，使用模板文件: {template_file}")
            config_file = template_file
        else:
            raise FileNotFoundError(f"配置文件和模板文件都不存在: {config_file}")

    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_db_connection():
    """获取数据库连接，如果连接失败返回None"""
    try:
        config = load_config()

        # 检查数据库密码配置
        db_password = config['mysql']['password']
        if not db_password:
            # 尝试从环境变量获取密码
            db_password = os.environ.get('DB_PASSWORD', '')
            if not db_password:
                print("数据库连接配置错误: 数据库密码未配置！请设置环境变量 DB_PASSWORD 或配置 config/config.json")
                return None

        return pymysql.connect(
            host=config['mysql']['host'],
            user=config['mysql']['user'],
            password=db_password,
            database=config['mysql']['database'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as e:
        print(f"数据库连接失败: {e}")
        print("程序将在无数据库模式下运行")
        return None

def execute_query(query, params=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    cursor.close()
    conn.close() 