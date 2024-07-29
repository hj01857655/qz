import re, requests
from login import isValid
import pandas as pd

def achievement():
    try:
        data = {"kksj": "", "kcxz": "", "kcmc": "", "xsfs": "max"}
        arr = []
        cj = requests.post('http://oa.csmu.edu.cn:8099/jsxsd/kscj/cjcx_list',
                           data=data,
                           cookies=isValid().cookies).text
        a, _ = re.subn('\r', '', cj)
        a, _ = re.subn('\n', '', a)
        a, _ = re.subn('\t', '', a)
        tr = re.findall('<tr.*?>.*?</tr>', a)
        tr.remove(tr[0])
        tr.remove(tr[0])
        for i in range(0, len(tr)):
            m = tr[i]
            m = m.replace('align="left"', "")
            m = m.replace(' ', "")
            m = m.replace('<tr>', "")
            m = m.replace('</tr>', "")
            m = m.replace('</tr>', "")
            m = m.replace('</td>', "")
            m = m.replace('style=" color:red;"', "")
            m = m.replace('<!-- 由于成绩项目基本不会改动，未做对应变化。 -->', "")
            m = m.replace('<!--控制绩点显示-->', "")
            m = m.replace('<!--控制成绩显示-->', "")
            m = m.replace('<!--技能成绩-->', "")
            m = m.replace('<!--平时成绩-->', "")
            m = m.replace('<!--卷面成绩-->', "")
            # m = m.replace('<tdstyle="color:red;">', "<td>")
            m = m.replace('<td style=" ">', "<td>")
            m = m.replace('<tdstyle="">', "<td>")
            m = m.replace('<tdstyle="color:red;">', "<td>")
            m = m.replace('</a>', "")
            m = m.split('<td>')
            aobj = []
            for t in m:
                aobj.append(t)
            aobj.remove(aobj[0])
            aobj[4] = re.findall('zcj=(\d{2}|通过)', str(aobj[4]))[0]
            # print(len(aobj))
            obj = {
                "xnxqmc": aobj[1],  # 学年学期
                "kcbh": aobj[2],  # 课程编号
                "kcmc": aobj[3],  # 课程名称
                "kczcj": aobj[4],  # 课程成绩
                "jncj": aobj[5],  # 技能成绩
                "pscj": aobj[6],  # 平时成绩
                "jmcj": aobj[7],  # 卷面成绩
                "cjbz": aobj[8],  # 成绩标志
                "xf": aobj[9],  # 学分
                "ksxz": aobj[10],  # 考试性质(正常考试，补考)
                "zxs": aobj[11],  # 学时
                "cjjd": aobj[12],  # 绩点
                "khfs": aobj[13],  # 考核方式
                "kcsx": aobj[14],  # 课程属性
                "kcxz": aobj[15],  # 课程性质
            }
            arr.append(obj)
        

        with open('achievement.json', 'w', encoding='utf-8') as f:
            f.write(str(arr) + '\n')

        return arr
    except Exception as e:
        # print(Exception.args,e)
        with open('achievement.json', 'r', encoding='utf-8') as f:
            achievement=f.read()
        return achievement
