#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import psutil
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from app.models.schemas import ApiResponse, SystemStats
from app.core.config import settings

router = APIRouter()

# 系统启动时间
system_start_time = datetime.now()

@router.get("/health", response_model=ApiResponse)
async def health_check():
    """系统健康检查"""
    try:
        # 检查上传目录
        upload_dir_exists = os.path.exists(settings.UPLOAD_DIR)
        upload_dir_writable = os.access(settings.UPLOAD_DIR, os.W_OK) if upload_dir_exists else False
        
        # 检查磁盘空间
        disk_usage = psutil.disk_usage('/')
        free_space_gb = disk_usage.free / (1024**3)
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now(),
            "checks": {
                "upload_directory": {
                    "exists": upload_dir_exists,
                    "writable": upload_dir_writable,
                    "path": settings.UPLOAD_DIR
                },
                "disk_space": {
                    "free_space_gb": round(free_space_gb, 2),
                    "sufficient": free_space_gb > 1.0  # 至少1GB空闲空间
                },
                "memory": {
                    "available_mb": round(psutil.virtual_memory().available / (1024**2), 2),
                    "usage_percent": psutil.virtual_memory().percent
                }
            }
        }
        
        # 判断整体健康状态
        is_healthy = (
            upload_dir_exists and 
            upload_dir_writable and 
            free_space_gb > 1.0 and
            psutil.virtual_memory().percent < 90
        )
        
        health_status["status"] = "healthy" if is_healthy else "warning"
        
        return ApiResponse(
            success=True,
            message="系统健康检查完成",
            data=health_status
        )
        
    except Exception as e:
        return ApiResponse(
            success=False,
            message=f"健康检查失败: {str(e)}",
            data={"status": "error", "error": str(e)}
        )

@router.get("/stats", response_model=ApiResponse)
async def get_system_stats():
    """获取系统统计信息"""
    try:
        # 计算系统运行时间
        uptime = datetime.now() - system_start_time
        uptime_str = str(uptime).split('.')[0]  # 移除微秒
        
        # 统计上传文件数量
        upload_files_count = 0
        if os.path.exists(settings.UPLOAD_DIR):
            upload_files_count = len([f for f in os.listdir(settings.UPLOAD_DIR) 
                                    if os.path.isfile(os.path.join(settings.UPLOAD_DIR, f))])
        
        # 这里可以从数据库或缓存中获取更详细的统计信息
        # 目前使用模拟数据
        stats = SystemStats(
            total_files_processed=upload_files_count,
            total_records_analyzed=0,  # 需要从分析历史中统计
            average_filter_rate=0.0,   # 需要从分析结果中计算
            active_tasks=0,            # 需要从任务队列中获取
            system_uptime=uptime_str
        )
        
        return ApiResponse(
            success=True,
            message="获取系统统计信息成功",
            data=stats.dict()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取系统统计信息失败: {str(e)}"
        )

@router.get("/config", response_model=ApiResponse)
async def get_system_config():
    """获取系统配置信息"""
    try:
        config_info = {
            "project_name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "debug_mode": settings.DEBUG,
            "upload_config": {
                "max_file_size_mb": settings.MAX_FILE_SIZE / (1024 * 1024),
                "allowed_extensions": settings.ALLOWED_EXTENSIONS,
                "upload_directory": settings.UPLOAD_DIR
            },
            "analysis_config": {
                "max_concurrent_analysis": settings.MAX_CONCURRENT_ANALYSIS,
                "analysis_timeout_seconds": settings.ANALYSIS_TIMEOUT
            }
        }
        
        return ApiResponse(
            success=True,
            message="获取系统配置成功",
            data=config_info
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取系统配置失败: {str(e)}"
        )

@router.post("/cleanup", response_model=ApiResponse)
async def cleanup_system():
    """清理系统临时文件"""
    try:
        cleaned_files = 0
        cleaned_size = 0
        
        # 清理上传目录中的临时文件
        if os.path.exists(settings.UPLOAD_DIR):
            for filename in os.listdir(settings.UPLOAD_DIR):
                file_path = os.path.join(settings.UPLOAD_DIR, filename)
                if os.path.isfile(file_path):
                    # 删除超过24小时的文件
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if datetime.now() - file_mtime > timedelta(hours=24):
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        cleaned_files += 1
                        cleaned_size += file_size
        
        cleanup_result = {
            "cleaned_files": cleaned_files,
            "cleaned_size_mb": round(cleaned_size / (1024 * 1024), 2),
            "cleanup_time": datetime.now()
        }
        
        return ApiResponse(
            success=True,
            message=f"系统清理完成，清理了 {cleaned_files} 个文件",
            data=cleanup_result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"系统清理失败: {str(e)}"
        )

@router.get("/logs", response_model=ApiResponse)
async def get_system_logs():
    """获取系统日志（简化版本）"""
    try:
        # 这里可以实现真正的日志读取功能
        # 目前返回模拟的日志信息
        logs = [
            {
                "timestamp": datetime.now() - timedelta(minutes=5),
                "level": "INFO",
                "message": "系统启动完成"
            },
            {
                "timestamp": datetime.now() - timedelta(minutes=3),
                "level": "INFO", 
                "message": "文件上传服务就绪"
            },
            {
                "timestamp": datetime.now() - timedelta(minutes=1),
                "level": "INFO",
                "message": "分析引擎初始化完成"
            }
        ]
        
        return ApiResponse(
            success=True,
            message="获取系统日志成功",
            data={"logs": logs, "total": len(logs)}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取系统日志失败: {str(e)}"
        )
