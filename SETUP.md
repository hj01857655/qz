# 项目设置指南

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/hj01857655/qz.git
cd qz
```

### 2. 创建虚拟环境
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置文件设置
```bash
# 复制配置模板
cp config/config.json.template config/config.json

# 编辑配置文件，填入实际的数据库连接信息
# 编辑器打开 config/config.json
```

### 5. 运行项目
```bash
# GUI模式（推荐）
python main.py

# 命令行模式
python main.py --cli

# 查看帮助
python main.py --help
```

## 详细配置

### 数据库配置（可选）

如果需要使用数据库功能，请配置MySQL和Redis：

1. **MySQL配置**
   ```json
   {
       "mysql": {
           "host": "localhost",
           "port": 3306,
           "user": "your_username",
           "password": "your_password",
           "database": "educational_system"
       }
   }
   ```

2. **Redis配置**
   ```json
   {
       "redis": {
           "host": "127.0.0.1",
           "port": 6379,
           "db": 0
       }
   }
   ```

3. **初始化数据库**
   ```bash
   python database/setup_database.py
   ```

### 环境变量（可选）

可以通过环境变量覆盖配置：
```bash
export DB_HOST=localhost
export DB_USER=your_username
export DB_PASSWORD=your_password
```

## 开发指南

### 项目结构
```
qz/
├── src/                  # 核心业务逻辑
│   ├── auth/            # 认证模块
│   ├── academic/        # 学术信息模块
│   └── models/          # 数据模型
├── database/            # 数据库相关
├── utils/               # 工具模块
├── gui/                 # 图形界面
├── config/              # 配置文件
├── tests/               # 测试文件
├── data/                # 数据文件
└── logs/                # 日志文件
```

### 添加新功能
1. 在相应模块目录下创建新文件
2. 在 `__init__.py` 中导出新功能
3. 更新主程序调用

### 运行测试
```bash
pytest tests/
```

### 代码格式化
```bash
black .
isort .
```

### 类型检查
```bash
mypy src/
```

## 故障排除

### 常见问题

1. **导入错误**
   - 确保在项目根目录运行
   - 检查虚拟环境是否激活

2. **依赖包缺失**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置文件错误**
   - 检查 `config/config.json` 格式
   - 参考 `config/config.json.template`

4. **数据库连接失败**
   - 检查数据库服务是否运行
   - 验证连接信息是否正确

### 获取帮助

- 查看 [README.md](README.md) 了解项目详情
- 提交 [Issue](https://github.com/hj01857655/qz/issues) 报告问题
- 查看项目 [Wiki](https://github.com/hj01857655/qz/wiki) 获取更多文档

## 更新项目

```bash
git pull origin main
pip install -r requirements.txt
```

## 贡献代码

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

欢迎贡献！
