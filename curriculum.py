import re, json
import requests
from login import isvaild
from bs4 import BeautifulSoup


def curriculum():
    try:
        res = requests.get(
            'http://oa.csmu.edu.cn:8099/jsxsd/xskb/xskb_list.do',
            cookies=isvaild().cookies).text
        # print(res)
        # a, _ = re.subn('\r', '', res)
        # a, _ = re.subn('\n', '', a)
        # a, _ = re.subn('\t', '', a)
        # tr = re.findall('<tr.*?>.*?</tr>', a)
        # tr.remove(tr[0])
        # print(tr)

        weekday = {
            '1': 'A003207A6624498F836BB24D19DD5A74',
            '2': 'A41B88AACE3649DEA0617C2B322A07A2',
            '3': 'E2ED1FEC1EDF48D3832EC07E45270721',
            '4': 'B674074118214BDDA88D9DACD9075C46',
            '5': '16FC051CF913479B9D3DBB1C1EBE4C9D',
            "6": '8CEDF435CAD644F3B7D2AF32B80F52D2',
            "7": 'A003207A6624498F836BB24D19DD5A74'
        }
        
        # print(weekday)
        # all = []
        # arr_all = []
        # for section in range(1, len(weekday) + 1):
        #     print(section)
        #     for day in range(1, 8):
        #         soup = BeautifulSoup(tr[section], 'html.parser')
        #         id = f"{weekday[str(section)]}-{day}-2"
        #         div = soup.find(attrs={'id': id})

        #         div = str(div).replace(
        #             f'<div class="kbcontent" id="{id}" style="display: none;">',
        #             '')
        #         div = div.replace('</div>', '')

        #         div = div.replace('---------------------', '\n')
        #         div = div.replace('<font title="老师">', '')
        #         div = div.replace('</font>', '')
        #         div = div.replace('<font title="周次(节次)">', '')
        #         div = div.replace('<font title="教室">', '')
        #         div = div.replace('</br>', '')
        #         div = div.replace('<br>', '<br/>')
        #         div = div.replace(' ', '')
        #         div=div.split('<br/>')
        #         # div = '\n'.join(div).split('\n')
        #         arr = []
        #         if div == ['\xa0']:
        #             div = ['']
        #             # print(div)
        #         if '\n' in div:
        #             # print(div.index('\n'),len(div),div)
        #             if div.index('\n') <4:
        #                 A=div[:4]
        #                 # print(A)
        #         # print(len(div),div)
        #         # elif len(div) > 16:

        #         # elif len(div)>12:
        #         #     pass
        #         # print(div[0:4],div[4:8],div[8:])

        #         # else:
        #         #     pass
        #         # print(div[0:4],div[4:8],div[8:12],div[12:])
        #         #     print(len(div),div)

        #         # else:
        #         #     # print(len(div),div)
        #         #     for i in range(len(div)):
        #         #         # div[i] = div[i].split('<br>')
        #         #         for j in div[i]:
        #         #             arr.append(j)

        #         # print(div)
        #         # print('\n',len(arr), arr,'\n')

        #         if len(arr) > 10:
        #             pass
        #             # print(arr)
        #             # n = len(arr) // 3

        #             # print(arr)
        #             # B = arr[n:2 * n]
        #             # C = arr[2 * n:]
        #             # get(A, day, all)
        #             # print(A,B)
        #             # week = B[2].split('(周)')[0]
        #             # print(week)
        #             # a = re.findall('(\d+)-(\d+)', week)
        #             # b = week.split(',')
        #             # c = re.findall('(\d{2})', B[2].split('(周)')[1])
        #             # print(''.join(c))
        #             # get(B, day, all)
        #             # get(C, day, all)
        #         elif len(arr) > 5:
        #             n = len(arr) // 2
        #             B = arr[:n]
        #             C = arr[n:]
        #             # get(B, day, all)
        #             # get(C, day, all)
        #         elif len(arr) > 2:
        #             pass
        #             # get(arr, day, all)
        #

        # return all
    except Exception as e:
        print(e)
        return []


def get(arr, day, all):
    week = arr[2].split('(周)')[0]
    a = re.findall('(\d+)-(\d+)', week)
    b = week.split(',')
    c = re.findall('(\d{2})', arr[2].split('(周)')[1])
    # print(''.join(c))
    if len(a) > 0:
        m = a[0]
        for h in range(int(m[0]), int(m[1]) + 1):
            if len(arr) == 3:
                obj = {
                    'jcdm': ''.join(c),  # 第几节课
                    'jxcdmc': '',  # 教室
                    'kcmc': arr[0],  # 课程名称
                    'teaxms': arr[1],  # 任课教师
                    'xq': day,  # 星期几
                    'zc': h  # 第几周
                }
                all.append(obj)
            else:
                obj = {
                    'jcdm': ''.join(c),  # 第几节课
                    'jxcdmc': arr[3],  # 教室
                    'kcmc': arr[0],  # 课程名称
                    'teaxms': arr[1],  # 任课教师
                    'xq': day,  # 星期几
                    'zc': h  # 第几周
                }
                all.append(obj)
    elif len(b) > 0:
        for h in b:
            obj = {
                'zcjc': ''.join(c),  # 第几节课
                'jsmc': arr[3],  # 教室
                'kcmc': arr[0],  # 课程名称
                'jsmc': arr[1],  # 任课教师
                'xq': day,  # 星期几
                'zc': h  # 第几周
            }
            all.append(obj)
    print(all)
    # with open('curriculum.json', 'w', encoding='utf-8') as f:
    #     json.dump(all, f, ensure_ascii=False, indent=4)


def isarr(arr):
    if len(arr) == 4:
        if '(' in arr[1]:
            arr[0] = arr[0] + arr[1]
            arr[1] = arr[2]
            arr[2] = arr[3]
            arr.pop()
            print(arr)
    else:
        if '(' in arr[1]:
            arr[0] = arr[0] + arr[1]
            arr[1] = arr[2]
            arr[2] = arr[3]
            arr[3] = arr[4]
            arr.pop()
            print(arr)
