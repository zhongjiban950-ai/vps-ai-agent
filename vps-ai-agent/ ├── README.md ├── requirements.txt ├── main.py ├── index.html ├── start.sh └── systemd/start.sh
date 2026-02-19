#!/bin/bash

echo "======================================"
echo "VPS AI Agent 启动脚本"
echo "======================================"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "检查依赖..."
pip install -q -r requirements.txt

# 停止旧进程
echo "停止旧进程..."
pkill -f "python3 main.py"

# 启动服务
echo "启动 AI Agent 服务..."
nohup python3 main.py > agent.log 2>&1 &

echo "======================================"
echo "✅ 服务已启动"
echo "访问地址: http://localhost:30800"
echo "日志文件: agent.log"
echo "======================================"
