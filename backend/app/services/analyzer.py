#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import pandas as pd
import datetime
import uuid
from typing import Dict, List, Optional, Any
from app.models.schemas import AnalysisResult, FilteredRecord, EnhancedAnalysisResult
from app.core.config import settings

class ChatAnalyzer:
    """聊天记录分析引擎"""
    
    def __init__(self):
        self.after_sales_staff = []
        self.filter_rules = settings.FILTER_RULES_CONFIG
        self.filtered_records_details = []  # 存储详细过滤记录
        self._load_staff_list()
    
    def _load_staff_list(self) -> None:
        """加载售后人员名单"""
        try:
            staff_file_path = settings.STAFF_CONFIG_PATH
            if os.path.exists(staff_file_path):
                with open(staff_file_path, 'r', encoding='utf-8') as f:
                    staff_data = json.load(f)
                self.after_sales_staff = [item['nick_name'] for item in staff_data]
                print(f"成功加载售后人员名单: {len(self.after_sales_staff)} 人")
            else:
                # 生产环境中初始化为空列表，通过API动态添加
                print("售后人员名单文件不存在，初始化为空列表")
                self.after_sales_staff = []
                # 确保配置文件目录存在
                config_dir = os.path.dirname(staff_file_path)
                if config_dir:
                    os.makedirs(config_dir, exist_ok=True)
        except Exception as e:
            print(f"加载售后人员名单出错: {e}")
            self.after_sales_staff = []
    
    def analyze_excel(self, excel_file_path: str, progress_callback=None) -> AnalysisResult:
        """
        分析Excel聊天记录文件
        
        Args:
            excel_file_path: Excel文件路径
            progress_callback: 进度回调函数
            
        Returns:
            AnalysisResult: 分析结果
        """
        print(f"开始分析聊天记录文件: {os.path.basename(excel_file_path)}")
        print(f"文件大小: {os.path.getsize(excel_file_path) / (1024 * 1024):.2f} MB")
        print(f"售后人员数量: {len(self.after_sales_staff)}")
        
        # 清空之前的详细记录
        self.filtered_records_details = []
        
        # 初始化计数器
        counters = {
            'total_records': 0,
            'filtered_records': 0,
            'early_morning_count': 0,
            'staff_involved_count': 0,
            'service_assistant_count': 0,
            'address_confirm_count': 0,
            'parse_error_count': 0,
            'empty_records_count': 0
        }
        
        try:
            # 读取Excel文件
            if progress_callback:
                progress_callback(10, "正在读取Excel文件...")
            
            df = pd.read_excel(excel_file_path)
            counters['total_records'] = len(df)
            
            print(f"共读取 {counters['total_records']} 条记录")
            
            if progress_callback:
                progress_callback(20, "开始应用过滤规则...")
            
            # 逐条处理记录
            for index, row in df.iterrows():
                # 更新进度
                if progress_callback and (index + 1) % 1000 == 0:
                    progress = 20 + int((index + 1) / counters['total_records'] * 70)
                    progress_callback(progress, f"处理进度: {index + 1}/{counters['total_records']}")
                
                try:
                    # 解析消息和用户数据
                    messages = self._parse_messages(row)
                    users = self._parse_users(row)
                    
                    # 检查是否为空记录
                    if not messages:
                        counters['empty_records_count'] += 1
                        counters['filtered_records'] += 1
                        self._add_filtered_record("empty_record", "空记录", index, row)
                        continue
                    
                    # 应用过滤规则
                    if self._apply_filters(messages, users, counters, index, row):
                        counters['filtered_records'] += 1
                        
                except Exception as e:
                    print(f"处理记录 {index} 时出错: {e}")
                    counters['parse_error_count'] += 1
                    counters['filtered_records'] += 1
                    self._add_filtered_record("parse_error", "解析错误", index, row, 
                                            error_message=str(e))
            
            if progress_callback:
                progress_callback(95, "生成分析结果...")
            
            # 计算结果
            valid_records = counters['total_records'] - counters['filtered_records']
            filter_rate = (counters['filtered_records'] / counters['total_records'] * 100) if counters['total_records'] > 0 else 0
            
            result = EnhancedAnalysisResult(
                total_records=counters['total_records'],
                filtered_records=counters['filtered_records'],
                valid_records=valid_records,
                filter_rate=round(filter_rate, 2),
                early_morning_count=counters['early_morning_count'],
                staff_involved_count=counters['staff_involved_count'],
                service_assistant_count=counters['service_assistant_count'],
                address_confirm_count=counters['address_confirm_count'],
                parse_error_count=counters['parse_error_count'],
                empty_records_count=counters['empty_records_count'],
                filtered_records_details=self.filtered_records_details
            )
            
            if progress_callback:
                progress_callback(100, "分析完成")
            
            # 打印结果摘要
            self._print_analysis_summary(result)
            
            return result
            
        except Exception as e:
            print(f"分析Excel文件时出错: {e}")
            raise e
    
    def _parse_messages(self, row: pd.Series) -> List[Dict]:
        """解析消息数据"""
        messages = []
        
        if 'messages' in row and not pd.isna(row['messages']):
            try:
                if isinstance(row['messages'], str):
                    messages = json.loads(row['messages'])
                elif isinstance(row['messages'], list):
                    messages = row['messages']
            except json.JSONDecodeError:
                pass
        
        return messages if isinstance(messages, list) else []
    
    def _parse_users(self, row: pd.Series) -> List[str]:
        """解析用户数据"""
        users = []
        
        if 'users' in row and not pd.isna(row['users']):
            users_str = str(row['users'])
            users = [user.strip() for user in users_str.split(',') if user.strip()]
        
        return users
    
    def _apply_filters(self, messages: List[Dict], users: List[str], counters: Dict, record_index: int, row: pd.Series) -> bool:
        """
        应用过滤规则
        
        Returns:
            bool: True表示应该过滤掉这条记录
        """
        # 过滤规则1: 早晨消息检查(0-8点)
        if self.filter_rules['early_morning_filter']['enabled']:
            early_time = self._check_early_morning_messages(messages)
            if early_time:
                counters['early_morning_count'] += 1
                self._add_filtered_record("early_morning", "早晨消息(0-8点)", record_index, row, 
                                        timestamp=early_time)
                return True
        
        # 过滤规则2: 售后人员检查
        if self.filter_rules['staff_filter']['enabled']:
            staff_name = self._check_staff_involvement(users)
            if staff_name:
                counters['staff_involved_count'] += 1
                self._add_filtered_record("staff_involvement", "售后人员参与", record_index, row,
                                        staff_name=staff_name)
                return True
        
        # 过滤规则3: 服务助手检查
        if self.filter_rules['service_assistant_filter']['enabled']:
            service_msg = self._check_service_assistant_only(messages)
            if service_msg:
                counters['service_assistant_count'] += 1
                self._add_filtered_record("service_assistant", "服务助手消息", record_index, row,
                                        service_message=service_msg)
                return True
        
        # 过滤规则4: 收货地址确认检查
        if self.filter_rules['address_confirm_filter']['enabled']:
            address_content = self._check_address_confirmation(messages)
            if address_content:
                counters['address_confirm_count'] += 1
                self._add_filtered_record("address_confirmation", "收货地址确认消息", record_index, row,
                                        address_content=address_content)
                return True
        
        return False
    
    def _check_early_morning_messages(self, messages: List[Dict]) -> Optional[datetime.datetime]:
        """检查早晨消息(0-8点)，返回具体时间"""
        try:
            for message in messages:
                if isinstance(message, dict) and 'time' in message:
                    time_str = message['time']
                    if time_str:
                        # 处理时间字符串
                        time_str = time_str.replace('Z', '+00:00')
                        dt = datetime.datetime.fromisoformat(time_str)
                        if 0 <= dt.hour < 8:
                            return dt
        except Exception:
            pass
        return None
    
    def _check_staff_involvement(self, users: List[str]) -> Optional[str]:
        """检查售后人员参与，返回具体人员姓名"""
        for user in users:
            if 'tineco添可官方旗舰店:k' in user:
                return user
            elif user in self.after_sales_staff:
                return user
        return None
    
    def _check_service_assistant_only(self, messages: List[Dict]) -> Optional[str]:
        """检查是否全部是服务助手消息，返回服务助手消息内容"""
        if not messages:
            return None
        
        service_messages = []
        for message in messages:
            if isinstance(message, dict) and 'sender_nick' in message:
                if message['sender_nick'] != 'tineco添可官方旗舰店:服务助手':
                    return None
                if 'content' in message:
                    content = message['content']
                    if isinstance(content, dict) and 'text' in content:
                        service_messages.append(content['text'])
        
        return "; ".join(service_messages) if service_messages else "服务助手消息"
    
    def _check_address_confirmation(self, messages: List[Dict]) -> Optional[str]:
        """检查收货地址确认消息，返回地址内容"""
        for message in messages:
            if isinstance(message, dict) and 'content' in message:
                content = message['content']
                if isinstance(content, dict) and content.get('summary') == '请确认收货地址':
                    # 尝试提取地址信息
                    if 'text' in content:
                        return content['text']
                    return '请确认收货地址'
        return None
    
    def _add_filtered_record(self, filter_type: str, filter_reason: str, record_index: int, 
                           row: pd.Series, **kwargs) -> None:
        """添加过滤记录详情"""
        # 生成记录ID
        record_id = f"CHT_{datetime.datetime.now().strftime('%Y%m%d')}_{record_index:06d}"
        
        # 创建原始数据字典
        raw_data = {}
        for col in row.index:
            try:
                value = row[col]
                if pd.notna(value):
                    raw_data[col] = value if not isinstance(value, pd.Series) else str(value)
            except Exception:
                pass
        
        # 创建FilteredRecord对象
        filtered_record = FilteredRecord(
            record_id=record_id,
            filter_type=filter_type,
            filter_reason=filter_reason,
            record_index=record_index,
            raw_data=raw_data,
            **kwargs
        )
        
        self.filtered_records_details.append(filtered_record)
    
    def _print_analysis_summary(self, result: AnalysisResult) -> None:
        """打印分析结果摘要"""
        print("\n" + "-" * 70)
        print("聊天记录分析结果摘要")
        print("-" * 70)
        print(f"总记录数: {result.total_records}")
        print(f"被过滤记录数: {result.filtered_records}")
        print(f"有效记录数: {result.valid_records}")
        print(f"过滤率: {result.filter_rate}%")
        print("\n" + "-" * 70)
        print("过滤条件统计")
        print("-" * 70)
        print(f"早晨消息(0-8点): {result.early_morning_count} 条")
        print(f"售后人员参与: {result.staff_involved_count} 条")
        print(f"全部是服务助手消息: {result.service_assistant_count} 条")
        print(f"收货地址确认消息: {result.address_confirm_count} 条")
        print(f"消息解析错误: {result.parse_error_count} 条")
        print(f"空消息记录: {result.empty_records_count} 条")
    
    def get_filter_rules(self) -> Dict:
        """获取当前过滤规则配置"""
        return self.filter_rules
    
    def update_filter_rules(self, rules: Dict) -> None:
        """更新过滤规则配置"""
        self.filter_rules.update(rules)
    
    def get_staff_list(self) -> List[str]:
        """获取售后人员名单"""
        return self.after_sales_staff.copy()
    
    def update_staff_list(self, staff_list: List[str]) -> None:
        """更新售后人员名单"""
        self.after_sales_staff = staff_list.copy()
        
        # 保存到配置文件
        try:
            os.makedirs(os.path.dirname(settings.STAFF_CONFIG_PATH), exist_ok=True)
            staff_data = [{"nick_name": name} for name in staff_list]
            with open(settings.STAFF_CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(staff_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存售后人员名单出错: {e}")

# 创建全局分析器实例
analyzer = ChatAnalyzer()
