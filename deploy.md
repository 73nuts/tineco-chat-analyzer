# 部署指南

## 方案一：Railway 全栈部署

### 后端部署到 Railway

1. **准备后端配置文件**

在 `backend` 目录创建以下文件：

```bash
# Procfile
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT

# runtime.txt (可选，指定Python版本)
python-3.9.18
```

2. **修改后端配置**

在 `backend/app/main.py` 中添加 CORS 配置和端口配置：

```python
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Tineco Chat Analyzer")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 端口配置
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

3. **部署到 Railway**

```bash
# 安装 Railway CLI
npm install -g @railway/cli

# 登录
railway login

# 初始化项目
railway init

# 部署后端
cd backend
railway up
```

### 前端部署到 Vercel

1. **修改前端 API 配置**

在 `frontend/src/api/index.ts` 中：

```typescript
const api = axios.create({
  baseURL: process.env.NODE_ENV === 'production' 
    ? 'https://your-railway-app.railway.app/api'  // 替换为实际的Railway URL
    : '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})
```

2. **构建和部署**

```bash
cd frontend
npm run build

# 使用 Vercel CLI 部署
npm install -g vercel
vercel --prod
```

## 方案二：Render 部署

### 后端部署

1. **创建 render.yaml**

```yaml
services:
  - type: web
    name: tineco-analyzer-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.18
```

2. **前端静态站点部署**

在 Render 控制台创建静态站点，构建命令：
```bash
cd frontend && npm install && npm run build
```

发布目录：`frontend/dist`

## 方案三：免费组合方案

- **后端**: Railway 或 Render
- **前端**: Vercel 或 Netlify
- **文件存储**: 如需持久化存储，使用 Supabase Storage (免费)

## 环境变量配置

### 后端环境变量
```
PORT=8000
CORS_ORIGINS=https://your-frontend-domain.vercel.app
UPLOAD_DIR=/tmp/uploads
MAX_FILE_SIZE=10485760
```

### 前端环境变量
```
VITE_API_BASE_URL=https://your-backend-domain.railway.app/api
```

## 注意事项

1. **文件上传限制**: 免费服务器通常有文件大小限制
2. **数据持久化**: 免费层的文件系统可能不持久，考虑使用云存储
3. **域名**: 可以使用免费的 .vercel.app 或 .railway.app 域名
4. **HTTPS**: 上述平台都自动提供 HTTPS

## 成本预估

- **完全免费**: Vercel前端 + Railway后端 (每月有使用限制)
- **低成本**: $5-10/月 可获得更好的性能和更高限制

## 部署检查清单

- [ ] 后端 CORS 配置正确
- [ ] 前端 API URL 指向正确的后端地址
- [ ] 环境变量配置完成
- [ ] 文件上传功能测试通过
- [ ] Excel解析功能正常工作
- [ ] 页面路由正确配置