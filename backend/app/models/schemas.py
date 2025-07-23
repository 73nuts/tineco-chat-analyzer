#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class AnalysisStatus(str, Enum):
    """分析状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class FileUploadResponse(BaseModel):
    """文件上传响应模型"""
    file_id: str = Field(..., description="文件唯一标识")
    filename: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小（字节）")
    upload_time: datetime = Field(..., description="上传时间")
    status: str = Field(default="uploaded", description="文件状态")

class AnalysisRequest(BaseModel):
    """分析请求模型"""
    file_id: str = Field(..., description="文件ID")
    filter_rules: Optional[Dict[str, bool]] = Field(
        default=None,
        description="过滤规则配置"
    )

class AnalysisResult(BaseModel):
    """分析结果模型"""
    total_records: int = Field(..., description="总记录数")
    filtered_records: int = Field(..., description="被过滤记录数")
    valid_records: int = Field(..., description="有效记录数")
    filter_rate: float = Field(..., description="过滤率百分比")
    
    # 各过滤条件统计
    early_morning_count: int = Field(default=0, description="早晨消息过滤数量")
    staff_involved_count: int = Field(default=0, description="售后人员参与过滤数量")
    service_assistant_count: int = Field(default=0, description="服务助手消息过滤数量")
    address_confirm_count: int = Field(default=0, description="地址确认消息过滤数量")
    parse_error_count: int = Field(default=0, description="解析错误数量")
    empty_records_count: int = Field(default=0, description="空记录数量")

class AnalysisTask(BaseModel):
    """分析任务模型"""
    task_id: str = Field(..., description="任务ID")
    file_id: str = Field(..., description="文件ID")
    filename: str = Field(..., description="文件名")
    status: AnalysisStatus = Field(..., description="任务状态")
    created_time: datetime = Field(..., description="创建时间")
    started_time: Optional[datetime] = Field(default=None, description="开始时间")
    completed_time: Optional[datetime] = Field(default=None, description="完成时间")
    progress: float = Field(default=0.0, description="进度百分比")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    result: Optional[AnalysisResult] = Field(default=None, description="分析结果")

class FilterRule(BaseModel):
    """过滤规则模型"""
    rule_id: str = Field(..., description="规则ID")
    name: str = Field(..., description="规则名称")
    description: str = Field(..., description="规则描述")
    enabled: bool = Field(default=True, description="是否启用")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="规则参数")

class FilterRulesConfig(BaseModel):
    """过滤规则配置模型"""
    rules: List[FilterRule] = Field(..., description="规则列表")
    updated_time: datetime = Field(..., description="更新时间")

class StaffMember(BaseModel):
    """售后人员模型"""
    nick_name: str = Field(..., description="昵称")
    real_name: Optional[str] = Field(default=None, description="真实姓名")
    department: Optional[str] = Field(default=None, description="部门")
    status: str = Field(default="active", description="状态")

class StaffList(BaseModel):
    """售后人员列表模型"""
    staff_members: List[StaffMember] = Field(..., description="售后人员列表")
    total_count: int = Field(..., description="总人数")
    updated_time: datetime = Field(..., description="更新时间")

class SystemStats(BaseModel):
    """系统统计模型"""
    total_files_processed: int = Field(..., description="处理文件总数")
    total_records_analyzed: int = Field(..., description="分析记录总数")
    average_filter_rate: float = Field(..., description="平均过滤率")
    active_tasks: int = Field(..., description="活跃任务数")
    system_uptime: str = Field(..., description="系统运行时间")

class ApiResponse(BaseModel):
    """通用API响应模型"""
    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(default=None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")

class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = Field(default=False, description="请求是否成功")
    error_code: str = Field(..., description="错误代码")
    error_message: str = Field(..., description="错误信息")
    details: Optional[Dict[str, Any]] = Field(default=None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")

# === 过滤详情相关模型 ===

class FilteredRecord(BaseModel):
    """被过滤记录详情模型"""
    record_id: str = Field(..., description="记录ID")
    filter_type: str = Field(..., description="过滤类型")
    filter_reason: str = Field(..., description="过滤原因")
    record_index: int = Field(..., description="记录在文件中的行号")
    raw_data: Dict[str, Any] = Field(..., description="原始聊天记录数据")
    
    # 不同过滤类型的特定字段
    staff_name: Optional[str] = Field(default=None, description="售后人员姓名（售后参与类型）")
    timestamp: Optional[datetime] = Field(default=None, description="时间戳（早晨消息类型）")
    address_content: Optional[str] = Field(default=None, description="地址内容（地址确认类型）")
    error_message: Optional[str] = Field(default=None, description="错误信息（解析错误类型）")
    service_message: Optional[str] = Field(default=None, description="服务助手消息内容")

class FilterDetailResponse(BaseModel):
    """过滤详情查询响应模型"""
    filter_type: str = Field(..., description="过滤类型")
    total_count: int = Field(..., description="该类型总记录数")
    records: List[FilteredRecord] = Field(..., description="过滤记录列表")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=50, description="每页大小")
    total_pages: int = Field(..., description="总页数")

class EnhancedAnalysisResult(AnalysisResult):
    """增强的分析结果模型（包含详细过滤记录）"""
    filtered_records_details: Optional[List[FilteredRecord]] = Field(default=None, description="详细过滤记录列表")
