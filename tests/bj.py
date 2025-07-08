import requests
import ddddocr
import time
import os
import re
from bs4 import BeautifulSoup
import csv
import json
from mysql_operations import insert_or_update_class_data_from_json

# 登录

#登录类
class Auth:

    #请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/85.0.4183.83 Safari/537.36',
        'Host': 'oa.csmu.edu.cn:8099',
        'Referer': 'http://oa.csmu.edu.cn:8099/Logon.do?method=logon'

    }
    #请求地址
    host = 'http://oa.csmu.edu.cn:8099/'
    #初始化
    def __init__(self, name=None, pwd=None):

        self.session = requests.session()
        if name and pwd:

            self.get_cookie()
            self.login(name, pwd)
    #管理端登录验证码识别
    def code_ocr(self, username):
        try:
            image_url = f'CSMU_code_{username}.png'
            response = self.session.get(f'http://oa.csmu.edu.cn:8099/verifycode.servlet?t={time.time()}')

            if response.status_code == 200:
                with open(image_url, 'wb') as file:
                    file.write(response.content)

                with open(image_url, 'rb') as image:
                    ocr = ddddocr.DdddOcr()
                    code = ocr.classification(image.read())
                    return code
                    
            else:
                print(f"获取验证码失败，状态码：{response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"请求异常：{e}")
            return None
        except Exception as e:
            print(f"验证码识别过程中出现问题：{e}")
            return None
        
    #登录参数编码
    def encode(self, username, password):
        url = '/Logon.do?method=logon&flag=sess'
        r = self.session.get(self.host + url, headers=self.headers)
        data_str = r.text
        scode, sxh = data_str.split("#")
        code = f"{username}%%%{password}"

        encode = ""
        i = 0
        while i < len(code):
            if i < 20:
                encode += code[i:i + 1] + scode[:int(sxh[i:i + 1])]
                scode = scode[int(sxh[i:i + 1]):]
            else:
                encode += code[i:]
                break
            i += 1
        return encode
    
    #管理端登录
    def login(self, name, pwd):
        url = '/Logon.do?method=logon'

        data = {
            'encoded': self.encode(name, pwd),
            'RANDOMCODE': self.code_ocr(name)
        }
        
        r = self.session.post(self.host + url, headers=self.headers, data=data)
        #获取<font color="red">验证码错误!!</font>中的text
        error_text = re.search(r'<font color="red">(.+?)</font>', r.text)
        if error_text:
            print(error_text.group(1))
            return False
        else:
            print('登录成功')
            return True

    #获取cookie
    def get_cookie(self):
        self.session.get(self.host, headers=self.headers)

    #获取班级信息
    def get_bj(self):
        url = 'bjxx.do?method=findByBjxxLb'
        page_num = 1
        all_data = []
        column_headers = []

        # 数据库字段名映射
        field_mapping = {
            "序号": "serial_number",
            "班级编号": "class_number",
            "班级名称": "class_name",
            "所属校区": "campus",
            "所属单位": "department",
            "专业名称": "major_name",
            "培养层次": "education_level",
            "电子注册号": "registration_number",
            "所属年度": "academic_year",
            "专业编号": "major_code",
            "班级人数": "class_size",
            "实际人数": "actual_size",
            "固定教室": "fixed_classroom",
            "联系电话": "contact_number",
            "有效状态": "valid_status",
            "部颁专业名称": "official_major_name",
            "部颁专业代码": "official_major_code",
            "学科门类": "discipline_category",
            "操作": "operation_link"
        }

        while True:
            params = {
                'dataTotal': 1218,  # 总数据量
                'pageSize': 200,    # 每页数据量
                'PageNum': page_num # 当前页码
            }
            
            # 利用登录的缓存进行请求
            r = self.session.get(self.host + url, headers=self.headers, params=params)
            
            # bs4解析
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # 获取到form标签
            form = soup.find('form')
            if not form:
                print("未找到表单，可能是请求失败或页面结构变化。")
                break
            
            # 数据在form下的div
            div = form.find('div', {'id': 'tag_tshowView'})
            if not div:
                print("未找到数据容器，可能是请求失败或页面结构变化。")
                break
            
            # div下的table
            table = div.find('table', {'id': 'dataTables'})
            if not table:
                print("未找到数据表，可能是请求失败或页面结构变化。")
                break
            
            # 提取表头，忽略第一个th
            if not column_headers:
                thead = table.find('thead')
                if thead:
                    header_row = thead.find('tr')
                    column_headers = [th.text.strip() for th in header_row.find_all('th')[1:]]
            
            # 提取数据，忽略第一个td
            tbody = table.find('tbody')
            if not tbody:
                print("未找到表格主体，可能是请求失败或页面结构变化。")
                break
            
            # 提取行数据
            rows = tbody.find_all('tr')
            for row in rows:
                cols = row.find_all('td')[1:]  # 忽略第一个td
                data = {field_mapping[column_headers[i]]: col.text.strip() for i, col in enumerate(cols[:-1])}  # 忽略最后一个td
                
                # 处理最后一个td，提取onclick中的URL
                last_td = cols[-1]
                a_tag = last_td.find('a')
                if a_tag and 'onclick' in a_tag.attrs:
                    onclick_value = a_tag['onclick']
                    match = re.search(r"JsMod\('(.+?)'", onclick_value)
                    if match:
                        data[field_mapping["操作"]] = match.group(1).replace('&amp;', '&')  # 替换HTML实体
                
                all_data.append(data)
            
            # 检查是否还有下一页
            if len(rows) < params['pageSize']:
                print("已到达最后一页。")
                break
            
            page_num += 1

        # 将数据转换为JSON格式并写入文件
        with open('all_class_data.json', 'w', encoding='utf-8') as file:
            json.dump(all_data, file, ensure_ascii=False, indent=4)
        print("所有班级数据已保存到all_class_data.json。")


    #
#测试
if __name__ == '__main__':
    auth = Auth('20130040', 'fincon123456')
    if auth:
        auth.get_bj()
        insert_or_update_class_data_from_json('all_class_data.json')

