#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    """应用配置类"""
    
    # 基础配置
    PROJECT_NAME: str = "Tineco聊天记录分析系统"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # 服务器配置
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # CORS配置
    ALLOWED_HOSTS: List[str] = Field(
        default=["*"],  # 允许所有来源，适用于开发环境
        env="ALLOWED_HOSTS"
    )
    
    # 数据库配置
    DATABASE_URL: str = Field(
        default="sqlite:///./chat_analyzer.db",
        env="DATABASE_URL"
    )
    
    # 文件上传配置
    UPLOAD_DIR: str = Field(default="./uploads", env="UPLOAD_DIR")
    MAX_FILE_SIZE: int = Field(default=50 * 1024 * 1024, env="MAX_FILE_SIZE")  # 50MB
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".xlsx", ".xls"],
        env="ALLOWED_EXTENSIONS"
    )
    
    # Redis配置（用于Celery）
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # 分析配置
    MAX_CONCURRENT_ANALYSIS: int = Field(default=3, env="MAX_CONCURRENT_ANALYSIS")
    ANALYSIS_TIMEOUT: int = Field(default=300, env="ANALYSIS_TIMEOUT")  # 5分钟
    
    # 售后人员配置文件路径
    STAFF_CONFIG_PATH: str = Field(
        default="./config/售后名单.json",
        env="STAFF_CONFIG_PATH"
    )
    
    # 过滤规则配置
    FILTER_RULES_CONFIG: dict = {
        "early_morning_filter": {
            "enabled": True,
            "start_hour": 0,
            "end_hour": 8,
            "description": "过滤早晨消息(0-8点)"
        },
        "staff_filter": {
            "enabled": True,
            "description": "过滤售后人员参与的对话"
        },
        "service_assistant_filter": {
            "enabled": True,
            "description": "过滤纯服务助手消息"
        },
        "address_confirm_filter": {
            "enabled": True,
            "description": "过滤收货地址确认消息"
        }
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建全局配置实例
settings = Settings()

# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
