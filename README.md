# 如何启动在线编程练习平台

## 方式一：使用批处理脚本（推荐）

双击运行 `start_server.bat` 文件即可自动启动服务器。

---

## 方式二：使用命令行手动启动

### 步骤 1: 打开命令提示符
按 `Win + R`，输入 `cmd`，按回车。

### 步骤 2: 进入项目目录
```bash
cd c:\Users\30782\d1\online_judge
```

### 步骤 3: 启动服务器
```bash
python manage.py runserver
```

### 步骤 4: 访问应用
在浏览器中打开：
- **首页**: http://127.0.0.1:8000/
- **题目列表**: http://127.0.0.1:8000/problems/
- **管理后台**: http://127.0.0.1:8000/admin/

---

## 其他常用命令

### 启动服务器（指定端口）
```bash
python manage.py runserver 8080
```

### 允许外部访问
```bash
python manage.py runserver 0.0.0.0:8000
```

### 创建超级用户
```bash
python manage.py createsuperuser
```

### 进行数据库迁移
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 管理账号

| 项目 | 内容 |
|-----|------|
| 用户名 | admin |
| 密码 | admin123 |
| 邮箱 | admin@example.com |

---

## 停止服务器

在命令窗口中按 `Ctrl + C`

---

## 常见问题

### 问题1: 提示找不到 python 命令
**解决:** 确保已安装 Python 并添加到系统 PATH 环境变量。

### 问题2: 端口已被占用
**解决:** 使用其他端口，例如：
```bash
python manage.py runserver 8080
```

### 问题3: 提示模块缺失
**解决:** 安装依赖包：
```bash
pip install -r requirements.txt
```

---

## 项目结构

```
online_judge/
├── manage.py          # Django 管理脚本
├── start_server.bat   # 快速启动脚本
├── requirements.txt   # 依赖列表
├── db.sqlite3         # 数据库文件
├── online_judge/      # 项目配置目录
├── oj_problems/       # 题目管理应用
├── oj_users/          # 用户管理应用
├── oj_submissions/    # 提交管理应用
├── oj_judge/          # 判题系统应用
└── templates/         # 模板文件
```
