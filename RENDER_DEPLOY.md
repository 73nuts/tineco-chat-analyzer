# 🚀 Render 免费部署指南

## Render优势
- ✅ **完全免费** - 无时间限制
- ✅ **自动构建** - Git推送自动部署
- ✅ **HTTPS** - 免费SSL证书
- ✅ **自定义域名** - 支持绑定域名

## 部署步骤

### 步骤1: 准备Git仓库

```bash
# 在项目根目录初始化Git
cd /Users/curtis/Desktop/tineco/建单过滤测试/tineco-chat-analyzer

# 如果还没有Git仓库
git init
git add .
git commit -m "Initial commit for Render deployment"

# 推送到GitHub (需要先在GitHub创建仓库)
# git remote add origin https://github.com/你的用户名/tineco-chat-analyzer.git
# git branch -M main
# git push -u origin main
```

### 步骤2: 部署后端到Render

1. **访问**: https://render.com/
2. **注册/登录**: 使用GitHub账户登录
3. **创建Web Service**:
   - 点击 "New +" → "Web Service"
   - 选择你的GitHub仓库
   - 配置如下：

#### 后端配置
```
Name: tineco-analyzer-backend
Environment: Python 3
Region: Oregon (US West)
Branch: main
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### 环境变量设置
```
DEBUG = False
UPLOAD_DIR = /tmp/uploads
MAX_FILE_SIZE = 52428800
ALLOWED_HOSTS = ["*"]
```

### 步骤3: 部署前端到Render

1. **创建Static Site**:
   - 点击 "New +" → "Static Site"
   - 选择同一个GitHub仓库

#### 前端配置
```
Name: tineco-analyzer-frontend
Branch: main
Root Directory: frontend
Build Command: npm install && npm run build
Publish Directory: frontend/dist
```

#### 环境变量设置
```
VITE_API_BASE_URL = https://你的后端服务名.onrender.com/api
```

### 步骤4: 更新CORS配置

后端部署完成后，获取后端URL（格式：`https://tineco-analyzer-backend.onrender.com`）

1. 在Render控制台，找到后端服务
2. 点击 "Environment" 
3. 更新 `ALLOWED_HOSTS`:
```
ALLOWED_HOSTS = ["https://你的前端服务名.onrender.com"]
```

### 步骤5: 验证部署

- **后端API**: https://tineco-analyzer-backend.onrender.com/docs
- **前端应用**: https://tineco-analyzer-frontend.onrender.com

## ⚠️ 重要提醒

### 免费服务限制
1. **自动睡眠**: 15分钟无活动后服务会睡眠
2. **冷启动**: 睡眠后首次访问需要等待30-60秒唤醒
3. **资源限制**: 512MB内存，0.1 CPU

### 解决方案
1. **保持活跃**: 可以设置定时ping服务（可选）
2. **用户提醒**: 在前端添加"服务唤醒中"提示
3. **预热访问**: 定期访问保持服务活跃

## 🎯 快速开始

如果你有GitHub仓库，现在就可以开始：

1. **访问**: https://render.com/
2. **连接GitHub**: 授权Render访问你的仓库
3. **创建后端服务**: 使用上面的后端配置
4. **创建前端服务**: 使用上面的前端配置
5. **更新CORS**: 配置正确的域名

## 没有GitHub？

我可以帮你：
1. 创建GitHub仓库
2. 推送代码
3. 连接到Render

准备好开始了吗？需要我帮你创建GitHub仓库吗？