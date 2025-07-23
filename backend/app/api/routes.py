#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import APIRouter
from app.api.endpoints import upload, analysis, config, system

# 创建主路由器
api_router = APIRouter()

# 注册各个功能模块的路由
api_router.include_router(upload.router, prefix="/upload", tags=["文件上传"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["分析管理"])
api_router.include_router(config.router, prefix="/config", tags=["配置管理"])
api_router.include_router(system.router, prefix="/system", tags=["系统管理"])
