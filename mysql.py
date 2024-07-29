from hashlib import md5
from sqlalchemy import create_engine, Column, String, Text, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
import time
# 数据库配置
HOST = 'localhost'
PORT = '3306'
DATABASE = 'weschool'
USERNAME = 'root'
PASSWORD = 'root'

# 本地数据库
DB_URI = "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8".format(
    username=USERNAME, password=PASSWORD, host=HOST, port=PORT, db=DATABASE)
engine = create_engine(DB_URI, echo=False)
DBsession = sessionmaker(bind=engine)

Base = declarative_base()


class Person(Base):
    __tablename__ = 'user'
    hash_ID = Column(String(35))
    hash_username = Column(String(35), primary_key=True)
    school = Column(Integer)
    name = Column(String(20))
    curriculum = Column(Text)
    achievement = Column(Text)
    other = Column(Text)

    def __init__(self, obj: dict):
        self.hash_ID = obj['hash_ID']
        self.hash_username = obj['hash_username']
        self.school = obj['school']
        self.name = obj['name']
        self.curriculum = obj['curriculum']
        self.achievement = obj['achievement']
        self.other = obj['other']
        # print(f'mysql.Person:{obj}')


def mysql_insert(obj: dict):
    session = DBsession()
    a = Person(obj)
    session.add(a)
    session.commit()
    session.close()


def mysql_search(obj: dict):
    session = DBsession()
    try:
        hash_ID = obj['hash_ID']
        hash_username = obj['hash_username']
        person = session.query(Person).filter_by(
            hash_username=hash_username).first()
        if person is None:
            session.close()
            return {"msg": "数据库中找不到此人信息", "code": 404, 'error': True}
        elif person.hash_ID == hash_ID:
            session.close()
            return {
                "data": {
                    "hash_ID": person.hash_ID,
                    "hash_username": person.hash_username,
                    "school": person.school,
                    "name": person.name,
                    "curriculum": person.curriculum,
                    "achievement": person.achievement,
                    "other": person.other,
                },
                "search_time": time.time(),
                'msg': '数据库查询成功',
                'code': 200
            }
        else:
            session.close()
            return {"msg": "账号或者密码错误", "code": 201, "name": "兜底"}
    except Exception as e:
        session.close()
        return {"msg": "Mysql有问题", "code": 500, "error": str(e)}


def mysql_updata(obj: dict):
    hash_username = obj['hash_username']
    session = DBsession()
    session.query(Person).filter_by(
        hash_username=hash_username).update({
            "hash_ID": obj['hash_ID'],
            "school": obj['school'],
            "name": obj['name'],
            "curriculum": obj['curriculum'],
            "achievement": obj['achievement'],
            "other": obj['other']
        })
    session.commit()
    session.close()
