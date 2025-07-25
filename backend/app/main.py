#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import api_router
from app.core.config import settings

# 创建FastAPI应用实例
app = FastAPI(
    title="Tineco聊天记录分析系统",
    description="用于分析Tineco添可官方旗舰店聊天记录的Web应用系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS中间件
# 确保包含前端域名
allowed_origins = settings.ALLOWED_HOSTS.copy()
if "https://tineco-analyzer-frontend.onrender.com" not in allowed_origins:
    allowed_origins.append("https://tineco-analyzer-frontend.onrender.com")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录（如果目录存在）
import os
static_dir = "static"
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 注册API路由
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "Tineco聊天记录分析系统API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
