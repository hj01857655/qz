import re, json
import requests
from login import isValid
from bs4 import BeautifulSoup



class course:
    def __init__(self, name, teacher, weeks, periods, classroom):
        self.name = name
        self.teacher = teacher
        self.weeks = weeks
        self.periods = periods
        self.classroom = classroom
        self.session=isValid()


# def fetch_course_table_page():
#     driver.get('http://oa.csmu.edu.cn:8099/jsxsd/xskb/xskb_list.do')
#     driver.add_cookie({'name': 'JSESSIONID', 'value': isValid().cookies['JSESSIONID']})
#     time.sleep(1)  # 延迟 1 秒
#     driver.refresh()
#     try:
#         table = WebDriverWait(driver, timeout=5).until(lambda d: d.find_element(By.XPATH,'//*[@id="kbtable"]'))
#     except NoSuchElementException:
#         print("未找到课表表格")
#         return None
#     return driver.page_source
def get_course_table():
    session=isValid()
    xskb_url='http://oa.csmu.edu.cn:8099/jsxsd/xskb/xskb_list.do'
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
    soup=BeautifulSoup(html,features='lxml')
    kb_table=soup.find('table',id='kbtable')
    if kb_table:
        table_content=kb_table.decode_contents()
        courses=[]
        for row in kb_table.find_all('tr')[1:]: #跳过标题行
            cells=row.find_all('td')
                
                
                    
                        

                

                
            
                
            
        
            
            
                
            
        

if __name__ == '__main__':
    html=get_course_table()
    parse_course_table(html)