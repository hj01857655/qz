import requests
import os
import re
import json
import sys
from pathlib import Path
from typing import Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.conwork import encodeInp
from utils.code1 import code_ocr

session = requests.Session()

# 全局变量存储登录凭据（仅在内存中，不持久化）
_cached_credentials = {
    "username": None,
    "password": None
}

def set_credentials(username: str, password: str) -> None:
    """设置登录凭据（仅存储在内存中）"""
    global _cached_credentials
    _cached_credentials["username"] = username
    _cached_credentials["password"] = password

def clear_credentials() -> None:
    """清除缓存的登录凭据"""
    global _cached_credentials
    _cached_credentials["username"] = None
    _cached_credentials["password"] = None

def get_credentials() -> tuple[Optional[str], Optional[str]]:
    """获取缓存的登录凭据"""
    return _cached_credentials["username"], _cached_credentials["password"]

def login(username: str, password: str) -> Optional[requests.Session]:
    """
    用户登录函数

    Args:
        username: 用户名
        password: 密码

    Returns:
        成功返回session对象，失败返回None
    """
    url = 'http://oa.csmu.edu.cn:8099/jsxsd/xk/LoginToXk'
    try:
        print("正在获取验证码")
        code = code_ocr(username, session)
        if not code:
            print("验证码获取失败")
            return None

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
                print("登录成功")
                # 缓存凭据用于重新登录
                set_credentials(username, password)
                # 保存cookies到文件
                save_cookies(session.cookies.get_dict())
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

def save_cookies(cookies_dict: dict) -> None:
    """保存cookies到文件"""
    try:
        cookies_file = project_root / "data" / "cookies.json"
        cookies_file.parent.mkdir(exist_ok=True)
        with open(cookies_file, 'w', encoding='utf-8') as f:
            json.dump(cookies_dict, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存cookies失败: {e}")

def load_cookies() -> dict:
    """从文件加载cookies"""
    try:
        cookies_file = project_root / "data" / "cookies.json"
        if cookies_file.exists():
            with open(cookies_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"加载cookies失败: {e}")
    return {}

def getname() -> Optional[str]:
    """获取用户姓名"""
    session_obj = isValid()  # 确保会话有效
    if session_obj:
        url = 'http://oa.csmu.edu.cn:8099/jsxsd/framework/xsMain.jsp'
        try:
            res = session_obj.get(url)
            if res.status_code == 200:
                name_match = re.findall('姓名：(.*?)<br/>', res.text)
                if name_match:
                    name = name_match[0]
                    print(f"获取到用户姓名: {name}")
                    return name
        except Exception as e:
            print(f"获取用户姓名失败: {e}")
    return None

def isValid() -> Optional[requests.Session]:
    """检查当前会话是否有效"""
    try:
        # 尝试加载cookies
        cookies = load_cookies()
        if cookies:
            session.cookies.update(cookies)
            url = 'http://oa.csmu.edu.cn:8099/jsxsd/framework/xsMain.jsp'
            res = session.get(url)
            if res.status_code == 200 and "xsMain.jsp" in res.url:
                print("cookies有效,可以获取信息")
                return session

        print("cookies无效或不存在,需要重新登录")
        # 尝试使用缓存的凭据重新登录
        username, password = get_credentials()
        if username and password:
            print("使用缓存凭据重新登录")
            return login(username, password)
        else:
            print("没有缓存的登录凭据，请先调用login()函数登录")
            return None

    except Exception as e:
        print(f"验证cookie时发生异常: {e}")
        # 尝试使用缓存的凭据重新登录
        username, password = get_credentials()
        if username and password:
            print("尝试使用缓存凭据重新登录")
            return login(username, password)
        else:
            print("没有缓存的登录凭据，请先调用login()函数登录")
            return None

