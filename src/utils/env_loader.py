#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境变量加载模块

支持从 .env 文件加载环境变量，提供便捷的配置管理功能。
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class EnvLoader:
    """环境变量加载器"""
    
    def __init__(self, env_file: str = ".env"):
        self.project_root = project_root
        self.env_file = self.project_root / env_file
        self._loaded = False
        self._env_vars = {}
    
    def load_env(self, override: bool = False) -> bool:
        """
        加载 .env 文件
        
        Args:
            override: 是否覆盖已存在的环境变量
            
        Returns:
            是否成功加载
        """
        if self._loaded and not override:
            return True
        
        if not self.env_file.exists():
            print(f"⚠️ 环境变量文件不存在: {self.env_file}")
            print(f"💡 请复制 .env.example 为 .env 并填入真实值")
            return False
        
        try:
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # 跳过空行和注释
                    if not line or line.startswith('#'):
                        continue
                    
                    # 解析键值对
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # 移除引号
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        # 设置环境变量
                        if override or key not in os.environ:
                            os.environ[key] = value
                            self._env_vars[key] = value
                    else:
                        print(f"⚠️ .env 文件第 {line_num} 行格式错误: {line}")
            
            self._loaded = True
            print(f"✅ 成功加载环境变量文件: {self.env_file}")
            return True
            
        except Exception as e:
            print(f"❌ 加载环境变量文件失败: {e}")
            return False
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """获取环境变量值"""
        return os.getenv(key, default)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """获取整数类型的环境变量"""
        try:
            return int(self.get(key, str(default)))
        except (ValueError, TypeError):
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """获取布尔类型的环境变量"""
        value = self.get(key, '').lower()
        if value in ('true', '1', 'yes', 'on'):
            return True
        elif value in ('false', '0', 'no', 'off'):
            return False
        return default
    
    def get_list(self, key: str, separator: str = ',', default: Optional[list] = None) -> list:
        """获取列表类型的环境变量"""
        value = self.get(key)
        if value:
            return [item.strip() for item in value.split(separator)]
        return default or []
    
    def get_credentials(self) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """获取教务系统登录凭据"""
        return (
            self.get('EDU_USERNAME'),
            self.get('EDU_PASSWORD'),
            self.get('EDU_SCHOOL', '10')
        )
    
    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return {
            'host': self.get('DB_HOST', 'localhost'),
            'port': self.get_int('DB_PORT', 3306),
            'user': self.get('DB_USER', 'root'),
            'password': self.get('DB_PASSWORD', ''),
            'database': self.get('DB_NAME', 'educational_system')
        }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """获取Redis配置"""
        return {
            'host': self.get('REDIS_HOST', '127.0.0.1'),
            'port': self.get_int('REDIS_PORT', 6379),
            'db': self.get_int('REDIS_DB', 0)
        }
    
    def get_app_config(self) -> Dict[str, Any]:
        """获取应用配置"""
        return {
            'log_level': self.get('LOG_LEVEL', 'INFO'),
            'log_file': self.get('LOG_FILE', 'logs/app.log'),
            'session_timeout': self.get_int('SESSION_TIMEOUT', 3600),
            'max_retry_count': self.get_int('MAX_RETRY_COUNT', 3),
            'ocr_timeout': self.get_int('OCR_TIMEOUT', 10)
        }
    
    def get_edu_urls(self) -> Dict[str, str]:
        """获取教务系统URL配置"""
        return {
            'base_url': self.get('EDU_BASE_URL', 'http://oa.csmu.edu.cn:8099'),
            'login_url': self.get('EDU_LOGIN_URL', 'http://oa.csmu.edu.cn:8099/jsxsd/xk/LoginToXk'),
            'achievement_url': self.get('EDU_ACHIEVEMENT_URL', 'http://oa.csmu.edu.cn:8099/jsxsd/kscj/cjcx_list'),
            'curriculum_url': self.get('EDU_CURRICULUM_URL', 'http://oa.csmu.edu.cn:8099/jsxsd/xskb/xskb_list.do')
        }
    
    def show_loaded_vars(self) -> None:
        """显示已加载的环境变量（隐藏敏感信息）"""
        if not self._loaded:
            print("❌ 尚未加载环境变量")
            return
        
        print("📋 已加载的环境变量:")
        sensitive_keys = ['password', 'secret', 'key', 'token']
        
        for key, value in self._env_vars.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                print(f"  {key} = {'*' * len(value)}")
            else:
                print(f"  {key} = {value}")


# 全局环境变量加载器实例
env_loader = EnvLoader()

def load_env(env_file: str = ".env", override: bool = False) -> bool:
    """加载环境变量的便捷函数"""
    global env_loader
    env_loader = EnvLoader(env_file)
    return env_loader.load_env(override)

def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """获取环境变量的便捷函数"""
    return env_loader.get(key, default)


if __name__ == "__main__":
    # 测试环境变量加载
    print("🔧 环境变量加载器测试")
    print("=" * 40)
    
    if load_env():
        print("\n📋 配置信息:")
        print(f"数据库配置: {env_loader.get_database_config()}")
        print(f"Redis配置: {env_loader.get_redis_config()}")
        print(f"应用配置: {env_loader.get_app_config()}")
        
        username, password, school = env_loader.get_credentials()
        print(f"登录凭据: 用户名={username}, 学校={school}")
        
        env_loader.show_loaded_vars()
    else:
        print("❌ 环境变量加载失败")
