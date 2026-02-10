#!/bin/bash

# 启动前端服务脚本

echo "正在启动前端服务..."

# 切换到前端目录
cd ~/project/frontend

# 检查目录是否存在
if [ $? -ne 0 ]; then
    echo "错误：无法进入前端目录"
    exit 1
fi

# 加载nvm环境
. ~/.nvm/nvm.sh

# 检查nvm是否加载成功
if ! command -v nvm &> /dev/null; then
    echo "错误：无法加载nvm"
    exit 1
fi

# 检查npm是否存在
if ! command -v npm &> /dev/null; then
    echo "错误：npm命令未找到"
    exit 1
fi

echo "前端服务启动中..."
echo "按 Ctrl+C 停止服务"

# 启动前端开发服务器
npm run dev
