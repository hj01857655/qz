"""
数据库模块
包含数据库连接、操作等功能
"""

from .mysql import mysql_insert, mysql_search, mysql_update
from .redis1 import redis_insert, redis_search
from .sql import search, update

__all__ = [
    'mysql_insert', 'mysql_search', 'mysql_update',
    'redis_insert', 'redis_search',
    'search', 'update'
]
