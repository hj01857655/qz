#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局Session管理器

提供整个项目的统一session管理，确保所有模块共享同一个登录状态。
"""

import requests
import time
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from threading import Lock

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class SessionManager:
    """全局Session管理器 - 单例模式"""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SessionManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self._session = requests.Session()
            self._is_logged_in = False
            self._last_activity = 0
            self._user_info = {}
            self._cookies_file = project_root / "data" / "cookies.json"
            self.initialized = True
            
            # 设置默认headers
            self._session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
    
    @property
    def session(self) -> requests.Session:
        """获取当前session对象"""
        self._update_activity()
        return self._session
    
    @property
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        return self._is_logged_in
    
    @property
    def user_info(self) -> Dict[str, Any]:
        """获取用户信息"""
        return self._user_info.copy()
    
    def _update_activity(self):
        """更新最后活动时间"""
        self._last_activity = time.time()
    
    def set_logged_in(self, user_info: Optional[Dict[str, Any]] = None):
        """设置登录状态"""
        self._is_logged_in = True
        self._user_info = user_info or {}
        self._update_activity()
        print("✅ Session管理器：用户已登录")
    
    def set_logged_out(self):
        """设置登出状态"""
        self._is_logged_in = False
        self._user_info = {}
        print("📝 Session管理器：用户已登出")
    
    def load_cookies(self) -> bool:
        """
        从文件加载cookies到session
        
        Returns:
            是否加载成功
        """
        try:
            if not self._cookies_file.exists():
                print("📝 Session管理器：Cookies文件不存在")
                return False
            
            with open(self._cookies_file, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
            
            # 检查是否是新格式（包含时间戳）
            if isinstance(cookies_data, dict) and "cookies" in cookies_data:
                timestamp = cookies_data.get("timestamp", 0)
                current_time = time.time()
                
                # 检查cookies是否过期（24小时）
                if current_time - timestamp > 24 * 3600:
                    print("⏰ Session管理器：Cookies已过期")
                    return False
                
                cookies = cookies_data["cookies"]
                print(f"✅ Session管理器：加载有效cookies（创建时间: {cookies_data.get('created_at', '未知')}）")
            else:
                # 兼容旧格式
                cookies = cookies_data if isinstance(cookies_data, dict) else {}
                print("📝 Session管理器：加载旧格式cookies")
            
            # 更新session的cookies
            self._session.cookies.update(cookies)
            return True
            
        except Exception as e:
            print(f"❌ Session管理器：加载cookies失败: {e}")
            return False
    
    def save_cookies(self) -> bool:
        """
        保存当前session的cookies到文件
        
        Returns:
            是否保存成功
        """
        try:
            self._cookies_file.parent.mkdir(exist_ok=True)
            
            # 处理重复的cookie名称，只保留最后一个
            cookies_dict = {}
            for cookie in self._session.cookies:
                cookies_dict[cookie.name] = cookie.value

            cookies_data = {
                "cookies": cookies_dict,
                "timestamp": time.time(),
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "user_info": self._user_info
            }
            
            with open(self._cookies_file, 'w', encoding='utf-8') as f:
                json.dump(cookies_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Session管理器：Cookies已保存到 {self._cookies_file}")
            return True
            
        except Exception as e:
            print(f"❌ Session管理器：保存cookies失败: {e}")
            return False
    
    def clear_cookies(self) -> bool:
        """
        清除cookies文件和session中的cookies
        
        Returns:
            是否清除成功
        """
        try:
            # 清除session中的cookies
            self._session.cookies.clear()
            
            # 删除cookies文件
            if self._cookies_file.exists():
                self._cookies_file.unlink()
                print("✅ Session管理器：Cookies文件已清除")
            
            # 重置登录状态
            self.set_logged_out()
            return True
            
        except Exception as e:
            print(f"❌ Session管理器：清除cookies失败: {e}")
            return False
    
    def is_session_valid(self) -> bool:
        """
        检查当前session是否有效
        
        Returns:
            session是否有效
        """
        try:
            url = 'http://oa.csmu.edu.cn:8099/jsxsd/framework/xsMain.jsp'
            response = self._session.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ Session管理器：响应状态码错误: {response.status_code}")
                return False
            
            # 检查是否重定向到登录页面
            if "login" in response.url.lower() or "verifycode" in response.url:
                print("❌ Session管理器：被重定向到登录页面")
                self.set_logged_out()
                return False
            
            # 检查页面内容是否包含用户信息
            if "姓名：" in response.text and "xsMain.jsp" in response.url:
                print("✅ Session管理器：Session验证成功")
                self.set_logged_in()
                return True
            else:
                print("❌ Session管理器：页面内容异常")
                self.set_logged_out()
                return False
                
        except Exception as e:
            print(f"❌ Session管理器：验证session失败: {e}")
            self.set_logged_out()
            return False
    
    def ensure_logged_in(self) -> bool:
        """
        确保用户已登录，如果未登录则尝试自动登录
        
        Returns:
            是否成功登录
        """
        # 1. 检查当前session是否有效
        if self.is_session_valid():
            return True
        
        # 2. 尝试加载cookies
        if self.load_cookies() and self.is_session_valid():
            return True
        
        # 3. 尝试自动登录
        print("🔄 Session管理器：尝试自动登录...")
        from src.auth.credentials import get_login_credentials
        
        username, password, _ = get_login_credentials()
        if username and password:
            # 导入login函数并登录
            from src.auth.login import login
            session_result = login(username, password)
            
            if session_result:
                # 登录成功，更新session管理器
                self._session = session_result
                self.set_logged_in({"username": username})
                self.save_cookies()
                return True
        
        print("❌ Session管理器：自动登录失败")
        return False
    
    def get_user_name(self) -> Optional[str]:
        """
        获取当前登录用户的姓名
        
        Returns:
            用户姓名或None
        """
        if not self.ensure_logged_in():
            return None
        
        try:
            url = 'http://oa.csmu.edu.cn:8099/jsxsd/framework/xsMain.jsp'
            response = self._session.get(url, timeout=10)
            
            if response.status_code == 200:
                import re
                name_match = re.findall('姓名：(.*?)<br/>', response.text)
                if name_match:
                    name = name_match[0].strip()
                    self._user_info["name"] = name
                    return name
        except Exception as e:
            print(f"❌ Session管理器：获取用户姓名失败: {e}")
        
        return None
    
    def reset_session(self):
        """重置session（保持cookies）"""
        cookies = dict(self._session.cookies)
        self._session = requests.Session()
        self._session.cookies.update(cookies)
        
        # 重新设置headers
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        print("🔄 Session管理器：Session已重置")


# 全局session管理器实例
session_manager = SessionManager()

def get_session() -> requests.Session:
    """
    获取全局session对象
    
    Returns:
        全局session对象
    """
    return session_manager.session

def ensure_logged_in() -> bool:
    """
    确保已登录
    
    Returns:
        是否已登录
    """
    return session_manager.ensure_logged_in()

def is_logged_in() -> bool:
    """
    检查是否已登录
    
    Returns:
        是否已登录
    """
    return session_manager.is_logged_in

def get_user_info() -> Dict[str, Any]:
    """
    获取用户信息
    
    Returns:
        用户信息字典
    """
    return session_manager.user_info

def logout():
    """登出并清除session"""
    session_manager.clear_cookies()
    session_manager.set_logged_out()
