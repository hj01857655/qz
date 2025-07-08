import sys
from hashlib import md5
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.academic.curriculum import curriculum
from src.academic.achievement import achievement
from src.auth.login import getname
from database.sql import updata

def data(username,password,school):
    try:
        # cur = curriculum()
        ach = achievement()
        obj = {
            "hash_ID": md5((username + password + school).encode('utf8')).hexdigest(),
            "hash_username": md5((username + school).encode('utf8')).hexdigest(),
            "school": school,
            "name": getname(),
            "curriculum": str([]),
            "achievement": str(ach),
            "other": '',
        }
        print(f'hash_ID:{ obj["hash_ID"]}  hash_username:{ obj["hash_username"]}')
        updata(obj)
    except:  # noqa: E722
        try:
            # data = search(username, password, 'CSMU','data')
            return {
                "achievement": eval(data['achievement']),
                # "curriculum": eval(data['curriculum'])
            }
        except Exception as e:
            return {
                "achievement": [],
                "curriculum": [],
                "code": 404,
                "error": str(e)
            }
