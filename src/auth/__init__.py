"""
认证模块
包含登录、验证、cookie管理等功能
"""

from .login import (
    login, isValid, getname, auto_login,
    refresh_session, get_session_with_auto_refresh
)
from .credentials import get_login_credentials, clear_credentials
from .session_manager import session_manager

__all__ = [
    'login', 'isValid', 'getname', 'auto_login',
    'refresh_session', 'get_session_with_auto_refresh',
    'get_login_credentials', 'clear_credentials',
    'session_manager'
]
