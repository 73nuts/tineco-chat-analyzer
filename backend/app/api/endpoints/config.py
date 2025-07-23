#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Dict
from fastapi import APIRouter, HTTPException, UploadFile, File
import pandas as pd
import json
import io
from app.models.schemas import ApiResponse, FilterRule, StaffMember
from app.services.analyzer import analyzer

router = APIRouter()

@router.get("/filter-rules", response_model=ApiResponse)
async def get_filter_rules():
    """获取过滤规则配置"""
    try:
        rules = analyzer.get_filter_rules()
        
        # 转换为前端友好的格式
        rules_list = []
        for rule_id, rule_config in rules.items():
            rule = FilterRule(
                rule_id=rule_id,
                name=rule_config.get("description", rule_id),
                description=rule_config.get("description", ""),
                enabled=rule_config.get("enabled", True),
                parameters=rule_config.get("parameters", {})
            )
            rules_list.append(rule)
        
        return ApiResponse(
            success=True,
            message="获取过滤规则成功",
            data={"rules": [rule.dict() for rule in rules_list]}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取过滤规则失败: {str(e)}"
        )

@router.put("/filter-rules", response_model=ApiResponse)
async def update_filter_rules(rules_update: Dict[str, Dict]):
    """更新过滤规则配置"""
    try:
        # 验证规则格式
        current_rules = analyzer.get_filter_rules()
        
        for rule_id, rule_config in rules_update.items():
            if rule_id not in current_rules:
                raise HTTPException(
                    status_code=400,
                    detail=f"未知的过滤规则: {rule_id}"
                )
            
            # 验证必要字段
            if "enabled" not in rule_config:
                raise HTTPException(
                    status_code=400,
                    detail=f"规则 {rule_id} 缺少 enabled 字段"
                )
        
        # 更新规则
        analyzer.update_filter_rules(rules_update)
        
        return ApiResponse(
            success=True,
            message="更新过滤规则成功",
            data={"updated_rules": list(rules_update.keys())}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新过滤规则失败: {str(e)}"
        )

