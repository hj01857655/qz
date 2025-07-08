#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教务系统主入口文件

功能：
1. 登录验证
2. 获取成绩信息
3. 获取课程表信息
4. 启动GUI界面

使用方法：
    python main.py [--gui] [--cli]

    --gui: 启动图形界面（默认）
    --cli: 使用命令行界面
"""

import sys
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.auth.login import login, isValid, getname
from src.academic.achievement import achievement
from src.academic.curriculum import curriculum
from src.models.data import data


def cli_mode():
    """命令行模式"""
    print("=" * 50)
    print("教务系统 - 命令行模式")
    print("=" * 50)

    try:
        # 检查登录状态
        session = isValid()
        if not session:
            print("登录失败，请检查网络连接或重新配置登录信息")
            return

        print(f"登录成功！用户：{getname()}")

        while True:
            print("\n请选择功能：")
            print("1. 获取成绩信息")
            print("2. 获取课程表信息")
            print("3. 获取所有数据")
            print("0. 退出")

            choice = input("请输入选择 (0-3): ").strip()

            if choice == '0':
                print("再见！")
                break
            elif choice == '1':
                print("正在获取成绩信息...")
                achievements = achievement()
                print(f"成功获取 {len(achievements)} 条成绩记录")

                # 显示前5条记录
                for i, record in enumerate(achievements[:5]):
                    print(f"{i+1}. {record.get('kcmc', 'N/A')} - {record.get('kczcj', 'N/A')}")

                if len(achievements) > 5:
                    print(f"... 还有 {len(achievements) - 5} 条记录")

            elif choice == '2':
                print("正在获取课程表信息...")
                courses = curriculum()
                print(f"成功获取课程表信息")

            elif choice == '3':
                print("正在获取所有数据...")
                # 这里需要用户名和密码参数，暂时跳过
                print("此功能需要在GUI模式下使用")

            else:
                print("无效选择，请重新输入")

    except Exception as e:
        print(f"运行出错：{e}")
        print("请检查网络连接和配置文件")


def gui_mode():
    """图形界面模式"""
    try:
        from gui.gui import create_login_gui
        print("启动图形界面...")
        create_login_gui()
    except ImportError as e:
        print(f"无法启动图形界面：{e}")
        print("请安装必要的GUI依赖包：pip install tkinter")
        print("或使用命令行模式：python main.py --cli")
    except Exception as e:
        print(f"GUI启动失败：{e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="教务系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  python main.py          # 启动GUI界面（默认）
  python main.py --gui     # 启动GUI界面
  python main.py --cli     # 使用命令行界面
        """
    )

    parser.add_argument(
        '--gui',
        action='store_true',
        help='启动图形用户界面（默认）'
    )

    parser.add_argument(
        '--cli',
        action='store_true',
        help='使用命令行界面'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='教务系统 v1.0.0'
    )

    args = parser.parse_args()

    # 如果没有指定模式，默认使用GUI
    if not args.cli and not args.gui:
        args.gui = True

    # 如果同时指定了两种模式，优先使用CLI
    if args.cli and args.gui:
        args.gui = False

    try:
        if args.cli:
            cli_mode()
        else:
            gui_mode()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
