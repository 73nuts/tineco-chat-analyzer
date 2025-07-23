#!/bin/bash

# Tineco聊天记录分析系统启动脚本

echo "🚀 启动 Tineco聊天记录分析系统..."

# 检查Python版本
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ 错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查Node.js版本
node --version
if [ $? -ne 0 ]; then
    echo "❌ 错误: 未找到Node.js，请先安装Node.js"
    exit 1
fi

echo "📦 安装后端依赖..."
cd backend
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

echo "📦 安装前端依赖..."
cd ../frontend
npm install

echo "🔧 启动后端服务器..."
cd ../backend
source venv/bin/activate
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!
echo "后端服务器已启动 (PID: $BACKEND_PID)"

echo "🔧 启动前端开发服务器..."
cd ../frontend
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端服务器已启动 (PID: $FRONTEND_PID)"

echo "✅ 系统启动完成!"
echo ""
echo "📋 访问地址:"
echo "   前端应用: http://localhost:3000"
echo "   后端API: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo ""
echo "📝 日志文件:"
echo "   后端日志: backend/backend.log"
echo "   前端日志: frontend/frontend.log"
echo ""
echo "🛑 停止服务: ./stop.sh"
echo ""

# 保存PID到文件
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo "🎉 系统已就绪，请在浏览器中访问 http://localhost:3000"
