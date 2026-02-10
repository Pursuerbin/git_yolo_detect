#!/bin/bash

# 同时启动前后端服务 - 使用screen

echo "正在启动前后端服务..."

# 创建两个screen会话分别运行前后端
echo "启动前端服务..."
screen -dmS frontend bash -c "cd ~/project/frontend && . ~/.nvm/nvm.sh && npm run dev"

echo "启动后端服务..."
screen -dmS backend bash -c "cd ~/project/backend && source ~/miniconda3/bin/activate flask && python app.py"

echo "已启动前后端服务！"
echo ""
echo "查看前端日志: screen -r frontend"
echo "查看后端日志: screen -r backend"
echo "退出screen会话: 按 Ctrl+A 然后按 D"
echo "杀死screen会话: screen -S frontend -X quit 或 screen -S backend -X quit"
