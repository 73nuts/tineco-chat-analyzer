# Tineco聊天记录分析系统

一个用于分析Tineco添可官方旗舰店聊天记录的Web应用系统，支持Excel文件上传、自动化分析和可视化报告展示。

## 项目结构

```
tineco-chat-analyzer/
├── frontend/           # 前端Vue.js应用
│   ├── src/
│   │   ├── components/ # 公共组件
│   │   ├── views/      # 页面组件
│   │   ├── utils/      # 工具函数
│   │   └── api/        # API接口
│   ├── public/         # 静态资源
│   └── package.json    # 前端依赖配置
├── backend/            # 后端FastAPI应用
│   ├── app/
│   │   ├── api/        # API路由
│   │   ├── core/       # 核心配置
│   │   ├── models/     # 数据模型
│   │   └── services/   # 业务逻辑
│   ├── tests/          # 测试文件
│   └── requirements.txt # 后端依赖配置
└── docs/               # 项目文档
```

## 功能特性

- 📁 **文件上传**: 支持Excel聊天记录文件拖拽上传
- 📊 **数据分析**: 自动化聊天记录过滤和统计分析
- 📈 **可视化报告**: 图表展示分析结果和统计数据
- ⚙️ **配置管理**: 过滤规则和售后名单在线管理
- 📱 **响应式设计**: 支持桌面端和移动端访问

## 技术栈

### 前端
- Vue.js 3 + TypeScript
- Element Plus UI组件库
- ECharts图表库
- Vite构建工具

### 后端
- FastAPI (Python)
- SQLite数据库
- Pandas数据处理
- Celery异步任务队列

## 快速开始

### 前端开发
```bash
cd frontend
npm install
npm run dev
```

### 后端开发
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 开发进度

- [x] 项目初始化和结构搭建
- [ ] 前端基础框架搭建
- [ ] 后端API框架搭建
- [ ] 文件上传功能
- [ ] 分析引擎集成
- [ ] 结果展示页面
- [ ] 配置管理功能

## 贡献指南

1. Fork本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情
