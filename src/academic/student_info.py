#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生信息查询模块

获取学生的详细个人信息和学籍信息
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Any, Optional

def get_student_info(session: requests.Session = None) -> Optional[Dict[str, Any]]:
    """
    获取学生个人信息

    Args:
        session: 已登录的session对象，如果为None则使用session_manager

    Returns:
        学生信息字典，包含基本信息、学籍信息等
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
        url = 'http://oa.csmu.edu.cn:8099/jsxsd/grxx/xsxx'
        print(f"🌐 正在访问学生信息页面: {url}")
        response = session.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ 获取学生信息失败: {response.status_code}")
            return None
        
        print(f"✅ 成功获取页面内容: {len(response.text)} 字符")
        
        # 保存HTML源码用于调试
        from pathlib import Path
        source_file = Path(__file__).parent / "student_info_source.html"
        with open(source_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"✅ HTML源码已保存到: {source_file}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 解析学生信息
        student_info = {}
        
        # 查找页面标题
        title = soup.find('title')
        if title:
            student_info['页面标题'] = title.get_text(strip=True)
            print(f"📄 页面标题: {student_info['页面标题']}")
        
        # 专门解析学籍卡片表格
        main_table = soup.find('table', id='xjkpTable')
        if main_table:
            print("📊 找到学籍卡片主表格，开始详细解析...")
            parsed_info = parse_student_card_table(main_table)
            student_info.update(parsed_info)
        else:
            print("⚠️ 未找到学籍卡片主表格")
        
        # 查找学生照片
        img_tags = soup.find_all('img')
        for img in img_tags:
            src = img.get('src', '')
            alt = img.get('alt', '')
            if 'xszpLoad' in src or '照片' in alt:
                student_info['学生照片URL'] = src
                print(f"✅ 找到学生照片: {src}")
                break
        
        print(f"\n✅ 总共解析出 {len(student_info)} 项学生信息")
        return student_info
        
    except Exception as e:
        print(f"❌ 获取学生信息时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def parse_student_card_table(table) -> Dict[str, Any]:
    """
    专门解析学籍卡片表格
    
    Args:
        table: BeautifulSoup表格对象
        
    Returns:
        解析出的学生信息字典
    """
    info = {}
    rows = table.find_all('tr')
    print(f"📋 学籍卡片表格共 {len(rows)} 行")
    
    for row_idx, row in enumerate(rows):
        cells = row.find_all('td')
        
        # 跳过空行
        if not cells:
            continue
        
        # 解析院系、专业等基本信息行 (第3行，索引为2)
        if row_idx == 2:
            for cell in cells:
                text = cell.get_text(strip=True)
                if '：' in text:
                    parts = text.split('：')
                    if len(parts) == 2:
                        key, value = parts
                        info[key] = value
                        print(f"   基本信息: {key} = {value}")
        
        # 解析详细信息行（有边框的行）
        elif 'border:1px solid black' in str(row):
            cell_texts = []
            for cell in cells:
                # 跳过包含照片的单元格或跨行单元格
                if cell.find('img') or 'rowspan' in str(cell):
                    continue
                text = cell.get_text(strip=True).replace('\xa0', '').replace('&nbsp;', '')
                cell_texts.append(text)

            # 处理键值对 - 更智能的配对
            i = 0
            while i < len(cell_texts):
                if i + 1 < len(cell_texts):
                    key = cell_texts[i]
                    value = cell_texts[i + 1]

                    # 只有当key不为空且value不为空且不相等时才记录
                    if key and value and key != value and len(key) < 20:  # 避免长文本作为key
                        info[key] = value
                        print(f"   详细信息: {key} = {value}")
                        i += 2
                    else:
                        i += 1
                else:
                    i += 1
    
    return info

def format_student_info(info: Dict[str, Any]) -> str:
    """格式化学生信息输出"""
    if not info:
        return "❌ 无学生信息"
    
    output = ["📋 学生信息"]
    output.append("=" * 40)
    
    # 重要信息优先显示
    important_keys = ['姓名', '学号', '性别', '专业', '班级', '年级', '学院', '院系']
    
    for key in important_keys:
        if key in info:
            output.append(f"{key}: {info[key]}")
    
    output.append("-" * 40)
    
    # 其他信息
    for key, value in info.items():
        if key not in important_keys and key != '学生照片URL' and key != '页面标题':
            output.append(f"{key}: {value}")
    
    # 照片信息
    if '学生照片URL' in info:
        output.append("-" * 40)
        output.append(f"学生照片: {info['学生照片URL']}")
    
    return "\n".join(output)

if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # 添加项目根目录到Python路径
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    from src.auth.session_manager import session_manager
    
    if session_manager.is_logged_in:
        info = get_student_info(session_manager.session)
        print(format_student_info(info))
    else:
        print("❌ 请先登录")
