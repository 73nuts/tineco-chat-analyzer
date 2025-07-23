#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import uuid
import aiofiles
import pandas as pd
import json
import io
from datetime import datetime
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.models.schemas import FileUploadResponse, ApiResponse, ErrorResponse
from app.core.config import settings

router = APIRouter()

# 存储上传文件信息的内存字典（生产环境应使用数据库）
uploaded_files = {}

def validate_file(file: UploadFile) -> None:
    """验证上传文件"""
    # 检查文件扩展名
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式。支持的格式: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # 检查文件大小（这里只能检查声明的大小，实际大小需要在读取时检查）
    if hasattr(file, 'size') and file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制。最大允许: {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
        )

def validate_chat_excel_format(file_path: str) -> dict:
    """验证聊天记录Excel文件格式"""
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        
        # 定义必需的列
        required_columns = ['platform', 'date', 'messages', 'user_nick', 'shop_name', 'users']
        missing_columns = []
        
        # 检查必需的列
        for col in required_columns:
            if col not in df.columns:
                missing_columns.append(col)
        
        if missing_columns:
            return {
                "valid": False,
                "error": f"Excel格式错误：缺少必需的列 {', '.join(missing_columns)}。请确保Excel文件包含聊天记录分析所需的所有列。"
            }
        
        # 验证messages列的JSON格式
        validation_errors = []
        sample_size = min(100, len(df))  # 只验证前100行作为样本
        
        for idx in range(sample_size):
            try:
                messages_value = df.iloc[idx]['messages']
                if pd.notna(messages_value):
                    if isinstance(messages_value, str):
                        json.loads(messages_value)
                    elif not isinstance(messages_value, list):
                        validation_errors.append(f"第{idx+2}行messages格式错误：应为JSON字符串或数组")
            except json.JSONDecodeError:
                validation_errors.append(f"第{idx+2}行messages JSON格式错误")
            except Exception as e:
                validation_errors.append(f"第{idx+2}行数据验证错误: {str(e)}")
            
            # 如果发现错误太多，提前退出
            if len(validation_errors) >= 5:
                break
        
        if validation_errors:
            return {
                "valid": False,
                "error": f"Excel格式校验失败：\n" + "\n".join(validation_errors[:5])
            }
        
        return {
            "valid": True,
            "total_rows": len(df),
            "columns": list(df.columns),
            "validated_rows": sample_size
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": f"Excel文件格式错误，无法解析: {str(e)}"
        }

@router.post("/", response_model=ApiResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    上传Excel聊天记录文件
    
    - **file**: 要上传的Excel文件 (.xlsx 或 .xls)
    """
    try:
        # 验证文件
        validate_file(file)
        
        # 生成唯一文件ID
        file_id = str(uuid.uuid4())
        
        # 确保上传目录存在
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # 生成安全的文件名
        file_ext = os.path.splitext(file.filename)[1]
        safe_filename = f"{file_id}{file_ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
        
        # 异步保存文件
        file_size = 0
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                file_size += len(chunk)
                
                # 检查文件大小
                if file_size > settings.MAX_FILE_SIZE:
                    # 删除已保存的部分文件
                    await f.close()
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    raise HTTPException(
                        status_code=400,
                        detail=f"文件大小超过限制。最大允许: {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
                    )
                
                await f.write(chunk)
        
        # 验证Excel文件格式
        validation_result = validate_chat_excel_format(file_path)
        
        if not validation_result["valid"]:
            # 删除格式不正确的文件
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail=validation_result["error"]
            )
        
        # 创建文件信息记录
        upload_time = datetime.now()
        file_info = FileUploadResponse(
            file_id=file_id,
            filename=file.filename,
            file_size=file_size,
            upload_time=upload_time,
            status="uploaded"
        )
        
        # 存储文件信息（生产环境应存储到数据库）
        uploaded_files[file_id] = {
            **file_info.dict(),
            "file_path": file_path,
            "safe_filename": safe_filename,
            "validation_info": validation_result
        }
        
        return ApiResponse(
            success=True,
            message=f"文件上传成功并通过格式验证（共{validation_result['total_rows']}行数据）",
            data={
                **file_info.dict(),
                "validation_info": {
                    "total_rows": validation_result["total_rows"],
                    "columns": validation_result["columns"],
                    "validated_rows": validation_result["validated_rows"]
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"文件上传失败: {str(e)}"
        )

@router.get("/files", response_model=ApiResponse)
async def list_uploaded_files():
    """获取已上传文件列表"""
    try:
        files_list = []
        for file_id, file_info in uploaded_files.items():
            # 检查文件是否仍然存在
            if os.path.exists(file_info["file_path"]):
                files_list.append({
                    "file_id": file_id,
                    "filename": file_info["filename"],
                    "file_size": file_info["file_size"],
                    "upload_time": file_info["upload_time"],
                    "status": file_info["status"]
                })
        
        return ApiResponse(
            success=True,
            message="获取文件列表成功",
            data={"files": files_list, "total": len(files_list)}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取文件列表失败: {str(e)}"
        )

@router.get("/files/{file_id}", response_model=ApiResponse)
async def get_file_info(file_id: str):
    """获取指定文件信息"""
    try:
        if file_id not in uploaded_files:
            raise HTTPException(
                status_code=404,
                detail="文件不存在"
            )
        
        file_info = uploaded_files[file_id]
        
        # 检查文件是否仍然存在
        if not os.path.exists(file_info["file_path"]):
            raise HTTPException(
                status_code=404,
                detail="文件已被删除"
            )
        
        return ApiResponse(
            success=True,
            message="获取文件信息成功",
            data={
                "file_id": file_id,
                "filename": file_info["filename"],
                "file_size": file_info["file_size"],
                "upload_time": file_info["upload_time"],
                "status": file_info["status"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取文件信息失败: {str(e)}"
        )

@router.delete("/files/{file_id}", response_model=ApiResponse)
async def delete_file(file_id: str):
    """删除指定文件"""
    try:
        if file_id not in uploaded_files:
            raise HTTPException(
                status_code=404,
                detail="文件不存在"
            )
        
        file_info = uploaded_files[file_id]
        
        # 删除物理文件
        if os.path.exists(file_info["file_path"]):
            os.remove(file_info["file_path"])
        
        # 从内存中删除文件信息
        del uploaded_files[file_id]
        
        return ApiResponse(
            success=True,
            message="文件删除成功",
            data={"file_id": file_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除文件失败: {str(e)}"
        )

def get_file_path(file_id: str) -> str:
    """获取文件路径（供其他模块使用）"""
    if file_id not in uploaded_files:
        raise ValueError(f"文件ID {file_id} 不存在")
    
    file_path = uploaded_files[file_id]["file_path"]
    if not os.path.exists(file_path):
        raise ValueError(f"文件 {file_path} 不存在")
    
    return file_path
