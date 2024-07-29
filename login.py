import requests.cookies
from conwork import encodeInp
from code1 import code_ocr
import os, re, json, requests
from requests.cookies import RequestsCookieJar

username = "12023050204013"
password = "852363680Fjl"
school = "10"
session = requests.Session()

def login():
    url = 'http://oa.csmu.edu.cn:8099/jsxsd/xk/LoginToXk'
    try:
        print("正在获取验证码")
        code = code_ocr(username, session)
        if os.path.exists(path='CSMU_code' + username + '.png'):
            os.remove(path='CSMU_code' + username + '.png')
            # pass
        account = encodeInp(username)
        passwd = encodeInp(password)
        encoded = account + "%%%" + passwd
        data = {
            "userAccount": account,
            "userPassword": passwd,
            "encoded": encoded,
            "RANDOMCODE": code
        }
        print("正在登录")
        # print(data)
        res = session.post(url=url, data=data)
        # print(res.text)
        if res.status_code == 200:
            if res.url == "http://oa.csmu.edu.cn:8099/jsxsd/framework/xsMain.jsp":
                print("登录成功", session.cookies.get_dict())
                with open('cookies.json', 'w') as f:
                    json.dump(session.cookies.get_dict(), f)
                return session
        elif '503 Service Unavailable' in res.text:
            print("服务器维护中")
        else:
            print("登录失败")
            print(re.findall('/<font.*?>(.*?)</font>/', res.text))
    except Exception as e:
        return e

def getname():
    url= 'http://oa.csmu.edu.cn:8099/jsxsd/framework/xsMain.jsp'
    res = session.get(url, cookies=load_cookies())
    print(re.findall('姓名：(.*?)<br/>', res.text)[0])
    if res.status_code == 200:
        name = re.findall('姓名：(.*?)<br/>', res.text)[0]
    return name

def load_cookies():
    with open('cookies.json', 'r') as f:
        cookies = json.load(f)
    return cookies

def isvaild():
    url = 'http://oa.csmu.edu.cn:8099/jsxsd/framework/xsMain.jsp'
    res = session.get(url, cookies=load_cookies())
    # print(res.status_code)
    if res.status_code == 200:
        print("cookies有效,可以获取信息")
        session.cookies.update(load_cookies())
        return session
    else:
        print("cookies无效,正在重新登录")
        return login()
