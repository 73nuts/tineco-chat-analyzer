# 🚀 快速部署指南

## 推荐免费部署方案

### Railway + Vercel (完全免费)

**1. 后端 → Railway**
- 免费额度：512MB内存，500小时运行时间/月
- 支持：Python、自动SSL、环境变量
- 部署：`./deploy.sh` 选择选项1

**2. 前端 → Vercel**
- 免费额度：100GB带宽、无限静态部署
- 支持：自动构建、CDN、自定义域名
- 部署：自动集成GitHub

## 快速开始

```bash
# 1. 运行部署脚本
./deploy.sh

# 2. 或手动部署
# 后端
cd backend
railway up

# 前端  
cd frontend
npm run build
vercel --prod
```

## 关键配置

### 后端环境变量
```bash
PORT=8000
DEBUG=False
ALLOWED_HOSTS=["https://your-frontend.vercel.app"]
UPLOAD_DIR=/tmp/uploads
```

### 前端环境变量
```bash
VITE_API_BASE_URL=https://your-backend.railway.app/api
```

## 成本预估

- **完全免费**：Railway + Vercel
- **升级版**：$5/月 Railway Pro + 免费 Vercel

## 支持功能

✅ 文件上传 (最大50MB)  
✅ Excel解析  
✅ 聊天记录分析  
✅ 实时进度显示  
✅ HTTPS安全连接  

## 需要帮助？

查看详细部署文档：`deploy.md`