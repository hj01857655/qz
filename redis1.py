# import json
from mysql import mysql_insert,mysql_search
from hashlib import md5
import redis


def connect_redis(host, port, db):
    # 如果host为None，则默认设置为127.0.0.1
    if host is None:
        host = "127.0.0.1"
    # 如果port为None，则默认设置为6379
    if port is None:
        port = int(6379)
    # 如果db为None，则默认设置为0
    if db is None:
        db = int(0)
    # 创建一个Redis对象
    r = redis.Redis(host=host, port=port, db=db)
    # 返回该对象
    return r


def hmset(r: redis.Redis, key: str, obj: dict):
    for index in obj:
        r.hset(key, index, obj[index])


# 定义一个函数insert，参数为一个字典obj
def redis_insert(obj: dict):
    # print(f"redis insert:{obj}")
    # 连接redis，设置主机地址和端口号，以及数据库编号
    r = connect_redis(host="127.0.0.1", port="6379", db=0)
    # 将字典obj存入redis中，key为obj['hash_ID']，value为obj
    hmset(r, obj['hash_ID'], obj)
    # 设置过期时间，时间为3600*7*24秒
    r.expire(obj['hash_ID'], 3600 * 7 * 24)
    # 关闭redis连接
    r.close()


def redis_search(obj: dict):
    try:
        r = connect_redis(host="127.0.0.1", port="6379", db=0)
        print(r.exists(obj['hash_ID']))
        get = r.hgetall(obj['hash_ID'])
        if len(get) == 0 or (get[b'curriculum'] == b'' or get[b'achievement'] == b''):
            #redis为空就查数据库
            returnData = mysql_search(obj)
            if returnData['code'] == 200:
                #数据库查到数据就插入到redis
                print("redis为空")
                redis_insert(returnData['data'])
            else:
                return mysql_insert(obj)
        else:
            print("redis有数据")
            object = {}
            for i in get:
                object[i.decode()] = get[i].decode()
            # print(object)
            return object
    except Exception as e:
        return {"msg": "Redis有问题", "code": "507", "error": str(e)}

