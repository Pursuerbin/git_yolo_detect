#!/bin/bash

# 启动后端服务脚本

echo "正在启动后端服务..."

# 切换到后端目录
cd ~/project/backend

# 激活conda环境
source ~/miniconda3/bin/activate flask

# 检查环境是否激活成功
if [ $? -ne 0 ]; then
    echo "错误：无法激活conda环境"
    exit 1
fi

# 检查app.py是否存在
if [ ! -f "app.py" ]; then
    echo "错误：找不到 app.py 文件"
    exit 1
fi

echo "后端服务启动中..."
echo "按 Ctrl+C 停止服务"

# 启动后端应用
python app.py
