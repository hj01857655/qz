# 教务系统

一个用于获取教务系统信息的Python应用程序，支持成绩查询、课程表查询等功能。

## 功能特性

- 🔐 **用户认证**: 支持验证码识别的自动登录
- 📊 **成绩查询**: 获取并解析学生成绩信息
- 📅 **课程表查询**: 获取课程表信息
- 💾 **数据存储**: 支持MySQL和Redis数据存储
- 🖥️ **双界面**: 支持GUI图形界面和CLI命令行界面
- 📁 **结构化**: 清晰的模块化项目结构

## 开发环境

- **操作系统**: Windows 11
- **开发工具**: Cursor IDE / VSCode
- **编程语言**: Python 3.12
- **数据库**: MySQL 8.4.0, Redis
- **数据库管理工具**: Navicat Premium 17.0.8

## 项目结构

```
qz/
├── main.py                 # 主入口文件
├── README.md              # 项目说明
├── requirements.txt       # 依赖库
├── .cursorrules          # Cursor IDE配置
├── .gitignore            # Git忽略文件
├── .vscode/              # VSCode配置
├── src/                  # 核心业务逻辑
│   ├── __init__.py
│   ├── auth/             # 认证模块
│   │   ├── __init__.py
│   │   └── login.py      # 登录功能
│   ├── academic/         # 学术信息模块
│   │   ├── __init__.py
│   │   ├── achievement.py # 成绩查询
│   │   ├── curriculum.py  # 课程表查询
│   │   └── semester.py    # 学期信息
│   └── models/           # 数据模型
│       ├── __init__.py
│       └── data.py       # 数据处理
├── database/             # 数据库相关
│   ├── __init__.py
│   ├── db_config.py      # 数据库配置
│   ├── setup_database.py # 数据库初始化
│   ├── mysql_operations.py # MySQL操作
│   ├── mysql.py          # MySQL模型
│   ├── redis1.py         # Redis操作
│   └── sql.py            # SQL查询
├── utils/                # 工具模块
│   ├── __init__.py
│   ├── code1.py          # 验证码识别
│   ├── conwork.py        # 编码工具
│   ├── parsers/          # 解析器
│   └── validators/       # 验证器
├── gui/                  # 图形界面
│   ├── __init__.py
│   └── gui.py            # GUI界面
├── config/               # 配置文件
│   └── config.json       # 配置文件
├── tests/                # 测试文件
│   ├── test.py
│   └── bj.py
├── data/                 # 数据文件
│   ├── *.json            # JSON数据文件
│   └── *.html            # HTML文件
└── logs/                 # 日志文件
```

## 依赖库

```txt
requests          # HTTP请求
selenium          # 浏览器自动化
pyautogui         # GUI自动化
pytesseract       # OCR文字识别
pymysql           # MySQL数据库
redis             # Redis数据库
beautifulsoup4    # HTML解析
tkinter           # GUI界面（Python内置）
pandas            # 数据处理
sqlalchemy        # ORM框架
```

## 安装和使用

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd qz

# 安装依赖
pip install -r requirements.txt

# 配置数据库（可选）
# 编辑 config/config.json 文件，配置MySQL和Redis连接信息
```

### 2. 配置文件

在 `config/config.json` 中配置数据库连接信息：

```json
{
    "mysql": {
        "host": "localhost",
        "port": 3306,
        "user": "your_username",
        "password": "your_password",
        "database": "educational_system"
    },
    "redis": {
        "host": "127.0.0.1",
        "port": 6379,
        "db": 0
    }
}
```

### 3. 运行程序

#### GUI模式（推荐）
```bash
python main.py
# 或
python main.py --gui
```

#### 命令行模式
```bash
python main.py --cli
```

#### 查看帮助
```bash
python main.py --help
```

## 使用说明

### GUI模式
1. 运行程序后会打开登录界面
2. 输入用户名和密码
3. 程序会自动识别验证码并登录
4. 登录成功后可以查看成绩和课程表信息

### CLI模式
1. 程序会自动检查登录状态
2. 根据菜单提示选择功能：
   - 获取成绩信息
   - 获取课程表信息
   - 获取所有数据

## 模块说明

### 认证模块 (src/auth/)
- `login.py`: 处理用户登录、验证码识别、会话管理

### 学术信息模块 (src/academic/)
- `achievement.py`: 成绩信息获取和解析
- `curriculum.py`: 课程表信息获取和解析
- `semester.py`: 学期信息处理

### 数据库模块 (database/)
- `mysql.py`: MySQL数据库模型和操作
- `redis1.py`: Redis缓存操作
- `sql.py`: 统一的数据库查询接口

### 工具模块 (utils/)
- `code1.py`: 验证码识别工具
- `conwork.py`: 数据编码和转换工具

## 开发指南

### 添加新功能
1. 在相应的模块目录下创建新文件
2. 在对应的 `__init__.py` 中导出新功能
3. 更新主程序中的导入和调用

### 数据库操作
- 使用 `database/sql.py` 中的统一接口
- MySQL用于持久化存储
- Redis用于缓存和临时数据

### 错误处理
- 所有模块都包含完善的异常处理
- 网络错误时会尝试从本地缓存加载数据
- 详细的错误日志记录

## 🚨 安全警告

**⚠️ 重要安全提醒**: 本项目曾在Git历史中泄露过敏感信息。请查看 [SECURITY_ALERT.md](SECURITY_ALERT.md) 了解详情。

### 安全最佳实践

1. **永远不要硬编码敏感信息**: 使用环境变量或安全配置文件
2. **定期更换密码**: 建议定期更新您的登录凭据
3. **使用安全的凭据管理**: 本项目提供了安全的凭据管理机制
4. **检查.gitignore**: 确保敏感文件不会被提交到版本控制

## 注意事项

1. **网络连接**: 需要能够访问教务系统网站
2. **验证码识别**: 依赖OCR技术，识别率可能不是100%
3. **数据安全**: 请妥善保管登录凭据和配置文件
4. **合规使用**: 请遵守学校相关规定，仅用于个人学习目的
5. **凭据安全**: 使用环境变量或安全配置，避免硬编码敏感信息

## 故障排除

### 常见问题

1. **登录失败**
   - 检查网络连接
   - 确认用户名密码正确
   - 检查验证码识别是否正常

2. **数据库连接失败**
   - 检查配置文件中的数据库信息
   - 确认数据库服务正在运行
   - 检查防火墙设置

3. **GUI界面无法启动**
   - 确认已安装tkinter（通常Python自带）
   - 尝试使用CLI模式

## 更新日志

### v1.0.0 (2025-07-08)
- ✨ 重构项目结构，采用模块化设计
- 🔧 优化代码质量，添加类型注解
- 📚 完善文档和使用说明
- 🐛 修复已知问题
- 🎨 改进用户界面

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

本项目仅供学习和研究使用。
    







