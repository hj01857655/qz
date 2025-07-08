# 🔐 环境变量配置指南

## 快速开始

### 1. 复制模板文件
```bash
cp .env.example .env
```

### 2. 编辑 .env 文件
用文本编辑器打开 `.env` 文件，填入您的真实信息：

```bash
# 教务系统登录凭据
EDU_USERNAME=您的学号
EDU_PASSWORD=您的密码
EDU_SCHOOL=10

# 数据库配置（可选）
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=您的数据库密码
DB_NAME=educational_system
```

### 3. 运行程序
```bash
python main.py --cli
```

## 📋 完整配置说明

### 必需配置
```bash
# 教务系统登录凭据
EDU_USERNAME=12023050204013    # 您的学号
EDU_PASSWORD=your_password     # 您的密码
EDU_SCHOOL=10                  # 学校代码，通常是10
```

### 可选配置

#### 数据库配置
```bash
DB_HOST=localhost              # 数据库主机
DB_PORT=3306                   # 数据库端口
DB_USER=root                   # 数据库用户名
DB_PASSWORD=your_db_password   # 数据库密码
DB_NAME=educational_system     # 数据库名称
```

#### Redis配置
```bash
REDIS_HOST=127.0.0.1          # Redis主机
REDIS_PORT=6379               # Redis端口
REDIS_DB=0                    # Redis数据库编号
```

#### 应用配置
```bash
LOG_LEVEL=INFO                # 日志级别: DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/app.log         # 日志文件路径
SESSION_TIMEOUT=3600          # 会话超时时间（秒）
MAX_RETRY_COUNT=3             # 最大重试次数
OCR_TIMEOUT=10                # 验证码识别超时时间（秒）
```

#### 教务系统URL配置
```bash
EDU_BASE_URL=http://oa.csmu.edu.cn:8099
EDU_LOGIN_URL=http://oa.csmu.edu.cn:8099/jsxsd/xk/LoginToXk
EDU_ACHIEVEMENT_URL=http://oa.csmu.edu.cn:8099/jsxsd/kscj/cjcx_list
EDU_CURRICULUM_URL=http://oa.csmu.edu.cn:8099/jsxsd/xskb/xskb_list.do
```

## 🔒 安全注意事项

### ✅ 安全做法
- ✅ 使用 `.env` 文件存储敏感信息
- ✅ `.env` 文件已在 `.gitignore` 中，不会被提交
- ✅ 定期更换密码
- ✅ 不要在代码中硬编码敏感信息

### ❌ 避免的做法
- ❌ 不要将 `.env` 文件提交到Git
- ❌ 不要在代码中硬编码密码
- ❌ 不要在公共场所展示包含密码的屏幕
- ❌ 不要与他人分享您的 `.env` 文件

## 🧪 测试配置

### 验证环境变量加载
```bash
python src/utils/env_loader.py
```

### 测试登录功能
```bash
python test_login.py
```

### 运行完整程序
```bash
# CLI模式
python main.py --cli

# GUI模式
python main.py --gui
```

## 🔧 故障排除

### 问题1：找不到 .env 文件
```
⚠️ 环境变量文件不存在: /path/to/.env
💡 请复制 .env.example 为 .env 并填入真实值
```

**解决方案**：
```bash
cp .env.example .env
# 然后编辑 .env 文件填入真实信息
```

### 问题2：环境变量格式错误
```
⚠️ .env 文件第 X 行格式错误: 错误内容
```

**解决方案**：
- 确保每行格式为 `KEY=VALUE`
- 不要在 `=` 前后添加空格
- 如果值包含空格，用引号包围：`KEY="value with spaces"`

### 问题3：登录失败
**检查清单**：
- ✅ 用户名和密码是否正确
- ✅ 网络是否可以访问教务系统
- ✅ 验证码识别是否成功
- ✅ 学校代码是否正确

## 📝 示例 .env 文件

```bash
# 教务系统配置
EDU_USERNAME=12023050204013
EDU_PASSWORD=MySecurePassword123
EDU_SCHOOL=10

# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=MyDBPassword123
DB_NAME=educational_system

# Redis配置
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0

# 应用配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
SESSION_TIMEOUT=3600
MAX_RETRY_COUNT=3
OCR_TIMEOUT=10
```

## 💡 提示

1. **首次使用**：复制 `.env.example` 为 `.env` 并填入真实信息
2. **开发环境**：可以创建 `.env.development` 用于开发
3. **生产环境**：可以创建 `.env.production` 用于生产
4. **团队协作**：只分享 `.env.example`，不要分享包含真实凭据的 `.env` 文件

现在您可以安全地使用 `.env` 文件来管理您的凭据了！
