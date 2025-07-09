# import json
import redis
import sys
from hashlib import md5
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.mysql import mysql_insert, mysql_search


def connect_redis(host=None, port=None, db=None):
    """连接Redis，支持从配置文件读取参数"""
    try:
        # 如果没有提供参数，尝试从配置文件读取
        if host is None or port is None or db is None:
            try:
                from .db_config import load_config
                config = load_config()
                redis_config = config.get('redis', {})

                host = host or redis_config.get('host', '127.0.0.1')
                port = port or redis_config.get('port', 6379)
                db = db or redis_config.get('db', 0)
            except Exception:
                # 如果配置文件读取失败，使用默认值
                host = host or "127.0.0.1"
                port = port or 6379
                db = db or 0

        # 确保端口和数据库是整数
        port = int(port)
        db = int(db)

        # 创建Redis连接
        r = redis.Redis(host=host, port=port, db=db)
        # 测试连接
        r.ping()
        return r

    except Exception as e:
        print(f"Redis连接失败: {e}")
        return None


def hmset(r: redis.Redis, key: str, obj: dict):
    for index in obj:
        r.hset(key, index, obj[index])


def redis_insert(obj: dict):
    """插入数据到Redis"""
    try:
        r = connect_redis()
        if not r:
            print("Redis连接失败，跳过插入操作")
            return False

        # 将字典obj存入redis中，key为obj['hash_ID']，value为obj
        hmset(r, obj['hash_ID'], obj)
        # 设置过期时间，时间为7天
        r.expire(obj['hash_ID'], 3600 * 24 * 7)
        # 关闭redis连接
        r.close()
        return True

    except Exception as e:
        print(f"Redis插入失败: {e}")
        return False


def redis_search(obj: dict):
    """从Redis搜索数据，如果没有则查询MySQL"""
    try:
        r = connect_redis()
        if not r:
            print("Redis连接失败，直接查询MySQL")
            return mysql_search(obj)

        # 检查Redis中是否存在数据
        exists = r.exists(obj['hash_ID'])
        print(f"Redis中存在数据: {bool(exists)}")

        get = r.hgetall(obj['hash_ID'])

        # 如果Redis为空或数据不完整，查询数据库
        if len(get) == 0 or (get.get(b'curriculum') == b'' or get.get(b'achievement') == b''):
            print("Redis为空或数据不完整，查询数据库")
            returnData = mysql_search(obj)

            if returnData.get('code') == 200:
                # 数据库查到数据就插入到redis
                print("数据库查询成功，缓存到Redis")
                redis_insert(returnData['data'])
                return returnData
            else:
                return returnData
        else:
            print("Redis有完整数据")
            # 将bytes转换为字符串
            result = {}
            for key, value in get.items():
                result[key.decode()] = value.decode()

            r.close()
            return result

    except Exception as e:
        print(f"Redis搜索失败: {e}")
        return {"msg": "Redis有问题", "code": 507, "error": str(e)}

