#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import uuid
import asyncio
from datetime import datetime
from typing import Dict, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from concurrent.futures import ThreadPoolExecutor

from app.models.schemas import (
    AnalysisRequest, AnalysisTask, AnalysisStatus, 
    AnalysisResult, ApiResponse, FilterDetailResponse,
    FilteredRecord
)
from app.services.analyzer import analyzer
from app.api.endpoints.upload import get_file_path

router = APIRouter()

# 存储分析任务的内存字典（生产环境应使用数据库和消息队列）
analysis_tasks = {}
executor = ThreadPoolExecutor(max_workers=3)  # 限制并发分析任务数

class ProgressTracker:
    """进度跟踪器"""
    def __init__(self, task_id: str):
        self.task_id = task_id
    
    def update_progress(self, progress: float, message: str = ""):
        """更新任务进度"""
        if self.task_id in analysis_tasks:
            analysis_tasks[self.task_id]["progress"] = progress
            analysis_tasks[self.task_id]["status_message"] = message
            print(f"任务 {self.task_id}: {progress}% - {message}")

def run_analysis_sync(task_id: str, file_path: str) -> None:
    """同步执行分析任务"""
    try:
        # 更新任务状态
        analysis_tasks[task_id]["status"] = AnalysisStatus.PROCESSING
        analysis_tasks[task_id]["started_time"] = datetime.now()
        
        # 创建进度跟踪器
        progress_tracker = ProgressTracker(task_id)
        
        # 执行分析
        result = analyzer.analyze_excel(
            file_path, 
            progress_callback=progress_tracker.update_progress
        )
        
        # 更新任务完成状态
        analysis_tasks[task_id]["status"] = AnalysisStatus.COMPLETED
        analysis_tasks[task_id]["completed_time"] = datetime.now()
        analysis_tasks[task_id]["progress"] = 100.0
        analysis_tasks[task_id]["result"] = result
        analysis_tasks[task_id]["status_message"] = "分析完成"
        
    except Exception as e:
        # 更新任务失败状态
        analysis_tasks[task_id]["status"] = AnalysisStatus.FAILED
        analysis_tasks[task_id]["completed_time"] = datetime.now()
        analysis_tasks[task_id]["error_message"] = str(e)
        analysis_tasks[task_id]["status_message"] = f"分析失败: {str(e)}"
        print(f"分析任务 {task_id} 失败: {e}")

