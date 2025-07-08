"""
认证模块
包含登录、验证等功能
"""

from .login import login, isValid, getname

__all__ = ['login', 'isValid', 'getname']
