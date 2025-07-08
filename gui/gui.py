import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import csv
import textwrap
import tkinter.font as tkFont
import sys
from pathlib import Path
from bs4 import BeautifulSoup

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.mysql_operations import insert_user, get_user, update_user_password, get_remembered_user
from database.db_config import execute_query
from src.auth.login import login

# 全局变量用于保存会话
session = None

def on_login():
    global session
    username = username_entry.get()
    password = password_entry.get()
    remember = remember_var.get()

    # 使用login.py中的login方法验证用户
    session = login(username, password)
    if session:
        # 检查用户是否存在
        user = get_user(username)
        if user:
            # 如果用户存在，更新记住密码状态
            update_user_password(username, password, remember)
        else:
            # 如果用户不存在，插入新用户
            insert_user(username, password, remember)
        
        messagebox.showinfo("登录成功", "您已成功登录！")
        root.withdraw()  # 隐藏登录窗口
        open_main_gui()  # 登录成功后打开主界面
    else:
        messagebox.showerror("登录失败", "用户名或密码错误，请重试。")

def export_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data)

def adjust_row_height(new_height):
    style = ttk.Style()
    style.configure("Treeview", rowheight=new_height)

def show_current_week_schedule():
    global session
    if session:  # 使用已保存的会话
        schedule_window = tk.Toplevel()
        schedule_window.title("当前周次课表")

        # 创建一个Frame来组织选择器和按钮
        control_frame = ttk.Frame(schedule_window, padding="10")
        control_frame.pack(side=tk.TOP, fill=tk.X)

        # 学期选择器
        ttk.Label(control_frame, text="选择学期:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        term_combobox = ttk.Combobox(control_frame, values=[
            "2024-2025-2", "2024-2025-1", "2023-2024-2", "2023-2024-1",
            "2022-2023-2", "2022-2023-1", "2021-2022-2", "2021-2022-1",
            "2020-2021-2", "2020-2021-1", "2019-2020-2", "2019-2020-1",
            "2018-2019-2", "2018-2019-1", "2017-2018-2", "2017-2018-1",
            "2016-2017-2", "2016-2017-1", "2015-2016-2", "2015-2016-1",
            "2014-2015-2", "2014-2015-1", "2013-2014-2", "2013-2014-1",
            "2012-2013-2", "2012-2013-1", "2011-2012-2", "2011-2012-1",
            "2010-2011-2", "2010-2011-1", "2009-2010-2", "2009-2010-1",
            "2008-2009-2", "2008-2009-1", "2007-2008-2", "2007-2008-1",
            "2006-2007-2", "2006-2007-1", "2005-2006-2", "2005-2006-1"
        ])
        term_combobox.set("2024-2025-2")  # 默认值
        term_combobox.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        # 周次选择器
        ttk.Label(control_frame, text="选择周次:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        week_combobox = ttk.Combobox(control_frame, values=[
            "(全部)", "第1周", "第2周", "第3周", "第4周", "第5周", "第6周", "第7周", "第8周",
            "第9周", "第10周", "第11周", "第12周", "第13周", "第14周", "第15周", "第16周",
            "第17周", "第18周", "第19周", "第20周", "第21周", "第22周", "第23周", "第24周",
            "第25周", "第26周", "第27周", "第28周", "第29周", "第30周"
        ])
        week_combobox.set("(全部)")  # 默认值
        week_combobox.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        # 初始化课表数据
        schedule_data = []

        def update_schedule(event=None):
            nonlocal schedule_data  # 使用nonlocal关键字来修改外部作用域的变量
            selected_week = week_combobox.get()
            selected_term = term_combobox.get()
            
            # 如果选择了"全部"，则设置为0
            week = "" if selected_week == "(全部)" else int(selected_week.replace("第", "").replace("周", ""))
            
            schedule_data = fetch_schedule(session, week, selected_term)
            
            if schedule_data:
                for item in tree.get_children():
                    tree.delete(item)
                for row in schedule_data:
                    # 处理换行
                    formatted_row = [textwrap.fill(cell, width=20) for cell in row]
                    tree.insert("", "end", values=formatted_row)
                
                # 动态调整行高
                max_lines = max(len(cell.split('\n')) for row in schedule_data for cell in row)
                adjust_row_height(max(50, max_lines * 20))  # 每行至少50像素高，每行内容增加20像素
            else:
                tk.messagebox.showerror("错误", "无法获取课表信息")

        # 查询按钮
        query_button = ttk.Button(control_frame, text="查询", command=update_schedule)
        query_button.grid(row=0, column=4, padx=10, pady=5, sticky='w')  # 将按钮放在选择器右边

        # 导出课表按钮
        export_button = ttk.Button(control_frame, text="导出课表", command=lambda: export_to_csv(schedule_data, "current_week_schedule.csv"))
        export_button.grid(row=0, column=5, padx=10, pady=5, sticky='w')  # 将按钮放在查询按钮旁边

        # 绑定选择器的事件
        term_combobox.bind("<<ComboboxSelected>>", update_schedule)
        week_combobox.bind("<<ComboboxSelected>>", update_schedule)

        # 更新列标题以匹配课表数据
        columns = ["时间段", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

        # 设置Treeview的样式
        style = ttk.Style()
        style.configure("Treeview", rowheight=50, borderwidth=1, relief="solid", highlightthickness=1, highlightbackground="black")  # 初始行高为50，设置边框样式
        style.map("Treeview", background=[('selected', 'lightblue')])

        tree = ttk.Treeview(schedule_window, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor='center')  # 列宽可拖动调整

        tree.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)  # 增加填充

        # 添加垂直和水平滚动条
        vsb = ttk.Scrollbar(schedule_window, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(schedule_window, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')

        # 在窗口创建后立即更新课表
        update_schedule()

    else:
        tk.messagebox.showerror("错误", "登录失败，无法获取课表信息")

def show_grades():
    global session
    if session:  # 确保会话已登录
        grades_window = tk.Toplevel()
        grades_window.title("成绩展示")

        # 创建一个Frame来组织选择器和按钮
        control_frame = ttk.Frame(grades_window, padding="10")
        control_frame.pack(side=tk.TOP, fill=tk.X)

        # 学期选择器
        ttk.Label(control_frame, text="选择学期:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        term_combobox = ttk.Combobox(control_frame, values=[
            "(全部学期)", "2024-2025-1", "2023-2024-2", "2023-2024-1", "2022-2023-2", "2022-2023-1"
        ])
        term_combobox.set("(全部学期)")  # 默认值
        term_combobox.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        # 课程性质选择器
        ttk.Label(control_frame, text="课程性质:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        kcxz_combobox = ttk.Combobox(control_frame, values=[
            "---请选择---", "公共课", "公共基础课", "专业基础课", "专业课", "专业选修课", "公共选修课", "其它"
        ])
        kcxz_combobox.set("---请选择---")  # 默认值
        kcxz_combobox.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        # 课程性质映射
        kcxz_mapping = {
            "---请选择---": "",
            "公共课": "01",
            "公共基础课": "02",
            "专业基础课": "03",
            "专业课": "04",
            "专业选修课": "05",
            "公共选修课": "06",
            "其它": "07"
        }

        # 初始化成绩数据
        grades_data = []

        def update_grades(event=None):
            nonlocal grades_data
            selected_term = term_combobox.get()
            term_param = "" if selected_term == "(全部学期)" else selected_term
            selected_kcxz = kcxz_combobox.get()
            kcxz_param = kcxz_mapping.get(selected_kcxz, "")
            grades_data = fetch_grades_data(session, term=term_param, kcxz=kcxz_param)
            
            if grades_data:
                for item in tree.get_children():
                    tree.delete(item)
                for row in grades_data:
                    tree.insert("", "end", values=row)
                
                # 调整列宽
                for col in columns:
                    tree.column(col, width=tkFont.Font().measure(col))
                for row in grades_data:
                    for i, value in enumerate(row):
                        col_width = tkFont.Font().measure(value)
                        if tree.column(columns[i], width=None) < col_width:
                            tree.column(columns[i], width=col_width)
                
                # 如果选择的是全部学期，插入数据到数据库
                if term_param == "":
                    insert_grades_data(grades_data)
            else:
                tk.messagebox.showerror("错误", "无法获取成绩信息")

        # 创建Treeview来显示成绩
        columns = ["序号", "开课学期", "课程编号", "课程名称", "总成绩", "技能成绩", "平时成绩", "卷面成绩", "成绩标志", "学分", "考试性质", "总学时", "绩点", "考核方式", "课程属性", "课程性质"]
        tree = ttk.Treeview(grades_window, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor='center')

        tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # 导出成绩按钮
        export_button = ttk.Button(grades_window, text="导出成绩", command=lambda: export_to_csv(grades_data, "grades.csv"))
        export_button.pack(pady=10)

        # 在窗口创建后立即更新成绩
        update_grades()

        # 绑定选择器的事件
        term_combobox.bind("<<ComboboxSelected>>", update_grades)
        kcxz_combobox.bind("<<ComboboxSelected>>", update_grades)
    else:
        tk.messagebox.showerror("错误", "请先登录")

