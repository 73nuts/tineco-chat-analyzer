# 🚀 立即部署指南

## 步骤1: 部署后端到Railway

### 1.1 Railway登录和初始化
```bash
# 在backend目录下执行
cd backend

# 登录Railway (会打开浏览器)
railway login

# 创建新项目
railway init

# 如果提示选择，选择 "Empty Project"
```

### 1.2 配置环境变量
在Railway控制台设置以下环境变量：
```
DEBUG=False
PORT=8000
ALLOWED_HOSTS=["*"]
UPLOAD_DIR=/tmp/uploads
MAX_FILE_SIZE=52428800
```

### 1.3 部署后端
```bash
# 部署代码
railway up

# 部署完成后，获取Railway URL
railway status
```

**重要**: 复制Railway给出的域名，格式类似：`https://xxx-production.up.railway.app`

## 步骤2: 配置前端API地址

### 2.1 创建生产环境配置
```bash
cd ../frontend

# 创建生产环境配置文件
echo "VITE_API_BASE_URL=https://你的railway域名.railway.app/api" > .env.production
```

**注意**: 替换上面的Railway域名为步骤1.3中获得的实际域名

### 2.2 测试前端构建
```bash
# 安装依赖（如果需要）
npm install

# 构建前端
npm run build

# 检查构建是否成功
ls dist/
```

## 步骤3: 部署前端到Vercel

### 3.1 登录Vercel
```bash
# 登录Vercel (会打开浏览器)
vercel login
```

### 3.2 部署前端
```bash
# 部署到生产环境
vercel --prod

# 如果是首次部署，会提示：
# ? Set up and deploy "~/frontend"? [Y/n] y
# ? Which scope do you want to deploy to? (选择你的团队/个人账户)
# ? Link to existing project? [y/N] n
# ? What's your project's name? tineco-chat-analyzer
# ? In which directory is your code located? ./
```

## 步骤4: 更新CORS配置

### 4.1 获取前端域名
Vercel部署完成后会给出前端URL，类似：`https://tineco-chat-analyzer-xxx.vercel.app`

### 4.2 更新后端CORS
在Railway控制台更新环境变量：
```
ALLOWED_HOSTS=["https://你的vercel域名.vercel.app"]
```

### 4.3 重新部署后端
```bash
cd backend
railway up
```

## 步骤5: 验证部署

### 5.1 访问前端应用
打开Vercel给出的URL，测试：
- ✅ 页面正常加载
- ✅ 配置页面正常显示
- ✅ 文件上传功能正常
- ✅ Excel解析功能正常

### 5.2 检查网络请求
在浏览器开发者工具Network标签中，确认：
- ✅ API请求指向正确的Railway域名
- ✅ 没有CORS错误
- ✅ 接口返回正常

## 🎉 部署完成！

**后端**: https://你的项目.railway.app  
**前端**: https://你的项目.vercel.app  

## 快速命令参考

```bash
# 后端重新部署
cd backend && railway up

# 前端重新部署  
cd frontend && npm run build && vercel --prod

# 查看后端日志
railway logs

# 查看Vercel部署状态
vercel list
```

## 遇到问题？

### 常见问题解决：

1. **CORS错误**: 检查Railway环境变量中的ALLOWED_HOSTS
2. **API请求失败**: 确认前端.env.production中的API URL正确
3. **文件上传失败**: 检查文件大小限制和Railway存储配置
4. **构建失败**: 检查package.json中的dependencies

### 获取帮助：
- Railway文档: https://docs.railway.app
- Vercel文档: https://vercel.com/docs

---

**准备好了吗？开始执行步骤1！** 🚀