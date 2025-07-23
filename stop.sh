#!/bin/bash

# Tineco聊天记录分析系统停止脚本

echo "🛑 停止 Tineco聊天记录分析系统..."

# 停止后端服务
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        echo "停止后端服务器 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        sleep 2
        if ps -p $BACKEND_PID > /dev/null; then
            echo "强制停止后端服务器..."
            kill -9 $BACKEND_PID
        fi
    fi
    rm -f .backend.pid
fi

# 停止前端服务
if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        echo "停止前端服务器 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        sleep 2
        if ps -p $FRONTEND_PID > /dev/null; then
            echo "强制停止前端服务器..."
            kill -9 $FRONTEND_PID
        fi
    fi
    rm -f .frontend.pid
fi

# 清理可能的其他进程
echo "清理相关进程..."
pkill -f "uvicorn app.main:app"
pkill -f "vite"

echo "✅ 系统已停止"
