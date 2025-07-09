#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
考试安排查询模块

获取学生的考试安排信息
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Any, Optional

def get_exam_schedule(session: requests.Session = None) -> Optional[List[Dict[str, Any]]]:
    """
    获取考试安排

    Args:
        session: 已登录的session对象，如果为None则使用session_manager

    Returns:
        考试安排列表
    """
    try:
        # 如果没有提供session，使用session_manager
        if session is None:
            from src.auth.session_manager import session_manager
            if not session_manager.ensure_logged_in():
                print("❌ 无法获取有效的登录session")
                return None
            session = session_manager.session
        url = 'http://oa.csmu.edu.cn:8099/jsxsd/xsks/xsksap_list'
        response = session.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ 获取考试安排失败: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找考试安排表格
        exams = []
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            headers = []
            
            # 获取表头
            if rows:
                header_row = rows[0]
                headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
            
            # 获取数据行
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= len(headers):
                    exam_info = {}
                    for i, cell in enumerate(cells[:len(headers)]):
                        if i < len(headers):
                            exam_info[headers[i]] = cell.get_text(strip=True)
                    
                    if exam_info:
                        exams.append(exam_info)
        
        return exams
        
    except Exception as e:
        print(f"❌ 获取考试安排时发生错误: {e}")
        return None

def format_exam_schedule(exams: List[Dict[str, Any]]) -> str:
    """格式化考试安排输出"""
    if not exams:
        return "📅 暂无考试安排"
    
    output = ["📅 考试安排"]
    output.append("=" * 60)
    
    for i, exam in enumerate(exams, 1):
        output.append(f"\n📝 考试 {i}")
        output.append("-" * 30)
        
        for key, value in exam.items():
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
        exams = get_exam_schedule(session_manager.session)
        print(format_exam_schedule(exams))
    else:
        print("❌ 请先登录")
