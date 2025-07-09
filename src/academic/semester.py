#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学期管理模块

获取可用的学期列表和当前选中的学期
"""

import requests
from bs4 import BeautifulSoup
from typing import Tuple, List, Optional

def get_semester(session: requests.Session = None) -> Optional[Tuple[List[str], str, str]]:
    """
    获取学期信息

    Args:
        session: 已登录的session对象，如果为None则使用session_manager

    Returns:
        元组 (学期列表, 当前选中学期, 用户姓名)，失败返回None
    """
    try:
        # 如果没有提供session，使用session_manager
        if session is None:
            from src.auth.session_manager import session_manager
            if not session_manager.ensure_logged_in():
                print("❌ 无法获取有效的登录session")
                return None
            session = session_manager.session
            print("✅ 使用session_manager获取有效session")

        url = 'http://oa.csmu.edu.cn:8099/jsxsd/xskb/xskb_list.do'
        print(f"🌐 正在访问学期信息页面: {url}")

        response = session.get(url, timeout=10)

        if response.status_code != 200:
            print(f"❌ 获取学期信息失败: {response.status_code}")
            return None

        print(f"✅ 成功获取页面内容: {len(response.text)} 字符")

        soup = BeautifulSoup(response.text, 'html.parser')

        # 获取学期选择框
        options_select = soup.find('select', id='xnxq01id')
        if not options_select:
            print("❌ 未找到学期选择框")
            return None

        # 获取用户姓名
        name_div = soup.find('div', id='Top1_divLoginName')
        user_name = ""
        if name_div:
            user_name = name_div.get_text(strip=True).split('(')[0]
            print(f"👤 用户姓名: {user_name}")

        # 获取当前选中的学期
        selected_option = options_select.find('option', attrs={'selected': 'selected'})
        current_semester = ""
        if selected_option:
            current_semester = selected_option.get_text(strip=True)
            print(f"📅 当前学期: {current_semester}")

        # 获取所有可用学期
        all_options = options_select.find_all('option')
        semester_list = []
        for option in all_options:
            semester_text = option.get_text(strip=True)
            if semester_text:
                semester_list.append(semester_text)

        print(f"📋 可用学期: {len(semester_list)} 个")
        for i, semester in enumerate(semester_list):
            status = " (当前)" if semester == current_semester else ""
            print(f"   {i+1}. {semester}{status}")

        return semester_list, current_semester, user_name

    except Exception as e:
        print(f"❌ 获取学期信息时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    import sys
    from pathlib import Path

    # 添加项目根目录到Python路径
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

    # 测试学期信息获取
    result = get_semester()
    if result:
        semesters, current, name = result
        print(f"\n📊 学期信息获取成功:")
        print(f"   用户: {name}")
        print(f"   当前学期: {current}")
        print(f"   总学期数: {len(semesters)}")
    else:
        print("❌ 学期信息获取失败")
