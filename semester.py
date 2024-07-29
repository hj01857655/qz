from bs4 import BeautifulSoup

from login import isValid
import requests

def get_semester():
    r = requests.get('http://oa.csmu.edu.cn:8099/jsxsd/xskb/xskb_list.do',
                     cookies=isValid().cookies)
    soup = BeautifulSoup(r.text, features='html.parser')
    options = soup.find('select', id='xnxq01id')
    # [<option selected="selected" value="2021-2022-1">2021-2022-1</option>]
    selected = options.findAll('option', attrs={'selected':
                                                'selected'})[0].getText()
    options = options.findAll('option')
    semester = []
    for option in options:
        semester.append(option.getText())
    print(semester,selected)
    # return semester, selected
get_semester()
