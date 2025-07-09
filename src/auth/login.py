import requests
import re
import json
import sys
import time
from pathlib import Path
from typing import Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.conwork import encodeInp
from utils.code1 import code_ocr
from src.auth.credentials import get_login_credentials
from src.auth.session_manager import session_manager

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

def login(username: str, password: str, max_retries: int = 3) -> Optional[requests.Session]:
    """
    用户登录函数

    Args:
        username: 用户名
        password: 密码
        max_retries: 最大重试次数

    Returns:
        成功返回session对象，失败返回None
    """
    url = 'http://oa.csmu.edu.cn:8099/jsxsd/xk/LoginToXk'

    for attempt in range(max_retries):
        try:
            print(f"🔐 登录尝试 {attempt + 1}/{max_retries}")

            # 获取验证码
            print("正在获取验证码...")
            code = code_ocr(username, session_manager.session)
            if not code:
                print(f"❌ 验证码获取失败 (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    import random
                    delay = random.uniform(5, 10)  # 5-10秒随机延迟
                    print(f"⏳ 等待 {delay:.1f} 秒后重试...")
                    time.sleep(delay)
                    continue
                else:
                    print("❌ 验证码获取失败，已达到最大重试次数")
                    return None

            # 编码用户名和密码
            account = encodeInp(username)
            passwd = encodeInp(password)
            encoded = account + "%%%" + passwd

            # 准备登录数据
            data = {
                "userAccount": account,
                "userPassword": passwd,
                "encoded": encoded,
                "RANDOMCODE": code
            }

            print(f"正在登录... (验证码: {code})")
            res = session_manager.session.post(url=url, data=data, timeout=10)

            # 检查响应状态
            if res.status_code == 200:
                # 检查是否成功重定向到主页
                if res.url == "http://oa.csmu.edu.cn:8099/jsxsd/framework/xsMain.jsp":
                    print("✅ 登录成功！")

                    # 缓存凭据用于重新登录
                    set_credentials(username, password)

                    # 更新session管理器状态
                    session_manager.set_logged_in({"username": username})

                    # 保存cookies到文件
                    if session_manager.save_cookies():
                        print("✅ Cookies已保存")

                    return session_manager.session

                elif "login" in res.url.lower():
                    # 重定向回登录页面，可能是验证码错误或用户名密码错误
                    error_message = re.findall(r'<font.*?color.*?>(.*?)</font>', res.text)
                    if error_message:
                        error_text = error_message[0].strip()
                        print(f"❌ 登录失败: {error_text}")

                        # 如果是验证码错误，可以重试
                        if "验证码" in error_text or "RANDOMCODE" in error_text:
                            if attempt < max_retries - 1:
                                print("🔄 验证码错误，重新尝试...")
                                time.sleep(1)
                                continue
                        else:
                            # 用户名密码错误，不需要重试
                            print("❌ 用户名或密码错误，请检查凭据")
                            return None
                    else:
                        print("❌ 登录失败，未知错误")
                        if attempt < max_retries - 1:
                            time.sleep(1)
                            continue
                else:
                    print(f"❌ 登录重定向异常: {res.url}")
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue

            elif res.status_code == 503 or '503 Service Unavailable' in res.text:
                print("⚠️ 服务器维护中，请稍后再试")
                return None

            else:
                print(f"❌ 服务器响应异常: {res.status_code}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue

        except requests.exceptions.Timeout:
            print(f"⏰ 登录请求超时 (尝试 {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue

        except requests.exceptions.RequestException as e:
            print(f"🌐 网络请求异常: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue

        except Exception as e:
            print(f"❌ 登录过程中发生异常: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
                continue

    print(f"❌ 登录失败，已尝试 {max_retries} 次")
    return None

# save_cookies 函数已移至 session_manager.py，避免重复代码

# load_cookies 函数已移至 session_manager.py，避免重复代码

# is_cookie_valid 函数已移至 session_manager.py，避免重复代码

def refresh_session() -> Optional[requests.Session]:
    """
    刷新会话 - 使用session管理器

    Returns:
        有效的session对象或None
    """
    try:
        if session_manager.ensure_logged_in():
            return session_manager.session
        else:
            return None

    except Exception as e:
        print(f"❌ 刷新会话失败: {e}")
        return None

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
    """
    检查当前会话是否有效，如果无效则尝试刷新

    Returns:
        有效的session对象或None
    """
    return refresh_session()


def auto_login() -> Optional[requests.Session]:
    """
    自动登录函数 - 从环境变量获取凭据并登录

    Returns:
        成功返回session对象，失败返回None
    """
    try:
        username, password, _ = get_login_credentials()
        if username and password:
            print(f"从环境变量获取到凭据，开始登录用户: {username}")
            return login(username, password)
        else:
            print("❌ 未找到登录凭据，请检查环境变量设置")
            print("需要设置: EDU_USERNAME, EDU_PASSWORD")
            return None
    except Exception as e:
        print(f"自动登录失败: {e}")
        return None


def get_session_with_auto_refresh() -> Optional[requests.Session]:
    """
    获取会话，如果cookie即将过期则自动刷新

    Returns:
        有效的session对象或None
    """
    try:
        cookies_file = project_root / "data" / "cookies.json"
        if cookies_file.exists():
            with open(cookies_file, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)

            if isinstance(cookies_data, dict) and "timestamp" in cookies_data:
                timestamp = cookies_data.get("timestamp", 0)
                current_time = time.time()

                # 如果cookie在2小时内过期，提前刷新
                if current_time - timestamp > 22 * 3600:  # 22小时后刷新
                    print("🔄 Cookie即将过期，提前刷新...")
                    return refresh_session()

        # 正常检查会话有效性
        return isValid()

    except Exception as e:
        print(f"❌ 自动刷新检查失败: {e}")
        return isValid()


# clear_cookies 函数已移至 session_manager.py，避免重复代码

