# 🚀 73nuts 专属部署指南

## GitHub仓库 ✅
**仓库地址**: https://github.com/73nuts/tineco-chat-analyzer  
**状态**: 代码已推送成功！

## 立即开始Render部署 🚀

### 步骤1: 访问Render
👉 **点击访问**: https://render.com/

### 步骤2: 连接GitHub
1. 点击 **"Sign Up"** 或 **"Log In"**
2. 选择 **"Continue with GitHub"**
3. 授权Render访问你的GitHub账户

### 步骤3: 部署后端服务

#### 3.1 创建Web Service
1. 在Render控制台，点击 **"New +"**
2. 选择 **"Web Service"**
3. 找到并选择 **"73nuts/tineco-chat-analyzer"** 仓库

#### 3.2 后端配置
```
Service Name: tineco-analyzer-backend
Environment: Python 3
Region: Oregon (US West)
Branch: main
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
Plan: Free
```

#### 3.3 环境变量设置
在 "Advanced" 部分添加环境变量：
```
DEBUG = False
UPLOAD_DIR = /tmp/uploads
MAX_FILE_SIZE = 52428800
ALLOWED_HOSTS = ["*"]
```

#### 3.4 创建服务
点击 **"Create Web Service"**，等待部署完成（约3-5分钟）

### 步骤4: 部署前端服务

#### 4.1 创建Static Site
1. 回到Render首页，点击 **"New +"**
2. 选择 **"Static Site"**
3. 再次选择 **"73nuts/tineco-chat-analyzer"** 仓库

#### 4.2 前端配置
```
Site Name: tineco-analyzer-frontend
Branch: main
Root Directory: frontend
Build Command: npm install && npm run build
Publish Directory: dist
```

#### 4.3 重要：前端环境变量
在 "Advanced" 部分添加（替换为实际的后端URL）：
```
VITE_API_BASE_URL = https://tineco-analyzer-backend-XXX.onrender.com/api
```

**注意**: 等后端部署完成后，复制实际的后端URL来替换上面的XXX部分！

#### 4.4 创建静态站点
点击 **"Create Static Site"**

### 步骤5: 更新CORS配置

#### 5.1 获取服务URL
部署完成后，你会得到类似这样的URL：
- 后端: `https://tineco-analyzer-backend-xxx.onrender.com`
- 前端: `https://tineco-analyzer-frontend-xxx.onrender.com`

#### 5.2 更新后端CORS
1. 进入后端服务的设置页面
2. 点击 "Environment" 标签
3. 修改 `ALLOWED_HOSTS` 环境变量：
```
ALLOWED_HOSTS = ["https://tineco-analyzer-frontend-xxx.onrender.com"]
```
4. 保存更改，服务会自动重新部署

## 🎯 验证部署

### 检查服务状态
- ✅ 后端服务显示 "Live"
- ✅ 前端服务显示 "Live"
- ✅ 构建日志无错误

### 功能测试
1. **访问前端**: 打开前端URL
2. **测试配置页**: 查看售后人员管理
3. **测试文件上传**: 尝试上传Excel文件
4. **检查API**: 访问 `后端URL/docs` 查看API文档

## 🚨 可能遇到的问题

### 1. 构建失败
- 检查构建日志中的错误信息
- 确认 `requirements.txt` 和 `package.json` 正确

### 2. CORS错误
- 确保 `ALLOWED_HOSTS` 包含正确的前端域名
- 检查前端的 `VITE_API_BASE_URL` 是否正确

### 3. 服务睡眠
- 免费服务15分钟无活动后会睡眠
- 首次访问需要30-60秒唤醒

## 🎉 部署完成！

恭喜！你的Tineco聊天分析系统现在已经在线运行了！

**你的应用链接**:
- 🌐 前端应用: `https://tineco-analyzer-frontend-xxx.onrender.com`
- 🔧 后端API: `https://tineco-analyzer-backend-xxx.onrender.com`
- 📖 API文档: `https://tineco-analyzer-backend-xxx.onrender.com/docs`

---

**现在就开始** → https://render.com/ 🚀

有问题随时问我！