@router.post("/start", response_model=ApiResponse)
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    开始分析任务
    
    - **file_id**: 要分析的文件ID
    - **filter_rules**: 可选的过滤规则配置
    """
    try:
        # 验证文件是否存在
        try:
            file_path = get_file_path(request.file_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 创建分析任务记录
        task = AnalysisTask(
            task_id=task_id,
            file_id=request.file_id,
            filename=f"文件_{request.file_id}",  # 可以从上传记录中获取真实文件名
            status=AnalysisStatus.PENDING,
            created_time=datetime.now(),
            progress=0.0
        )
        
        # 存储任务信息
        analysis_tasks[task_id] = {
            **task.dict(),
            "status_message": "等待开始分析"
        }
        
        # 如果提供了自定义过滤规则，更新分析器配置
        if request.filter_rules:
            # 这里可以临时更新过滤规则，或者为每个任务创建独立的分析器实例
            pass
        
        # 提交后台任务
        loop = asyncio.get_event_loop()
        loop.run_in_executor(
            executor,
            run_analysis_sync,
            task_id,
            file_path
        )
        
        return ApiResponse(
            success=True,
            message="分析任务已启动",
            data={"task_id": task_id, "status": "pending"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"启动分析任务失败: {str(e)}"
        )

@router.get("/tasks/{task_id}", response_model=ApiResponse)
async def get_task_status(task_id: str):
    """获取分析任务状态"""
    try:
        if task_id not in analysis_tasks:
            raise HTTPException(
                status_code=404,
                detail="任务不存在"
            )
        
        task_info = analysis_tasks[task_id].copy()
        
        return ApiResponse(
            success=True,
            message="获取任务状态成功",
            data=task_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取任务状态失败: {str(e)}"
        )

@router.get("/tasks", response_model=ApiResponse)
async def list_analysis_tasks():
    """获取所有分析任务列表"""
    try:
        tasks_list = []
        for task_id, task_info in analysis_tasks.items():
            tasks_list.append({
                "task_id": task_id,
                "file_id": task_info["file_id"],
                "filename": task_info["filename"],
                "status": task_info["status"],
                "created_time": task_info["created_time"],
                "progress": task_info["progress"],
                "status_message": task_info.get("status_message", "")
            })
        
        # 按创建时间倒序排列
        tasks_list.sort(key=lambda x: x["created_time"], reverse=True)
        
        return ApiResponse(
            success=True,
            message="获取任务列表成功",
            data={"tasks": tasks_list, "total": len(tasks_list)}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取任务列表失败: {str(e)}"
        )

@router.get("/tasks/{task_id}/result", response_model=ApiResponse)
async def get_analysis_result(task_id: str):
    """获取分析结果"""
    try:
        if task_id not in analysis_tasks:
            raise HTTPException(
                status_code=404,
                detail="任务不存在"
            )
        
        task_info = analysis_tasks[task_id]
        
        if task_info["status"] != AnalysisStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"任务尚未完成，当前状态: {task_info['status']}"
            )
        
        if "result" not in task_info or task_info["result"] is None:
            raise HTTPException(
                status_code=404,
                detail="分析结果不存在"
            )
        
        return ApiResponse(
            success=True,
            message="获取分析结果成功",
            data={
                "task_id": task_id,
                "result": task_info["result"],
                "completed_time": task_info["completed_time"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取分析结果失败: {str(e)}"
        )

@router.delete("/tasks/{task_id}", response_model=ApiResponse)
async def cancel_or_delete_task(task_id: str):
    """取消或删除分析任务"""
    try:
        if task_id not in analysis_tasks:
            raise HTTPException(
                status_code=404,
                detail="任务不存在"
            )
        
        task_info = analysis_tasks[task_id]
        
        # 如果任务正在运行，这里应该实现取消逻辑
        # 由于使用了ThreadPoolExecutor，取消正在运行的任务比较复杂
        # 在生产环境中，建议使用Celery等支持任务取消的队列系统
        
        if task_info["status"] == AnalysisStatus.PROCESSING:
            # 标记为取消状态（实际的取消逻辑需要在分析函数中检查这个状态）
            analysis_tasks[task_id]["status"] = "cancelled"
            analysis_tasks[task_id]["status_message"] = "任务已取消"
        
        # 删除任务记录
        del analysis_tasks[task_id]
        
        return ApiResponse(
            success=True,
            message="任务已删除",
            data={"task_id": task_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除任务失败: {str(e)}"
        )

@router.get("/stats", response_model=ApiResponse)
async def get_analysis_stats():
    """获取分析统计信息"""
    try:
        total_tasks = len(analysis_tasks)
        completed_tasks = sum(1 for task in analysis_tasks.values() 
                            if task["status"] == AnalysisStatus.COMPLETED)
        processing_tasks = sum(1 for task in analysis_tasks.values() 
                             if task["status"] == AnalysisStatus.PROCESSING)
        failed_tasks = sum(1 for task in analysis_tasks.values() 
                         if task["status"] == AnalysisStatus.FAILED)
        
        # 计算平均过滤率
        completed_results = [task["result"] for task in analysis_tasks.values() 
                           if task["status"] == AnalysisStatus.COMPLETED and "result" in task]
        avg_filter_rate = 0.0
        if completed_results:
            avg_filter_rate = sum(result.filter_rate for result in completed_results) / len(completed_results)
        
        stats = {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "processing_tasks": processing_tasks,
            "failed_tasks": failed_tasks,
            "average_filter_rate": round(avg_filter_rate, 2)
        }
        
        return ApiResponse(
            success=True,
            message="获取统计信息成功",
            data=stats
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取统计信息失败: {str(e)}"
        )

@router.get("/tasks/{task_id}/filter-details/{filter_type}", response_model=ApiResponse)
async def get_filter_details(task_id: str, filter_type: str, page: int = 1, page_size: int = 50):
    """获取特定过滤类型的详细记录"""
    try:
        if task_id not in analysis_tasks:
            raise HTTPException(
                status_code=404,
                detail="任务不存在"
            )
        
        task_info = analysis_tasks[task_id]
        
        if task_info["status"] != AnalysisStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"任务尚未完成，当前状态: {task_info['status']}"
            )
        
        if "result" not in task_info or not hasattr(task_info["result"], "filtered_records_details"):
            raise HTTPException(
                status_code=404,
                detail="过滤详情数据不存在"
            )
        
        # 获取所有过滤记录
        all_filtered_records = task_info["result"].filtered_records_details
        
        # 按过滤类型筛选
        filtered_by_type = [
            record for record in all_filtered_records 
            if record.filter_type == filter_type
        ]
        
        # 计算分页
        total_count = len(filtered_by_type)
        total_pages = (total_count + page_size - 1) // page_size
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_records = filtered_by_type[start_idx:end_idx]
        
        # 构建响应
        filter_detail_response = FilterDetailResponse(
            filter_type=filter_type,
            total_count=total_count,
            records=page_records,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
        return ApiResponse(
            success=True,
            message=f"获取{filter_type}过滤详情成功",
            data=filter_detail_response.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取过滤详情失败: {str(e)}"
        )

@router.get("/tasks/{task_id}/chat-record/{record_id}", response_model=ApiResponse)
async def get_chat_record_detail(task_id: str, record_id: str):
    """获取具体聊天记录的完整内容"""
    try:
        if task_id not in analysis_tasks:
            raise HTTPException(
                status_code=404,
                detail="任务不存在"
            )
        
        task_info = analysis_tasks[task_id]
        
        if "result" not in task_info or not hasattr(task_info["result"], "filtered_records_details"):
            raise HTTPException(
                status_code=404,
                detail="记录详情数据不存在"
            )
        
        # 查找具体记录
        all_filtered_records = task_info["result"].filtered_records_details
        target_record = None
        
        for record in all_filtered_records:
            if record.record_id == record_id:
                target_record = record
                break
        
        if not target_record:
            raise HTTPException(
                status_code=404,
                detail="记录不存在"
            )
        
        return ApiResponse(
            success=True,
            message="获取聊天记录详情成功",
            data={
                "record_id": record_id,
                "filter_info": {
                    "filter_type": target_record.filter_type,
                    "filter_reason": target_record.filter_reason,
                    "staff_name": target_record.staff_name,
                    "timestamp": target_record.timestamp,
                    "address_content": target_record.address_content,
                    "error_message": target_record.error_message,
                    "service_message": target_record.service_message
                },
                "raw_data": target_record.raw_data
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取聊天记录详情失败: {str(e)}"
        )
