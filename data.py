from curriculum import curriculum
from achievement import achievement
from sql import updata
from hashlib import md5
from login import getname

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
    except:
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
