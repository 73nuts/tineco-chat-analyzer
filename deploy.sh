#!/bin/bash

# Tineco Chat Analyzer 部署脚本

echo "🚀 Tineco Chat Analyzer 部署助手"
echo "=================================="

# 检查部署目标
echo "请选择部署平台："
echo "1) Railway + Vercel (推荐)"
echo "2) Render"
echo "3) 本地测试构建"
read -p "请输入选择 (1-3): " choice

case $choice in
  1)
    echo "📦 准备 Railway + Vercel 部署..."
    
    # 检查CLI工具
    if ! command -v railway &> /dev/null; then
      echo "❌ Railway CLI 未安装，请先安装："
      echo "npm install -g @railway/cli"
      exit 1
    fi
    
    if ! command -v vercel &> /dev/null; then
      echo "❌ Vercel CLI 未安装，请先安装："
      echo "npm install -g vercel"
      exit 1
    fi
    
    # 部署后端到Railway
    echo "🔧 部署后端到 Railway..."
    cd backend
    railway login
    railway init
    railway up
    
    # 获取Railway URL
    echo "📝 请复制 Railway 部署后的 URL，更新前端配置"
    read -p "输入 Railway 后端 URL (例: https://xxx.railway.app): " backend_url
    
    # 更新前端配置
    cd ../frontend
    echo "VITE_API_BASE_URL=${backend_url}/api" > .env.production
    
    # 部署前端到Vercel
    echo "🔧 部署前端到 Vercel..."
    npm run build
    vercel --prod
    
    echo "✅ 部署完成！请在 Vercel 控制台查看前端 URL"
    ;;
    
  2)
    echo "📦 准备 Render 部署..."
    echo "请手动在 Render 控制台创建服务："
    echo "1. 创建 Web Service (后端): Python, 构建命令: pip install -r requirements.txt"
    echo "2. 创建 Static Site (前端): 构建命令: cd frontend && npm install && npm run build"
    ;;
    
  3)
    echo "🔧 本地测试构建..."
    
    # 构建后端
    echo "📦 安装后端依赖..."
    cd backend
    pip install -r requirements.txt
    
    # 构建前端
    echo "📦 构建前端..."
    cd ../frontend
    npm install
    npm run build
    
    echo "✅ 构建完成！"
    echo "前端构建文件在: frontend/dist"
    echo "启动后端: cd backend && python -m app.main"
    ;;
    
  *)
    echo "❌ 无效选择"
    exit 1
    ;;
esac

echo ""
echo "🎉 部署流程完成！"
echo "📚 更多详细信息请参考 deploy.md"