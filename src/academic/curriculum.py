#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
课程表获取和解析模块

从教务系统获取课程表数据并解析为结构化格式
"""

import re
import json
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path
from bs4 import BeautifulSoup

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.auth.session_manager import get_session, ensure_logged_in


class CurriculumParser:
    """课程表解析器"""

    def __init__(self):
        self.base_url = 'http://oa.csmu.edu.cn:8099/jsxsd/xskb/xskb_list.do'
        self.json_file = "curriculum.json"

        # 时间段映射（根据实际HTML结构调整）
        self.time_slots = {
            '12': '第1-2节',
            '34': '第3-4节',
            '56': '第5-6节',
            '78': '第7-8节',
            '910': '第9-10节',
            '1112': '第11-12节'
        }

        # 星期映射
        self.weekdays = {
            1: '星期一',
            2: '星期二',
            3: '星期三',
            4: '星期四',
            5: '星期五',
            6: '星期六',
            7: '星期日'
        }

    def fetch_curriculum(self, zc: str = "", xnxq01id: str = "") -> List[Dict[str, Any]]:
        """
        获取课程表数据

        Args:
            zc: 周次，为空表示所有周次
            xnxq01id: 学年学期ID（如2025-2026-1），为空表示当前学期

        Returns:
            课程表数据列表
        """
        try:
            # 确保已登录
            if not ensure_logged_in():
                print("❌ 登录失败，无法获取课程表数据")
                return []

            # 使用全局session发送请求
            session = get_session()
            print("🔍 正在获取课程表数据...")
            print(f"📋 参数: 周次={zc or '所有周次'}, 学期={xnxq01id or '当前学期'}")

            # 准备POST参数（固定其他参数）
            post_data = {
                'cj0701id': '',      # 固定为空，表示当前用户班级
                'zc': zc,            # 周次参数
                'demo': '',          # 固定为空，非演示模式
                'xnxq01id': xnxq01id, # 学期参数
                'sfFD': '1'          # 固定为1，表示放大方法
            }

            # 发送POST请求获取课程表页面
            response = session.post(self.base_url, data=post_data, timeout=30)
            response.raise_for_status()

            # 保存HTML源码到同目录
            html_file = Path(__file__).parent / "curriculum_source.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"✅ HTML源码已保存到: {html_file}")

            # 解析HTML获取课程表
            curriculum_data = self._parse_html_table(response.text)

            # 保存到JSON文件
            if curriculum_data:
                self._save_to_json(curriculum_data)
                print(f"✅ 课程表数据已保存到: {self.json_file}")

            return curriculum_data

        except Exception as e:
            print(f"❌ 获取课程表失败: {e}")
            return []

    def _parse_html_table(self, html_content: str) -> List[Dict[str, Any]]:
        """
        解析HTML课程表

        Args:
            html_content: HTML内容

        Returns:
            解析后的课程表数据列表
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # 查找课程表表格
            table = soup.find('table', {'id': 'kbtable'})
            if not table:
                # 尝试其他可能的表格标识
                table = soup.find('table', class_='kbcontent')
                if not table:
                    print("❌ 未找到课程表表格")
                    return []

            print("✅ 找到课程表表格，开始解析...")

            curriculum_data = []

            # 获取所有详细课程内容div（包含老师信息的隐藏div）
            course_divs = soup.find_all('div', class_='kbcontent')

            print(f"🔍 找到 {len(course_divs)} 个课程div")

            for div in course_divs:
                try:
                    # 提取div的id来确定时间和星期
                    div_id = div.get('id', '')
                    if not div_id:
                        continue

                    print(f"📋 解析div: {div_id}")

                    # 解析课程信息
                    course_info = self._parse_course_div(div, div_id)
                    if course_info:
                        curriculum_data.extend(course_info)
                        print(f"✅ 解析出 {len(course_info)} 条课程记录")

                except Exception as e:
                    print(f"⚠️ 解析课程div时出错: {e}")
                    continue

            print(f"✅ 成功解析 {len(curriculum_data)} 条课程记录")
            return curriculum_data

        except Exception as e:
            print(f"❌ 解析HTML课程表失败: {e}")
            return []

    def _parse_course_div(self, div, div_id: str) -> List[Dict[str, Any]]:
        """
        解析单个课程div

        Args:
            div: BeautifulSoup div元素
            div_id: div的id属性

        Returns:
            课程信息列表
        """
        try:
            # 解析div_id获取时间和星期信息
            # 格式: 时间段ID-星期-序号，如 "1FB6E9938A9149589F498C24834EB7E3-1-2"
            id_parts = div_id.split('-')
            if len(id_parts) < 3:
                print(f"⚠️ div_id格式不正确: {div_id}")
                return []

            weekday = int(id_parts[1]) if id_parts[1].isdigit() else 0  # 星期

            if weekday < 1 or weekday > 7:
                print(f"⚠️ 星期数不正确: {weekday}")
                return []

            # 获取div的HTML内容（保留标签）
            div_html = str(div)

            # 解析课程内容
            courses = self._parse_course_content_html(div_html, div_id, weekday)
            return courses

        except Exception as e:
            print(f"❌ 解析课程div失败: {e}")
            return []

    def _parse_course_content_html(self, div_html: str, div_id: str, weekday: int) -> List[Dict[str, Any]]:
        """
        解析课程内容HTML

        Args:
            div_html: div的HTML内容
            div_id: div的id
            weekday: 星期几

        Returns:
            课程信息列表
        """
        courses = []

        try:
            # 检查是否为空课程槽（只包含&nbsp;）
            if div_html.strip() == '&nbsp;' or not div_html.strip():
                print(f"📅 时间槽 {div_id} 无课程安排（空时间槽）")
                return []

            # 使用BeautifulSoup解析div内容
            div_soup = BeautifulSoup(div_html, 'html.parser')

            # 检查解析后的文本内容是否为空
            div_text = div_soup.get_text(strip=True)
            if not div_text or div_text == '':
                print(f"📅 时间槽 {div_id} 无课程安排（空内容）")
                return []

            # 🎯 基于HTML标签结构直接提取信息
            course_name = ''
            teacher = ''
            time_info = ''
            classroom = ''

            # 1. 提取课程名称（第一个<br>之前的纯文本）
            course_name = ''

            # 调试：打印div的内容结构
            print(f"🔍 调试div内容: {[str(elem)[:50] for elem in div_soup.contents]}")

            # 方法1: 查找第一个<br>标签之前的文本
            first_br = div_soup.find('br')
            if first_br:
                # 获取第一个<br>之前的所有文本内容
                for i, element in enumerate(div_soup.contents):
                    if element == first_br:
                        break
                    # 检查是否是文本节点
                    from bs4 import NavigableString
                    if isinstance(element, NavigableString) and not isinstance(element, type(first_br)):
                        course_name += str(element).strip()
                        print(f"🔍 找到文本节点 {i}: '{str(element).strip()}'")
                course_name = course_name.strip()

            # 方法2: 如果方法1失败，直接从HTML中提取
            if not course_name:
                # 使用正则表达式直接从HTML中提取第一个<br>之前的内容
                import re
                match = re.search(r'>([^<]+)<br', div_html)
                if match:
                    course_name = match.group(1).strip()
                    print(f"🔍 正则提取课程名称: '{course_name}'")

            print(f"🔍 最终课程名称: '{course_name}' (元素数量: {len(div_soup.contents)})")

            # 2. 提取教师信息（直接从font标签获取）
            teacher = ''
            teacher_font = div_soup.find('font', title='老师')
            if teacher_font:
                teacher = teacher_font.get_text(strip=True)

            # 3. 提取时间信息（title='周次(节次)'的font标签）
            time_font = div_soup.find('font', title='周次(节次)')
            if time_font:
                time_info = time_font.get_text(strip=True)

            # 4. 提取教室信息（title='教室'的font标签）
            classroom_font = div_soup.find('font', title='教室')
            if classroom_font:
                classroom = classroom_font.get_text(strip=True)

            print(f"✅ 基于标签解析 - 课程: {course_name}, 教师: {teacher}, 教室: {classroom}, 时间: {time_info}")

            # 如果基于标签的方法成功提取了信息，直接使用
            if course_name and time_info:
                # 解析时间信息
                week_info, period_info = self._parse_time_info(time_info)

                # 确定时间段
                time_slot = self._determine_time_slot(div_id, period_info)

                # 为每个周次创建课程记录
                for week in week_info:
                    course = {
                        'kcmc': course_name,           # 课程名称
                        'teaxms': teacher,             # 任课教师
                        'jxcdmc': classroom,           # 教室
                        'xq': weekday,                 # 星期几
                        'xqmc': self.weekdays.get(weekday, f'星期{weekday}'),  # 星期名称
                        'zc': week,                    # 周次
                        'jcdm': period_info,           # 节次
                        'jcmc': self._get_time_name(period_info),  # 节次名称
                        'time_slot': time_slot,        # 时间段
                        'div_id': div_id               # 原始div_id
                    }
                    courses.append(course)

                return courses

            # 如果基于标签的方法没有找到课程，尝试文本解析方法
            print("📅 标签解析未找到课程，尝试文本解析方法")

            # 获取纯文本内容
            div_text = div_soup.get_text()

            # 按分隔符分割多个课程
            course_blocks = div_text.split('---------------------')

            for block in course_blocks:
                block = block.strip()
                if not block:
                    continue

                print(f"📝 解析课程块: {block[:50]}...")

                # 按行分割课程信息
                lines = [line.strip() for line in block.split('\n') if line.strip()]

                if len(lines) >= 1:
                    # 解析第一行，可能包含课程名称和教师
                    first_line = lines[0]

                    # 分离课程名称和教师（通常课程名称后跟教师名）
                    course_name = ''
                    teacher = ''

                    # 查找时间信息和教室
                    time_info = ''
                    classroom = ''

                    # 解析所有行
                    full_text = ' '.join(lines)
                    print(f"🔍 完整文本: {full_text}")

                    # 🎯 改进的解析逻辑
                    # 1. 提取时间信息（包含周次和节次）
                    time_match = re.search(r'(\d+(?:[-,]\d+)*)\(周\)\[([^\]]+)\]', full_text)
                    if time_match:
                        week_part = time_match.group(1)
                        period_part = time_match.group(2)
                        time_info = f"{week_part}(周)[{period_part}]"
                        print(f"✅ 找到时间信息: {time_info}")

                    # 2. 提取课程名称（更精确的模式）
                    course_name = ''
                    if time_info:
                        text_before_time = full_text.split(time_info)[0]
                    else:
                        text_before_time = full_text

                    # 🎯 更智能的课程名称提取
                    # 先尝试从时间信息前提取完整的课程名称
                    if time_info:
                        # 移除时间信息，剩下的前半部分包含课程名称和教师
                        course_teacher_text = text_before_time.strip()

                        # 尝试不同的分离策略
                        # 🎯 智能课程名称提取策略（通用版）
                        course_name = self._extract_course_name_smart(course_teacher_text)

                    print(f"🔍 课程名称提取结果: '{course_name}' (来源: '{text_before_time[:50]}...')")

                    # 3. 提取教师名称（在课程名称之后，时间信息之前）
                    teacher = ''
                    if course_name and time_info:
                        # 从完整文本中移除课程名称和时间信息，剩下的就是教师和教室
                        remaining_text = text_before_time.replace(course_name, '', 1).strip()

                        # 教师名称模式（包含职称的优先）
                        teacher_patterns = [
                            r'^([^0-9\[\(]*?(?:讲师|教授|护师|副教授)(?:\（[^）]*\）)?)',  # 包含职称
                            r'^([^0-9\[\(]{2,8}?)(?=\d|\s|$)',  # 简单姓名
                        ]

                        for pattern in teacher_patterns:
                            teacher_match = re.search(pattern, remaining_text)
                            if teacher_match:
                                teacher = teacher_match.group(1).strip()
                                # 清理教师名称
                                teacher = re.sub(r'[,，].*$', '', teacher)  # 移除逗号后的内容
                                teacher = re.sub(r'\]', '', teacher)  # 移除残留的]符号
                                break

                    # 4. 提取教室信息（在时间信息之后）
                    classroom = ''
                    if time_info:
                        text_after_time = full_text.split(time_info)[-1].strip()

                        # 教室名称模式
                        classroom_patterns = [
                            r'(护理楼\d+)',                    # 护理楼+数字
                            r'(实验楼\d+)',                    # 实验楼+数字
                            r'(临床技能中心\d+)',              # 临床技能中心+数字
                            r'(长沙医学院第一附属医院)',        # 附属医院
                            r'(第一附属医院[^0-9\[\(]*)',      # 附属医院相关
                            r'([^0-9\[\(]*(?:楼|室|院|中心)\d*)', # 通用地点模式
                        ]

                        for pattern in classroom_patterns:
                            classroom_match = re.search(pattern, text_after_time)
                            if classroom_match:
                                classroom = classroom_match.group(1).strip()
                                break

                    print(f"📝 优化解析结果 - 课程: {course_name}, 教师: {teacher}, 教室: {classroom}, 时间: {time_info}")

                    # 如果没有找到教师，尝试从原始HTML中提取
                    if not teacher:
                        teacher_match = re.search(r'<font title=[\'"]老师[\'"]>(.*?)</font>', div_html)
                        if teacher_match:
                            teacher = teacher_match.group(1)

                    # 如果没有找到教室，尝试从原始HTML中提取
                    if not classroom:
                        classroom_match = re.search(r'<font title=[\'"]教室[\'"]>(.*?)</font>', div_html)
                        if classroom_match:
                            classroom = classroom_match.group(1)

                    # 解析时间信息
                    week_info, period_info = self._parse_time_info(time_info)

                    # 确定时间段
                    time_slot = self._determine_time_slot(div_id, period_info)

                    # 为每个周次创建课程记录
                    for week in week_info:
                        course = {
                            'kcmc': course_name,           # 课程名称
                            'teaxms': teacher,             # 任课教师
                            'jxcdmc': classroom,           # 教室
                            'xq': weekday,                 # 星期几
                            'xqmc': self.weekdays.get(weekday, f'星期{weekday}'),  # 星期名称
                            'zc': week,                    # 周次
                            'jcdm': period_info,           # 节次
                            'jcmc': self._get_time_name(period_info),  # 节次名称
                            'time_slot': time_slot,        # 时间段
                            'div_id': div_id               # 原始div_id
                        }
                        courses.append(course)

        except Exception as e:
            print(f"❌ 解析课程内容HTML失败: {e}")

        return courses

    def _parse_multiple_courses_html(self, div_html: str, div_id: str, weekday: int) -> List[Dict[str, Any]]:
        """
        解析包含多个课程的div（用---------------------分隔）

        Args:
            div_html: div的HTML内容
            div_id: div的id
            weekday: 星期几

        Returns:
            课程信息列表
        """
        courses = []

        try:
            # 按分隔符分割HTML
            course_blocks = div_html.split('---------------------')

            for i, block in enumerate(course_blocks):
                block = block.strip()
                if not block:
                    continue

                print(f"📋 处理多课程块 {i+1}: {block[:100]}...")

                # 解析每个课程块
                block_soup = BeautifulSoup(block, 'html.parser')

                course_name = ''
                teacher = ''
                time_info = ''
                classroom = ''

                # 提取课程名称（第一个<br>之前的文本）
                first_br = block_soup.find('br')
                if first_br:
                    for element in block_soup.contents:
                        if element == first_br:
                            break
                        if isinstance(element, str):
                            course_name += element.strip()
                    course_name = course_name.strip()

                # 提取教师信息
                teacher_font = block_soup.find('font', title='老师')
                if teacher_font:
                    teacher = teacher_font.get_text(strip=True)

                # 提取时间信息
                time_font = block_soup.find('font', title='周次(节次)')
                if time_font:
                    time_info = time_font.get_text(strip=True)

                # 提取教室信息
                classroom_font = block_soup.find('font', title='教室')
                if classroom_font:
                    classroom = classroom_font.get_text(strip=True)

                print(f"✅ 多课程块解析 - 课程: '{course_name}', 教师: '{teacher}', 教室: '{classroom}', 时间: '{time_info}'")

                # 如果成功提取了基本信息，创建课程记录
                if course_name and time_info:
                    # 解析时间信息
                    week_info, period_info = self._parse_time_info(time_info)

                    # 确定时间段
                    time_slot = self._determine_time_slot(div_id, period_info)

                    # 为每个周次创建课程记录
                    for week in week_info:
                        course = {
                            'kcmc': course_name,           # 课程名称
                            'teaxms': teacher,             # 任课教师
                            'jxcdmc': classroom,           # 教室
                            'xq': weekday,                 # 星期几
                            'xqmc': self.weekdays.get(weekday, f'星期{weekday}'),  # 星期名称
                            'zc': week,                    # 周次
                            'jcdm': period_info,           # 节次
                            'jcmc': self._get_time_name(period_info),  # 节次名称
                            'time_slot': time_slot,        # 时间段
                            'div_id': div_id               # 原始div_id
                        }
                        courses.append(course)

            return courses

        except Exception as e:
            print(f"❌ 解析多课程失败: {e}")
            return []

    def _extract_course_name_smart(self, text: str) -> str:
        """
        智能提取课程名称的通用方法

        Args:
            text: 包含课程名称和教师的混合文本

        Returns:
            提取出的课程名称
        """
        text = text.strip()
        if not text:
            return ''

        # 策略1: 基于教师职称分割
        # 查找明确的教师职称标识
        teacher_titles = r'(?:讲师|教授|护师|副教授|实验师)(?:\（[^）]*\）)?'
        teacher_match = re.search(rf'([^0-9]*?)([A-Za-z\u4e00-\u9fff]{{2,4}}{teacher_titles})', text)
        if teacher_match:
            potential_name = teacher_match.group(1).strip()
            if len(potential_name) >= 2 and not re.search(teacher_titles, potential_name):
                return potential_name

        # 策略2: 基于常见的中文姓名模式分割
        # 查找2-4个中文字符的姓名（在数字或周次前）
        name_patterns = [
            r'^(.*?)([A-Za-z\u4e00-\u9fff]{2,4})(?=\d+(?:[-,]\d+)*\(周\))',  # 姓名+周次模式
            r'^(.*?)([A-Za-z\u4e00-\u9fff]{2,4})(?=\d)',                     # 姓名+数字模式
        ]

        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                potential_name = match.group(1).strip()
                teacher_name = match.group(2).strip()

                # 验证提取的课程名称合理性
                if (len(potential_name) >= 2 and
                    len(teacher_name) >= 2 and
                    not re.search(r'^\d', potential_name) and  # 不以数字开头
                    not re.search(teacher_titles, potential_name)):  # 不包含职称
                    return potential_name

        # 策略3: 基于课程名称的语义特征
        # 查找以常见课程结尾词结束的部分
        course_endings = [
            r'(.*?护理学(?:\[实践\])?)',     # 护理学类
            r'(.*?(?:学|教育|指导|规划|原理|概论|政策|管理学|生物学|实验学)(?:\[实践\])?)',  # 通用学科结尾
            r'(.*?(?:\（[^）]*\）)(?:\[实践\])?)',  # 带括号的课程名称
        ]

        for pattern in course_endings:
            match = re.match(pattern, text)
            if match:
                potential_name = match.group(1).strip()
                # 验证不包含明显的教师信息
                if (len(potential_name) >= 2 and
                    not re.search(teacher_titles, potential_name)):
                    return potential_name

        # 策略4: 基于中文字符连续性
        # 提取开头的连续中文字符、括号、方括号
        chinese_match = re.match(r'^([\u4e00-\u9fff（）\[\]]+)', text)
        if chinese_match:
            potential_name = chinese_match.group(1).strip()
            if len(potential_name) >= 2:
                return potential_name

        # 策略5: 最后的备选方案
        # 如果以上都失败，尝试提取前面的非数字部分
        fallback_match = re.match(r'^([^0-9]+)', text)
        if fallback_match:
            potential_name = fallback_match.group(1).strip()
            # 移除可能的教师名称后缀
            potential_name = re.sub(rf'{teacher_titles}.*$', '', potential_name).strip()
            if len(potential_name) >= 2:
                return potential_name

        return text  # 如果所有策略都失败，返回原文本

    def _determine_time_slot(self, div_id: str, period_info: str) -> str:
        """根据div_id和节次信息确定时间段"""
        # 从课程表的行位置推断时间段
        # 这需要根据实际的表格结构来调整
        if '01-02' in period_info:
            return '12'
        elif '03-04' in period_info:
            return '34'
        elif '05-06' in period_info:
            return '56'
        elif '07-08' in period_info:
            return '78'
        elif '09-10' in period_info:
            return '910'
        elif '11-12' in period_info:
            return '1112'
        else:
            return '12'  # 默认

    def _get_time_name(self, period_info: str) -> str:
        """根据节次信息获取时间名称"""
        if '01-02' in period_info:
            return '第1-2节'
        elif '03-04' in period_info:
            return '第3-4节'
        elif '05-06' in period_info:
            return '第5-6节'
        elif '07-08' in period_info:
            return '第7-8节'
        elif '09-10' in period_info:
            return '第9-10节'
        elif '11-12' in period_info:
            return '第11-12节'
        else:
            return period_info or '未知时间'

    def _parse_time_info(self, time_info: str) -> tuple:
        """
        解析时间信息（周次和节次）

        Args:
            time_info: 时间信息字符串，如 "1-15(周)[01-02节]"

        Returns:
            (周次列表, 节次信息)
        """
        weeks = []
        periods = ''

        try:
            print(f"🔍 解析时间信息: {time_info}")

            # 分离周次和节次信息
            if '(周)' in time_info:
                parts = time_info.split('(周)')
                week_part = parts[0]

                # 解析节次信息（在方括号中）
                if len(parts) > 1 and '[' in parts[1] and ']' in parts[1]:
                    period_match = re.search(r'\[(.*?)\]', parts[1])
                    if period_match:
                        periods = period_match.group(1)

                # 解析周次
                week_ranges = week_part.split(',')
                for week_range in week_ranges:
                    week_range = week_range.strip()
                    if '-' in week_range:
                        # 连续周次，如 "1-16"
                        try:
                            start, end = map(int, week_range.split('-'))
                            weeks.extend(list(range(start, end + 1)))
                        except ValueError:
                            print(f"⚠️ 无法解析周次范围: {week_range}")
                    elif week_range.isdigit():
                        # 单个周次
                        weeks.append(int(week_range))

                # 去重并排序
                weeks = sorted(list(set(weeks)))

            print(f"✅ 解析结果 - 周次: {weeks}, 节次: {periods}")

        except Exception as e:
            print(f"⚠️ 解析时间信息失败: {e}")
            weeks = [1]  # 默认第1周
            periods = ''

        return weeks, periods

    def _save_to_json(self, data: List[Dict[str, Any]]) -> None:
        """保存数据到JSON文件"""
        try:
            # 确保data目录存在
            data_dir = Path(__file__).parent.parent.parent / "data"
            data_dir.mkdir(exist_ok=True)

            json_path = data_dir / self.json_file
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"❌ 保存JSON文件失败: {e}")


def curriculum(zc: str = "", xnxq01id: str = "") -> List[Dict[str, Any]]:
    """
    获取课程表信息的主函数

    Args:
        zc: 周次，为空表示所有周次
        xnxq01id: 学年学期ID（如2025-2026-1），为空表示当前学期

    Returns:
        List[Dict[str, Any]]: 课程表数据列表
    """
    parser = CurriculumParser()
    return parser.fetch_curriculum(zc, xnxq01id)


if __name__ == "__main__":
    import argparse

    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='获取课程表数据')
    parser.add_argument('--zc', default='', help='周次，为空表示所有周次')
    parser.add_argument('--xnxq01id', default='', help='学年学期ID（如2025-2026-1），为空表示当前学期')

    # 解析命令行参数
    args = parser.parse_args()

    # 获取课程表数据
    results = curriculum(
        zc=args.zc,
        xnxq01id=args.xnxq01id
    )

    print(f"成功获取 {len(results)} 条课程记录")
