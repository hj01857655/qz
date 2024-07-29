import re, json
import requests
from login import isvaild
from bs4 import BeautifulSoup


# 定义分割课程信息的函数
def split_course_details(details_text):
    # 使用“----------------------”作为分割符
    all_courses = []
    if '----------------------'  in details_text:
        parts = details_text.split('----------------------')

        for part in parts:
            print(part)
            # all_courses.append(extract_course_details(part))
    # return all_courses



def curriculum():
    try:
        res = requests.get(
            'http://oa.csmu.edu.cn:8099/jsxsd/xskb/xskb_list.do',
            cookies=isvaild().cookies)
        data=res.content
        classes=[['' for j in range(14)] for i in range(7)]
        for i, f in enumerate(re.finditer(r'.*kbcontent1.*?>(.+?)<', data)):
            day  = i % 7
            time = i / 7
            classes[day][time] = f.group(1)
        for day in ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']:
            print (day.center(27)),
        i = 0
        for time in range(14):
            for day in range(7):
                cls = classes[day][time]
                if cls == '&nbsp;':
                    cls = ''
                print (cls.center(26)),
    except Exception as e:
        print(e)
        return []



if __name__ == '__main__':
    curriculum()
