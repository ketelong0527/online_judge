#!/bin/bash

echo "======================================"
echo "  在线编程练习平台部署脚本"
echo "  Server IP: 8.136.43.59"
echo "======================================"

# 1. 更新系统
echo ""
echo "[1/10] 更新系统..."
sudo apt update && sudo apt upgrade -y

# 2. 安装依赖
echo ""
echo "[2/10] 安装依赖..."
sudo apt install -y python3 python3-pip python3-venv nginx git gcc g++ make

# 3. 安装 C/C++ 编译工具
echo ""
echo "[3/10] 安装 C/C++ 编译工具..."
sudo apt install -y build-essential

# 4. 创建项目目录
echo ""
echo "[4/10] 创建项目目录..."
mkdir -p /var/www/online_judge
cd /var/www/online_judge

# 5. 创建虚拟环境
echo ""
echo "[5/10] 创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 6. 安装Python依赖
echo ""
echo "[6/10] 安装Python依赖..."
pip install --upgrade pip
pip install Django>=5.2 gunicorn>=21.0 django-crispy-forms>=2.0 crispy-bootstrap5>=2024.1 psutil

# 7. 克隆项目
echo ""
echo "[7/10] 克隆项目代码..."
git clone https://github.com/ketelong0527/online_judge.git .

# 8. 配置项目
echo ""
echo "[8/10] 配置项目..."

# 数据库迁移
python manage.py migrate

# 创建管理员
echo "创建管理员用户:"
python manage.py createsuperuser

# 收集静态文件
python manage.py collectstatic --noinput

# 9. 配置 Gunicorn 服务
echo ""
echo "[9/10] 配置 Gunicorn 服务..."

sudo tee /etc/systemd/system/online_judge.service > /dev/null <<EOF
[Unit]
Description=Gunicorn instance to serve online_judge
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/online_judge
Environment="PATH=/var/www/online_judge/venv/bin"
ExecStart=/var/www/online_judge/venv/bin/gunicorn --workers=3 --bind=0.0.0.0:8000 online_judge.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable online_judge
sudo systemctl start online_judge

# 10. 配置 Nginx
echo ""
echo "[10/10] 配置 Nginx..."

sudo tee /etc/nginx/sites-available/online_judge > /dev/null <<EOF
server {
    listen 80;
    server_name 8.136.43.59;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        root /var/www/online_judge;
    }

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/online_judge /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

echo ""
echo "======================================"
echo "  项目部署完成！"
echo "  访问地址: http://8.136.43.59"
echo "  管理后台: http://8.136.43.59/admin"
echo "======================================"