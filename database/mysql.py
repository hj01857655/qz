import sys
from pathlib import Path
from sqlalchemy import create_engine, Column, String, Text, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
import time

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置加载功能已移至 db_config.py，避免重复代码

def get_database_uri():
    """获取数据库连接URI"""
    from .db_config import load_config

    config = load_config()
    mysql_config = config["mysql"]

    if not mysql_config["password"]:
        raise ValueError("数据库密码未配置！请设置环境变量 DB_PASSWORD 或配置 config/config.json")

    return "mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8".format(
        **mysql_config
    )

# 创建数据库引擎和会话
try:
    engine = create_engine(get_database_uri(), echo=False)
    DBsession = sessionmaker(bind=engine)
except Exception as e:
    print(f"数据库连接配置错误: {e}")
    print("请检查配置文件或环境变量设置")
    engine = None
    DBsession = None

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


def mysql_update(obj: dict):
    """更新MySQL数据库中的用户信息"""
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
