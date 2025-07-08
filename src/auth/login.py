import requests
import os
import re
import json
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.conwork import encodeInp
from utils.code1 import code_ocr

session = requests.Session()

def login(username, password):
    url = 'http://oa.csmu.edu.cn:8099/jsxsd/xk/LoginToXk'
    try:
        print("正在获取验证码")
        code = code_ocr(username, session)
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
        res = session.post(url=url, data=data)
        if res.status_code == 200:
            if res.url == "http://oa.csmu.edu.cn:8099/jsxsd/framework/xsMain.jsp":
                print("登录成功", session.cookies.get_dict())
                # 返回会话对象
                return session
            else:
                print("登录重定向失败")
        elif '503 Service Unavailable' in res.text:
            print("服务器维护中")
        else:
            print("登录失败")
            error_message = re.findall(r'<font.*?>(.*?)</font>', res.text)
            if error_message:
                print(error_message[0])
    except Exception as e:
        print(f"登录过程中发生异常: {e}")
    return None

def getname():
    session = isValid()  # 确保会话有效
    if session:
        url = 'http://oa.csmu.edu.cn:8099/jsxsd/framework/xsMain.jsp'
        res = session.get(url)
        if res.status_code == 200:
            name = re.findall('姓名：(.*?)<br/>', res.text)[0]
            print(name)
            return name
    return None

def load_cookies():
    with open('cookies.json', 'r') as f:
        cookies = json.load(f)
    return cookies

def isValid():
    """检查当前会话是否有效"""
    try:
        session.cookies.update(load_cookies())
        url = 'http://oa.csmu.edu.cn:8099/jsxsd/framework/xsMain.jsp'
        res = session.get(url)
        if res.status_code == 200:
            print("cookies有效,可以获取信息")
            return session
        else:
            print("cookies无效,正在重新登录")
            return login()
    except Exception as e:
        print(f"验证cookie时发生异常: {e}")
        return login()

