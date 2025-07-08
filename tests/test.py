import re
import json
import requests
import sys
from pathlib import Path
from bs4 import BeautifulSoup

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.auth.login import isValid


class course:
    def __init__(self, name, teacher, zc, jc, classroom):
        self.name = name
        self.teacher = teacher
        self.zc = zc
        self.jc = jc
        self.classroom = classroom

    def to_dict(self):
        # 解析周次
        zc = self.parse_weeks(self.zc)
        return {
            'name': self.name,
            'teacher': self.teacher,
            'zc': zc,
            'jc': self.jc,
            'classroom': self.classroom
        }

    @staticmethod
    def parse_weeks(zc):
        # 去除(周)字符
        if zc.find('(周)') != -1:
            zc = zc.replace('(周)', '')
        weeks = []

        # 检查是否有逗号分隔的多个周次
        if ',' in zc:
            for range_str in zc.split(','):
                weeks.extend(parse_single_range_or_week(range_str))
        else:
            weeks = parse_single_range_or_week(zc)

        return weeks


def parse_single_range_or_week(range_str):
    # 检查是否为连续的周次
    if '-' in range_str:
        start, end = map(int, range_str.split('-'))
        return list(range(start, end + 1))
    else:
        # 如果不是连续周次，则直接返回单个周次
        return [int(range_str)]


def get_course_table():
    session = isValid()
    xskb_url = 'http://oa.csmu.edu.cn:8099/jsxsd/xskb/xskb_list.do'
    if session:
        try:
            res = session.get(xskb_url)
            res.raise_for_status()  # Raise an exception for HTTP errors
            return res.text
        except requests.exceptions.RequestException as e:
            print(f'Error retrieving course table: {e}')
    else:
        print('获取session失败')


def parse_course_table(html):
    soup = BeautifulSoup(html, 'html.parser')
    course_table = []
    # 拿到kbtable
    kbtable = soup.find('table', {'id': 'kbtable'})
    # print(kbtable)
    # 拿到课程行
    course_rows = kbtable.find_all('tr')
    # 避开第一个tr
    course_rows.pop(0)

    # 拿到课程行中的每一个td中的div.kbcontent
    for row in course_rows:
        course_tds = row.find_all('td')
        for td in course_tds:
            course_divs = td.find_all('div', {'class': 'kbcontent'})
            # print(course_divs)
            for div in course_divs:
                # print(len(div.get_text().split())==0,div.get_text().split())
                if len(div.get_text().split()) == 0:
                    course_table.append('')
                    # course('','','','','')
                    # print(div.get_text().replace(u'\xa0', u' ').strip(),'->')
                if div.get_text().find('---------------------') != -1:
                    # print(str(div).split('---------------------'))
                    div = str(div).split('---------------------')
                    for item in div:
                        if len(item.split()) != 0:
                            course_table.append(item)
                            # course('','','','','')
                #     divs=[[item] for item in div]
                else:
                    if len(div.get_text().split()) != 0:
                        # print(div,len(div.get_text().split()))
                        course_table.append(div)

            #

    # print(course_table)
    return course_table


def parse_course(html):
    soup = BeautifulSoup(html, 'html.parser')
    course_div = soup.find('div', {'class': 'kbcontent'})
    if course_div == None:
        course_name = soup.find('br').next_sibling.strip() if soup else ''
        course_teacher = soup.find('font', {'title': '老师'}).text.strip(
        ) if soup.find('font', {'title': '老师'}) else ''
        zc_jc = soup.find('font', {'title': '周次(节次)'}).text.strip(
        ) if soup.find('font', {'title': '周次(节次)'}) else ''
        zc, jc = zc_jc.split('[', 1)
        zc += ''
        jc = '['+jc
        classroom = soup.find('font', {'title': '教室'}).text.strip(
        ) if soup.find('font', {'title': '教室'}) else ''

        return course(course_name, course_teacher, zc, jc, classroom)

    else:
        course_teacher = course_div.find('font', {'title': '老师'}).text.strip(
        ) if course_div.find('font', {'title': '老师'}) else ''
        zc_jc = course_div.find('font', {'title': '周次(节次)'}).text.strip(
        ) if course_div.find('font', {'title': '周次(节次)'}) else ''

        zc, jc = zc_jc.split('[', 1)
        zc += ''
        jc = '['+jc
        classroom = course_div.find('font', {'title': '教室'}).text.strip(
        ) if course_div.find('font', {'title': '教室'}) else ''

        for child in course_div.find_all(True):
            child.decompose()
        course_name = course_div.get_text(strip=True).split(' ')[0]
        return course(course_name, course_teacher, zc, jc, classroom)


if __name__ == '__main__':
    html = get_course_table()
    for i in parse_course_table(html):
        # print(i)
        if i != '':
            Course = parse_course(str(i))
            print(json.dumps(Course.to_dict(), ensure_ascii=False))
            with open('course_table.json', 'a+', encoding='utf-8') as f:
                json.dump(Course.to_dict(), f, ensure_ascii=False)