@router.get("/staff-list", response_model=ApiResponse)
async def get_staff_list():
    """获取售后人员名单"""
    try:
        staff_names = analyzer.get_staff_list()
        
        # 转换为结构化格式
        staff_members = []
        for name in staff_names:
            staff_member = StaffMember(
                nick_name=name,
                status="active"
            )
            staff_members.append(staff_member)
        
        return ApiResponse(
            success=True,
            message="获取售后人员名单成功",
            data={
                "staff_members": [member.dict() for member in staff_members],
                "total_count": len(staff_members)
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取售后人员名单失败: {str(e)}"
        )

@router.put("/staff-list", response_model=ApiResponse)
async def update_staff_list(staff_data: Dict[str, List[str]]):
    """更新售后人员名单"""
    try:
        if "staff_names" not in staff_data:
            raise HTTPException(
                status_code=400,
                detail="请提供 staff_names 字段"
            )
        
        staff_names = staff_data["staff_names"]
        
        # 验证数据格式
        if not isinstance(staff_names, list):
            raise HTTPException(
                status_code=400,
                detail="staff_names 必须是字符串数组"
            )
        
        # 过滤空字符串和重复项
        cleaned_names = list(set(name.strip() for name in staff_names if name.strip()))
        
        # 更新售后人员名单
        analyzer.update_staff_list(cleaned_names)
        
        return ApiResponse(
            success=True,
            message="更新售后人员名单成功",
            data={
                "total_count": len(cleaned_names),
                "updated_names": cleaned_names
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新售后人员名单失败: {str(e)}"
        )

@router.post("/staff-list/add", response_model=ApiResponse)
async def add_staff_member(staff_data: Dict[str, str]):
    """添加售后人员"""
    try:
        if "nick_name" not in staff_data:
            raise HTTPException(
                status_code=400,
                detail="请提供 nick_name 字段"
            )
        
        nick_name = staff_data["nick_name"].strip()
        if not nick_name:
            raise HTTPException(
                status_code=400,
                detail="昵称不能为空"
            )
        
        # 获取当前名单
        current_staff = analyzer.get_staff_list()
        
        # 检查是否已存在
        if nick_name in current_staff:
            raise HTTPException(
                status_code=400,
                detail="该售后人员已存在"
            )
        
        # 添加新成员
        current_staff.append(nick_name)
        analyzer.update_staff_list(current_staff)
        
        return ApiResponse(
            success=True,
            message="添加售后人员成功",
            data={"nick_name": nick_name}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"添加售后人员失败: {str(e)}"
        )

@router.delete("/staff-list/{nick_name}", response_model=ApiResponse)
async def remove_staff_member(nick_name: str):
    """删除售后人员"""
    try:
        # 获取当前名单
        current_staff = analyzer.get_staff_list()
        
        # 检查是否存在
        if nick_name not in current_staff:
            raise HTTPException(
                status_code=404,
                detail="该售后人员不存在"
            )
        
        # 删除成员
        current_staff.remove(nick_name)
        analyzer.update_staff_list(current_staff)
        
        return ApiResponse(
            success=True,
            message="删除售后人员成功",
            data={"nick_name": nick_name}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除售后人员失败: {str(e)}"
        )

@router.post("/staff-list/upload-excel", response_model=ApiResponse)
async def upload_staff_excel(file: UploadFile = File(...)):
    """上传Excel文件解析售后人员名单"""
    try:
        print(f"开始处理Excel文件: {file.filename}")
        
        # 验证文件类型
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="请选择文件"
            )
        
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=400,
                detail="只支持Excel文件格式(.xlsx/.xls)"
            )
        
        # 读取文件内容
        content = await file.read()
        print(f"文件大小: {len(content)} bytes")
        
        try:
            # 使用pandas读取Excel文件
            df = pd.read_excel(io.BytesIO(content))
            print(f"Excel文件读取成功，形状: {df.shape}")
            print(f"列名: {list(df.columns)}")
        except Exception as e:
            print(f"Excel文件解析失败: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Excel文件格式错误，无法解析: {str(e)}"
            )
        
        # 检查Excel格式 - 支持两种格式
        # 1. 专门的售后人员名单文件（包含nick_name列）
        # 2. 聊天记录文件（从messages列中提取售后人员昵称）
        
        valid_names = []
        
        if 'nick_name' in df.columns:
            # 格式1：专门的售后人员名单文件
            print("检测到nick_name列，开始解析售后人员名单...")
            nick_names = df['nick_name'].dropna().astype(str).tolist()
            print(f"从nick_name列读取到 {len(nick_names)} 个条目")
            
            for i, name in enumerate(nick_names):
                name = name.strip()
                print(f"  处理第{i+1}个: '{name}'")
                if name and name not in valid_names:
                    valid_names.append(name)
                    print(f"    ✓ 添加到有效名单: '{name}'")
                else:
                    print(f"    ✗ 跳过（空值或重复）: '{name}'")
                    
        elif 'messages' in df.columns:
            # 格式2：聊天记录文件，从messages中提取售后人员昵称
            tineco_staff_nicks = set()
            
            for idx, row in df.iterrows():
                try:
                    messages_value = row['messages']
                    if pd.notna(messages_value):
                        if isinstance(messages_value, str):
                            messages = json.loads(messages_value)
                        else:
                            messages = messages_value
                        
                        if isinstance(messages, list):
                            for message in messages:
                                if isinstance(message, dict):
                                    sender_nick = message.get('sender_nick', '')
                                    receiver_nick = message.get('receiver_nick', '')
                                    
                                    # 识别tineco官方店铺的售后人员昵称
                                    for nick in [sender_nick, receiver_nick]:
                                        if isinstance(nick, str) and 'tineco添可官方旗舰店:' in nick:
                                            staff_name = nick.split('tineco添可官方旗舰店:')[-1]
                                            if staff_name and staff_name != '服务助手':
                                                tineco_staff_nicks.add(nick)
                                                
                except (json.JSONDecodeError, AttributeError, KeyError) as e:
                    continue  # 跳过解析失败的行
            
            valid_names = list(tineco_staff_nicks)
            
        else:
            raise HTTPException(
                status_code=400,
                detail="Excel格式错误：文件必须包含 'nick_name' 列（售后人员名单）或 'messages' 列（聊天记录文件）。"
            )
        
        print(f"解析完成，共找到 {len(valid_names)} 个有效售后人员:")
        for i, name in enumerate(valid_names):
            print(f"  {i+1}: {name}")
            
        if not valid_names:
            print("❌ 没有找到有效的售后人员昵称数据")
            raise HTTPException(
                status_code=400,
                detail="Excel文件中没有找到有效的售后人员昵称数据"
            )
        
        # 更新售后人员名单
        print(f"开始更新售后人员名单，共 {len(valid_names)} 个人员...")
        analyzer.update_staff_list(valid_names)
        print("✅ 售后人员名单更新成功")
        
        return ApiResponse(
            success=True,
            message=f"成功从Excel文件解析并导入{len(valid_names)}个售后人员",
            data={
                "total_count": len(valid_names),
                "imported_names": valid_names,
                "filename": file.filename
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"处理Excel文件失败: {str(e)}"
        )

@router.post("/validate-chat-excel", response_model=ApiResponse)
async def validate_chat_excel(file: UploadFile = File(...)):
    """验证聊天记录Excel文件格式"""
    try:
        # 验证文件类型
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="请选择文件"
            )
        
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=400,
                detail="只支持Excel文件格式(.xlsx/.xls)"
            )
        
        # 读取文件内容
        content = await file.read()
        
        try:
            # 使用pandas读取Excel文件
            df = pd.read_excel(io.BytesIO(content))
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Excel文件格式错误，无法解析: {str(e)}"
            )
        
        # 定义必需的列
        required_columns = ['platform', 'date', 'messages', 'user_nick', 'shop_name', 'users']
        missing_columns = []
        
        # 检查必需的列
        for col in required_columns:
            if col not in df.columns:
                missing_columns.append(col)
        
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Excel格式错误：缺少必需的列 {', '.join(missing_columns)}。请确保Excel文件包含聊天记录分析所需的所有列。"
            )
        
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
        
        # 如果有太多错误，只返回前5个
        if len(validation_errors) > 5:
            validation_errors = validation_errors[:5] + [f"...还有{len(validation_errors)-5}个类似错误"]
        
        if validation_errors:
            raise HTTPException(
                status_code=400,
                detail=f"Excel格式校验失败：\n" + "\n".join(validation_errors)
            )
        
        return ApiResponse(
            success=True,
            message="Excel文件格式验证通过",
            data={
                "filename": file.filename,
                "total_rows": len(df),
                "columns": list(df.columns),
                "validated_rows": sample_size
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"验证Excel文件失败: {str(e)}"
        )

@router.post("/staff-list/validate-excel", response_model=ApiResponse)
async def validate_staff_excel(file: UploadFile = File(...)):
    """验证售后人员Excel文件格式并预览导入信息"""
    try:
        print(f"开始验证售后人员Excel文件: {file.filename}")
        
        # 验证文件类型
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="请选择文件"
            )
        
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=400,
                detail="只支持Excel文件格式(.xlsx/.xls)"
            )
        
        # 读取文件内容
        content = await file.read()
        print(f"文件大小: {len(content)} bytes")
        
        try:
            # 使用pandas读取Excel文件
            df = pd.read_excel(io.BytesIO(content))
            print(f"Excel文件读取成功，形状: {df.shape}")
            print(f"列名: {list(df.columns)}")
        except Exception as e:
            print(f"Excel文件解析失败: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Excel文件格式错误，无法解析: {str(e)}"
            )
        
        # 预览解析结果
        valid_names = []
        
        if 'nick_name' in df.columns:
            # 格式1：专门的售后人员名单文件
            print("检测到nick_name列，开始预览售后人员名单...")
            nick_names = df['nick_name'].dropna().astype(str).tolist()
            print(f"从nick_name列读取到 {len(nick_names)} 个条目")
            
            for name in nick_names:
                name = name.strip()
                if name and name not in valid_names:
                    valid_names.append(name)
                    
        elif 'messages' in df.columns:
            # 格式2：聊天记录文件，从messages中提取售后人员昵称
            print("检测到messages列，开始预览聊天记录中的售后人员...")
            tineco_staff_nicks = set()
            
            # 只处理前100行作为预览
            sample_size = min(100, len(df))
            for idx in range(sample_size):
                try:
                    messages_value = df.iloc[idx]['messages']
                    if pd.notna(messages_value):
                        if isinstance(messages_value, str):
                            messages = json.loads(messages_value)
                        else:
                            messages = messages_value
                        
                        if isinstance(messages, list):
                            for message in messages:
                                if isinstance(message, dict):
                                    sender_nick = message.get('sender_nick', '')
                                    receiver_nick = message.get('receiver_nick', '')
                                    
                                    # 识别tineco官方店铺的售后人员昵称
                                    for nick in [sender_nick, receiver_nick]:
                                        if isinstance(nick, str) and 'tineco添可官方旗舰店:' in nick:
                                            staff_name = nick.split('tineco添可官方旗舰店:')[-1]
                                            if staff_name and staff_name != '服务助手':
                                                tineco_staff_nicks.add(nick)
                                                
                except (json.JSONDecodeError, AttributeError, KeyError):
                    continue
            
            valid_names = list(tineco_staff_nicks)
            
        else:
            raise HTTPException(
                status_code=400,
                detail="Excel格式错误：文件必须包含 'nick_name' 列（售后人员名单）或 'messages' 列（聊天记录文件）。"
            )
        
        print(f"预览完成，共找到 {len(valid_names)} 个有效售后人员")
        
        return ApiResponse(
            success=True,
            message="Excel文件格式验证通过",
            data={
                "filename": file.filename,
                "total_rows": len(df),
                "columns": list(df.columns),
                "expected_count": len(valid_names),
                "preview_names": valid_names[:10] if valid_names else []  # 返回前10个作为预览
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"验证Excel文件失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"验证Excel文件失败: {str(e)}"
        )