def fetch_grades_data(session, term="", kcxz="", kcmc="", xsfs="max"):
    url = "http://oa.csmu.edu.cn:8099/jsxsd/kscj/cjcx_list"
    params = {
        "kksj": term,
        "kcxz": kcxz,
        "kcmc": kcmc,
        "xsfs": xsfs
    }
    
    # 打印请求参数以进行调试
    print(f"Fetching grades with params: {params}")
    
    response = session.post(url, data=params)
    
    # 打印响应状态码和内容以进行调试
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text[:500]}")  # 只打印前500个字符以避免过多输出
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 查找成绩表格
        table = soup.find('table', {'id': 'dataList'})
        grades_data = []

        if table:
            rows = table.find_all('tr')
            for row in rows[1:]:  # 跳过表头
                cols = row.find_all('td')
                # 提取每列的数据，忽略第一列（id）
                data = [col.text.strip() for col in cols[1:]]
                # 确保数据行有15个元素
                if len(data) == 15:
                    grades_data.append(data)
                else:
                    print(f"Data row does not match expected length: {data}")

        return grades_data
    else:
        print("Failed to retrieve grades data")
        return []

def insert_grades_data(grades_data):
    query = """
    INSERT INTO grades (term, course_code, course_name, total_score, skill_score, usual_score, exam_score, score_flag, credit, exam_nature, total_hours, gpa, assessment_method, course_attribute, course_nature)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    for row in grades_data:
        # 打印每一行数据以进行调试
        print(f"Inserting row: {row}")
        execute_query(query, row)

def open_main_gui():
    global week_combobox, term_combobox

    main_window = tk.Toplevel()
    main_window.title("教务系统")
    main_window.geometry("600x400")

    # 窗口居中
    main_window.update_idletasks()
    width = main_window.winfo_width()
    height = main_window.winfo_height()
    x = (main_window.winfo_screenwidth() // 2) - (width // 2)
    y = (main_window.winfo_screenheight() // 2) - (height // 2)
    main_window.geometry(f'{width}x{height}+{x}+{y}')

    # 使用ttk.Style来设置样式
    style = ttk.Style()
    style.configure('TButton', font=('Arial', 12), padding=10)
    style.configure('TLabel', font=('Arial', 16))

    # 创建一个Frame来组织组件
    frame = ttk.Frame(main_window, padding="10")
    frame.pack(expand=True, fill='both')

    # 添加组件到Frame中
    ttk.Label(frame, text="欢迎使用系统！").pack(pady=20)

    ttk.Button(frame, text="当前周次课表", command=show_current_week_schedule).pack(pady=5)
    ttk.Button(frame, text="成绩查询", command=show_grades).pack(pady=5)  # 添加成绩查询按钮
    ttk.Button(frame, text="退出", command=lambda: [main_window.destroy(), root.deiconify()]).pack(pady=10)

def create_login_gui():
    global username_entry, password_entry, remember_var, root

    root = tk.Tk()
    root.title("登录界面")
    root.geometry("400x300")  # 设置登录界面的大小

    # 窗口居中
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    # 设置列的权重，使表单居中
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

    # 创建学号标签和输入框
    ttk.Label(root, text="学号:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
    username_entry = ttk.Entry(root)
    username_entry.grid(row=0, column=1, padx=10, pady=10, sticky='w')

    # 创建密码标签和输入框
    ttk.Label(root, text="密码:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
    password_entry = ttk.Entry(root, show="*")
    password_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')

    # 创建记住密码复选框
    remember_var = tk.BooleanVar()
    remember_check = ttk.Checkbutton(root, text="记住密码", variable=remember_var)
    remember_check.grid(row=2, column=0, columnspan=2)

    # 检查是否有记住密码的用户
    remembered_user = get_remembered_user()
    if remembered_user:
        username_entry.insert(0, remembered_user['username'])
        password_entry.insert(0, remembered_user['password'])
        remember_var.set(True)
        # 自动登录
        on_login()

    # 创建登录按钮
    login_button = ttk.Button(root, text="登录", command=on_login)
    login_button.grid(row=3, column=0, columnspan=2, pady=20)

    root.mainloop()

def fetch_schedule(session, week, term):
    url = "http://oa.csmu.edu.cn:8099/jsxsd/xskb/xskb_list.do"
    params = {
        "zc": week,
        "xnxq01id": term
    }
    response = session.post(url, data=params)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        table = soup.find('table', {'id': 'kbtable'})
        schedule_data = []

        if table:
            rows = table.find_all('tr')
            for row in rows[1:]:
                time_slot = row.find('th').text.strip()
                cols = row.find_all('td')
                day_data = [time_slot]

                for col in cols:
                    course_info = col.find('div', class_='kbcontent')
                    if course_info:
                        course_details = course_info.get_text(separator=' ', strip=True)
                        day_data.append(course_details)
                    else:
                        day_data.append('')

                schedule_data.append(day_data)

        return schedule_data
    else:
        print("Failed to retrieve schedule data")
        return None

if __name__ == "__main__":
    create_login_gui()

