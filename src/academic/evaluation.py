#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
课程评价模块

学生评教功能
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional

def get_evaluation_list(session: requests.Session = None) -> Optional[List[Dict[str, Any]]]:
    """
    获取可评价的课程列表

    Args:
        session: 已登录的session对象，如果为None则使用session_manager

    Returns:
        可评价课程列表
    """
    try:
        # 如果没有提供session，使用session_manager
        if session is None:
            from src.auth.session_manager import session_manager
            if not session_manager.ensure_logged_in():
                print("❌ 无法获取有效的登录session")
                return None
            session = session_manager.session
        url = 'http://oa.csmu.edu.cn:8099/jsxsd/xspj/xspj_find.do'
        response = session.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ 获取评价列表失败: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 解析评价列表
        courses = []
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            headers = []
            
            if rows:
                header_row = rows[0]
                headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
            
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= len(headers):
                    course_info = {}
                    for i, cell in enumerate(cells[:len(headers)]):
                        if i < len(headers):
                            course_info[headers[i]] = cell.get_text(strip=True)
                    
                    if course_info:
                        courses.append(course_info)
        
        return courses
        
    except Exception as e:
        print(f"❌ 获取评价列表时发生错误: {e}")
        return None

def format_evaluation_list(courses: List[Dict[str, Any]]) -> str:
    """格式化评价列表输出"""
    if not courses:
        return "📊 暂无可评价课程"
    
    output = ["📊 课程评价"]
    output.append("=" * 60)
    
    for i, course in enumerate(courses, 1):
        output.append(f"\n📚 课程 {i}")
        output.append("-" * 30)
        
        for key, value in course.items():
            if value:
                output.append(f"{key}: {value}")
    
    return "\n".join(output)

if __name__ == "__main__":
    import sys
    from pathlib import Path

    # 添加项目根目录到Python路径
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

    from src.auth.session_manager import session_manager

    if session_manager.is_logged_in:
        courses = get_evaluation_list(session_manager.session)
        print(format_evaluation_list(courses))
    else:
        print("❌ 请先登录")
