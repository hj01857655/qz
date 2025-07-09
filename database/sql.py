import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.redis1 import redis_search, redis_insert
from database import mysql


def search(obj: dict):
    try:
        return redis_search(obj)
    except Exception as e:
        print(f'search:{e}')

def update(obj: dict):
    """更新数据到数据库和Redis"""
    try:
        update_params = search(obj)

        if 'code' in update_params and update_params['code'] == 404:
            # 数据库没有，就插入到数据库和redis
            print(f'returnData:{update_params["msg"]}->mysql.insert')

        elif 'code' in update_params and update_params['code'] == 201:
            # 账号密码错误
            print(f'returnData:{update_params["msg"]}')
        elif 'code' in update_params and update_params['code'] == 200:
            # 数据库有，就更新到数据库和redis
            mysql.mysql_update(obj)
            redis_insert(obj)
    except Exception as e:
        print(f'update:{e}')

# 兼容性代码已移除，请直接使用 update() 函数