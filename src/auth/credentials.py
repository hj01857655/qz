#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全凭据管理模块

此模块提供安全的凭据管理功能，支持：
- 环境变量读取
- 配置文件读取
- 交互式输入
- 内存缓存（不持久化敏感信息）

⚠️ 安全注意事项：
- 永远不要在代码中硬编码敏感信息
- 使用环境变量或安全的配置文件
- 定期更换密码
"""

import sys
from pathlib import Path
from typing import Optional, Tuple

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入环境变量加载器
from src.utils.env_loader import env_loader


class CredentialsManager:
    """安全凭据管理器"""
    
    def __init__(self):
        self.project_root = project_root
        self._cached_credentials = {}
        # 尝试加载 .env 文件
        env_loader.load_env()
    
    def get_credentials(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        从环境变量获取登录凭据（包括.env文件）

        Returns:
            (username, password, school) 元组
        """
        # 从环境变量获取（包括 .env 文件）
        username, password, school = env_loader.get_credentials()

        if username and password:
            print("✅ 从环境变量/.env文件获取凭据")
            return username, password, school
        else:
            print("❌ 未找到环境变量中的凭据")
            print("💡 请确保设置了以下环境变量或在.env文件中配置：")
            print("   EDU_USERNAME=您的学号")
            print("   EDU_PASSWORD=您的密码")
            print("   EDU_SCHOOL=10")
            return None, None, None
    

    
    def clear_cached_credentials(self) -> None:
        """清除缓存的凭据"""
        self._cached_credentials.clear()
        print("✓ 已清除缓存的凭据")
    
    def validate_credentials(self, username: str, password: str) -> bool:
        """验证凭据格式"""
        if not username or not password:
            return False

        # 基本格式验证
        if len(username) < 3:
            print("⚠️ 用户名长度过短")
            return False

        if len(password) < 6:
            print("⚠️ 密码长度过短")
            return False

        return True


# 全局凭据管理器实例
credentials_manager = CredentialsManager()

def get_login_credentials() -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    获取登录凭据的便捷函数（仅从环境变量）

    Returns:
        (username, password, school) 元组
    """
    return credentials_manager.get_credentials()

def clear_credentials() -> None:
    """清除缓存凭据的便捷函数"""
    credentials_manager.clear_cached_credentials()


if __name__ == "__main__":
    # 测试凭据管理器
    print("🔐 凭据管理器测试")
    username, password, school = get_login_credentials(force_input=True)
    print(f"获取到凭据: 用户名={username}, 学校={school}")
