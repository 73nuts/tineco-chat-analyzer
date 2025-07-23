# Tineco聊天记录分析系统 - 部署指南

## 系统要求

### 软件依赖
- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 硬件要求
- 内存: 最少 2GB，推荐 4GB+
- 磁盘: 最少 1GB 可用空间
- CPU: 双核心以上

## 快速开始

### 1. 克隆项目
```bash
cd /Users/curtis/Desktop/tineco/建单过滤测试/tineco-chat-analyzer
```

### 2. 一键启动
```bash
./start.sh
```

### 3. 访问系统
- 前端应用: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 4. 停止系统
```bash
./stop.sh
```

## 手动部署

### 后端部署

1. 进入后端目录
```bash
cd backend
```

2. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 启动后端服务
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 前端部署

1. 进入前端目录
```bash
cd frontend
```

2. 安装依赖
```bash
npm install
```

3. 启动开发服务器
```bash
npm run dev
```

4. 构建生产版本
```bash
npm run build
```

## 配置说明

### 后端配置 (backend/.env)
```env
DEBUG=true                    # 调试模式
HOST=0.0.0.0                 # 服务器地址
PORT=8000                    # 服务器端口
MAX_FILE_SIZE=52428800       # 最大文件大小 (50MB)
UPLOAD_DIR=./uploads         # 文件上传目录
STAFF_CONFIG_PATH=./config/售后名单.json  # 售后名单配置
```

### 前端配置 (frontend/vite.config.ts)
```typescript
server: {
  port: 3000,                # 前端端口
  proxy: {
    '/api': {
      target: 'http://localhost:8000',  # 后端API地址
      changeOrigin: true
    }
  }
}
```

## 功能验证

### 1. 文件上传测试
1. 访问首页 http://localhost:3000
2. 上传一个Excel文件（.xlsx或.xls格式）
3. 检查文件是否成功上传

### 2. 分析功能测试
1. 在文件列表中点击"开始分析"
2. 查看分析进度
3. 分析完成后查看结果报告

### 3. 配置管理测试
1. 访问配置管理页面
2. 查看和修改过滤规则
3. 管理售后人员名单

### 4. 系统状态测试
1. 访问系统状态页面
2. 检查系统健康状态
3. 查看系统统计信息

## 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 查看端口占用
   lsof -i :8000
   lsof -i :3000
   
   # 杀死占用进程
   kill -9 <PID>
   ```

2. **Python依赖安装失败**
   ```bash
   # 升级pip
   pip install --upgrade pip
   
   # 使用国内镜像
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
   ```

3. **前端依赖安装失败**
   ```bash
   # 清除缓存
   npm cache clean --force
   
   # 使用yarn替代npm
   yarn install
   ```

4. **文件上传失败**
   - 检查文件大小是否超过50MB
   - 确认文件格式为.xlsx或.xls
   - 检查uploads目录权限

5. **分析任务失败**
   - 检查Excel文件格式是否正确
   - 查看后端日志获取详细错误信息
   - 确认售后名单配置文件存在

### 日志查看

- 后端日志: `backend/backend.log`
- 前端日志: `frontend/frontend.log`
- 系统日志: 通过系统状态页面查看

## 生产环境部署

### 使用Docker部署

1. 创建Dockerfile (后端)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. 创建Dockerfile (前端)
```dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

### 使用Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 维护建议

1. **定期备份**
   - 备份数据库文件
   - 备份配置文件
   - 备份用户上传的文件

2. **监控系统**
   - 监控磁盘空间使用
   - 监控内存使用情况
   - 定期清理临时文件

3. **安全建议**
   - 定期更新依赖包
   - 使用HTTPS协议
   - 限制文件上传大小和类型

4. **性能优化**
   - 使用Redis缓存
   - 配置数据库连接池
   - 启用Gzip压缩

## 联系支持

如遇到问题，请查看：
1. 项目README.md文件
2. API文档: http://localhost:8000/docs
3. 系统日志和错误信息
