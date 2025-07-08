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

import os
import json
import getpass
import sys
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

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
    
    def get_credentials(self, force_input: bool = False) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        获取登录凭据
        
        优先级：
        1. 环境变量
        2. 配置文件
        3. 交互式输入
        
        Args:
            force_input: 强制使用交互式输入
            
        Returns:
            (username, password, school) 元组
        """
        if force_input:
            return self._get_interactive_credentials()
        
        # 1. 尝试从环境变量获取（包括 .env 文件）
        username, password, school = env_loader.get_credentials()

        if username and password:
            print("✓ 从环境变量/.env文件获取凭据")
            return username, password, school
        
        # 2. 尝试从配置文件获取
        config_creds = self._get_config_credentials()
        if config_creds[0] and config_creds[1]:
            print("✓ 从配置文件获取凭据")
            return config_creds
        
        # 3. 交互式输入
        print("⚠️ 未找到环境变量或配置文件中的凭据")
        return self._get_interactive_credentials()
    
    def _get_config_credentials(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """从配置文件获取凭据"""
        try:
            config_file = self.project_root / "config" / "config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                edu_config = config.get('educational_system', {})
                return (
                    edu_config.get('username'),
                    edu_config.get('password'),
                    edu_config.get('school', '10')
                )
        except Exception as e:
            print(f"读取配置文件失败: {e}")
        
        return None, None, None
    
    def _get_interactive_credentials(self) -> Tuple[str, str, str]:
        """交互式获取凭据"""
        print("\n🔐 请输入登录凭据:")
        print("=" * 40)
        
        try:
            username = input("用户名/学号: ").strip()
            if not username:
                raise ValueError("用户名不能为空")
            
            password = getpass.getpass("密码: ").strip()
            if not password:
                raise ValueError("密码不能为空")
            
            school = input("学校代码 [默认: 10]: ").strip() or "10"
            
            # 询问是否保存到环境变量
            save_env = input("\n是否保存到环境变量? (y/N): ").strip().lower()
            if save_env in ['y', 'yes']:
                self._show_env_instructions(username, password, school)
            
            return username, password, school
            
        except KeyboardInterrupt:
            print("\n\n用户取消输入")
            sys.exit(1)
        except Exception as e:
            print(f"输入错误: {e}")
            return self._get_interactive_credentials()
    
    def _show_env_instructions(self, username: str, password: str, school: str) -> None:
        """显示环境变量设置说明"""
        print("\n📝 环境变量设置说明:")
        print("=" * 40)
        print("Windows (PowerShell):")
        print(f'$env:EDU_USERNAME="{username}"')
        print(f'$env:EDU_PASSWORD="{password}"')
        print(f'$env:EDU_SCHOOL="{school}"')
        print("\nWindows (CMD):")
        print(f'set EDU_USERNAME={username}')
        print(f'set EDU_PASSWORD={password}')
        print(f'set EDU_SCHOOL={school}')
        print("\nLinux/Mac:")
        print(f'export EDU_USERNAME="{username}"')
        print(f'export EDU_PASSWORD="{password}"')
        print(f'export EDU_SCHOOL="{school}"')
        print("\n⚠️ 注意：请将这些命令添加到您的shell配置文件中以持久化设置")
    
    def clear_cached_credentials(self) -> None:
        """清除缓存的凭据"""
        self._cached_credentials.clear()
        print("✓ 已清除缓存的凭据")
    
    def validate_credentials(self, username: str, password: str, school: str) -> bool:
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

def get_login_credentials(force_input: bool = False) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    获取登录凭据的便捷函数
    
    Args:
        force_input: 强制使用交互式输入
        
    Returns:
        (username, password, school) 元组
    """
    return credentials_manager.get_credentials(force_input)

def clear_credentials() -> None:
    """清除缓存凭据的便捷函数"""
    credentials_manager.clear_cached_credentials()


if __name__ == "__main__":
    # 测试凭据管理器
    print("🔐 凭据管理器测试")
    username, password, school = get_login_credentials(force_input=True)
    print(f"获取到凭据: 用户名={username}, 学校={school}")
