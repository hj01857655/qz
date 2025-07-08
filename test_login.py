#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录功能测试脚本

使用方法：
1. 直接运行，会提示输入凭据
2. 设置环境变量后运行
3. 创建配置文件后运行

注意：此文件仅用于测试，不要提交到Git！
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.auth.credentials import get_login_credentials
from src.auth.login import login, getname
from src.academic.achievement import achievement


def test_login():
    """测试登录功能"""
    print("🧪 开始测试登录功能")
    print("=" * 50)
    
    try:
        # 获取凭据
        username, password, school = get_login_credentials()
        
        if not username or not password:
            print("❌ 未获取到有效凭据")
            return False
        
        print(f"📝 使用凭据: 用户名={username}, 学校={school}")
        
        # 尝试登录
        print("\n🔐 正在尝试登录...")
        session = login(username, password)
        
        if session:
            print("✅ 登录成功！")
            
            # 测试获取用户名
            print("\n👤 正在获取用户信息...")
            name = getname()
            if name:
                print(f"✅ 用户姓名: {name}")
            else:
                print("⚠️ 获取用户姓名失败")
            
            # 测试获取成绩
            print("\n📊 正在测试成绩查询...")
            try:
                achievements = achievement()
                if achievements:
                    print(f"✅ 成功获取 {len(achievements)} 条成绩记录")
                    # 显示前3条记录
                    for i, record in enumerate(achievements[:3]):
                        course_name = record.get('kcmc', 'N/A')
                        grade = record.get('kczcj', 'N/A')
                        print(f"   {i+1}. {course_name} - {grade}")
                    if len(achievements) > 3:
                        print(f"   ... 还有 {len(achievements) - 3} 条记录")
                else:
                    print("⚠️ 未获取到成绩数据")
            except Exception as e:
                print(f"❌ 成绩查询失败: {e}")
            
            return True
        else:
            print("❌ 登录失败")
            return False
            
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户取消测试")
        return False
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False


def main():
    """主函数"""
    print("🔐 教务系统登录测试")
    print("=" * 50)
    print("此脚本将测试登录功能和基本数据获取")
    print("请确保您有有效的教务系统账号")
    print()
    
    # 显示凭据获取方式
    print("📋 凭据获取方式:")
    print("1. 环境变量 (EDU_USERNAME, EDU_PASSWORD, EDU_SCHOOL)")
    print("2. 配置文件 (config/config.json)")
    print("3. 交互式输入")
    print()
    
    input("按回车键开始测试...")
    print()
    
    success = test_login()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 测试完成！所有功能正常")
    else:
        print("⚠️ 测试失败，请检查凭据和网络连接")
    
    print("\n💡 提示:")
    print("- 如果登录失败，请检查用户名和密码")
    print("- 如果验证码识别失败，可以多试几次")
    print("- 确保网络可以访问教务系统")


if __name__ == "__main__":
    main()
