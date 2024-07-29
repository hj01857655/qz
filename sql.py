from redis1 import redis_search,redis_insert
import mysql


def search(obj: dict):
    try:
        return redis_search(obj)
    except Exception as e:
        print(f'search:{e}')

def updata(obj: dict):
    try:
        updataparams = search(obj)
        # print(f'mysql updata params:{updataparams}')
        # print(f'mysql updata params:{updataparams}')
        if 'code' in updataparams and updataparams['code'] == 404:
            #数据库没有，就插入到数据库和redis
            print(f'returnData:{updataparams['msg']}->mysql.insert')
            
        elif 'code' in updataparams and updataparams['code'] == 201:
            #账号密码错误
            print(f'returnData:{updataparams["msg"]}')
        elif 'code' in updataparams and updataparams['code'] == 200:
            #数据库有，就更新到数据库和redis
            mysql.mysql_updata(obj)
            redis_insert(obj)
    except Exception as e:
        print(f'updata:{e}')