#!/bin/bash

echo "======================================"
echo "  在线编程练习平台部署脚本"
echo "  Server IP: 47.99.140.127"
echo "======================================"

# 1. 更新系统
echo ""
echo "[1/7] 更新系统..."
sudo apt update && sudo apt upgrade -y

# 2. 安装依赖
echo ""
echo "[2/7] 安装依赖..."
sudo apt install -y python3 python3-pip python3-venv nginx git

# 3. 创建项目目录
echo ""
echo "[3/7] 创建项目目录..."
mkdir -p /var/www/online_judge
cd /var/www/online_judge

# 4. 创建虚拟环境
echo ""
echo "[4/7] 创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 5. 安装Python依赖
echo ""
echo "[5/7] 安装Python依赖..."
pip install Django>=5.2 gunicorn>=21.0 django-crispy-forms>=2.0 crispy-bootstrap5>=2024.1

# 6. 克隆项目（请替换为你的Git仓库地址）
echo ""
echo "[6/7] 克隆项目代码..."
git clone https://github.com/your-username/online_judge.git .

# 7. 配置项目
echo ""
echo "[7/7] 配置项目..."

# 数据库迁移
python manage.py migrate

# 创建管理员
echo "创建管理员用户:"
python manage.py createsuperuser

# 收集静态文件
python manage.py collectstatic --noinput

echo ""
echo "======================================"
echo "  项目部署完成！"
echo "  接下来配置Gunicorn和Nginx"
echo "======================================"
