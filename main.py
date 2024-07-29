from login import username,password,school
from curriculum import curriculum
from data import data
def getData():
    try:
        # achievement()
        # curriculum()
       curriculum()
        # data(username, password,school)
    except Exception as e:
        print("获取失败，请检查网络连接")



if __name__ == '__main__':
    getData()
