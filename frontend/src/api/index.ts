import axios from 'axios'
import { ElMessage } from 'element-plus'

// 获取API基础URL
const getBaseURL = () => {
  // 开发环境使用代理
  if (import.meta.env.DEV) {
    return '/api'
  }
  
  // 生产环境使用环境变量或默认值
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'https://tineco-analyzer-backend.onrender.com/api'
  console.log('API Base URL:', baseURL, 'Environment:', import.meta.env.PROD ? 'production' : 'development')
  return baseURL
}

// 创建axios实例
const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    const { data } = response
    if (data.success === false) {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message || '请求失败'))
    }
    return data
  },
  (error) => {
    console.error('API Request Error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      message: error.message,
      responseData: error.response?.data
    })
    
    const message = error.response?.data?.detail || error.message || '网络错误'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// API接口定义
export interface FileUploadResponse {
  file_id: string
  filename: string
  file_size: number
  upload_time: string
  status: string
}

export interface AnalysisResult {
  total_records: number
  filtered_records: number
  valid_records: number
  filter_rate: number
  early_morning_count: number
  staff_involved_count: number
  service_assistant_count: number
  address_confirm_count: number
  parse_error_count: number
  empty_records_count: number
}

export interface AnalysisTask {
  task_id: string
  file_id: string
  filename: string
  status: string
  created_time: string
  started_time?: string
  completed_time?: string
  progress: number
  error_message?: string
  result?: AnalysisResult
  status_message?: string
}

export interface FilterRule {
  rule_id: string
  name: string
  description: string
  enabled: boolean
  parameters?: Record<string, any>
}

export interface StaffMember {
  nick_name: string
  real_name?: string
  department?: string
  status: string
}

export interface FilteredRecord {
  record_id: string
  filter_type: string
  filter_reason: string
  record_index: number
  raw_data: Record<string, any>
  staff_name?: string
  timestamp?: string
  address_content?: string
  error_message?: string
  service_message?: string
}

export interface FilterDetailResponse {
  filter_type: string
  total_count: number
  records: FilteredRecord[]
  page: number
  page_size: number
  total_pages: number
}

export interface ChatRecordDetail {
  record_id: string
  filter_info: {
    filter_type: string
    filter_reason: string
    staff_name?: string
    timestamp?: string
    address_content?: string
    error_message?: string
    service_message?: string
  }
  raw_data: Record<string, any>
}

// 文件上传相关API
export const uploadAPI = {
  // 上传文件
  uploadFile: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<any, { success: boolean; message: string; data: FileUploadResponse }>('/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 获取文件列表
  getFiles: () => {
    return api.get<any, { success: boolean; message: string; data: { files: FileUploadResponse[]; total: number } }>('/upload/files')
  },

  // 获取文件信息
  getFileInfo: (fileId: string) => {
    return api.get<any, { success: boolean; message: string; data: FileUploadResponse }>(`/upload/files/${fileId}`)
  },

  // 删除文件
  deleteFile: (fileId: string) => {
    return api.delete<any, { success: boolean; message: string; data: { file_id: string } }>(`/upload/files/${fileId}`)
  }
}

// 分析相关API
export const analysisAPI = {
  // 开始分析
  startAnalysis: (fileId: string, filterRules?: Record<string, boolean>) => {
    return api.post<any, { success: boolean; message: string; data: { task_id: string; status: string } }>('/analysis/start', {
      file_id: fileId,
      filter_rules: filterRules
    })
  },

  // 获取任务状态
  getTaskStatus: (taskId: string) => {
    return api.get<any, { success: boolean; message: string; data: AnalysisTask }>(`/analysis/tasks/${taskId}`)
  },

  // 获取任务列表
  getTasks: () => {
    return api.get<any, { success: boolean; message: string; data: { tasks: AnalysisTask[]; total: number } }>('/analysis/tasks')
  },

  // 获取分析结果
  getResult: (taskId: string) => {
    return api.get<any, { success: boolean; message: string; data: { task_id: string; result: AnalysisResult; completed_time: string } }>(`/analysis/tasks/${taskId}/result`)
  },

  // 删除任务
  deleteTask: (taskId: string) => {
    return api.delete<any, { success: boolean; message: string; data: { task_id: string } }>(`/analysis/tasks/${taskId}`)
  },

  // 获取统计信息
  getStats: () => {
    return api.get<any, { success: boolean; message: string; data: any }>('/analysis/stats')
  },

  // 获取过滤详情列表
  getFilterDetails: (taskId: string, filterType: string, page: number = 1, pageSize: number = 50) => {
    return api.get<any, { success: boolean; message: string; data: FilterDetailResponse }>(`/analysis/tasks/${taskId}/filter-details/${filterType}`, {
      params: { page, page_size: pageSize }
    })
  },

  // 获取聊天记录详情
  getChatRecordDetail: (taskId: string, recordId: string) => {
    return api.get<any, { success: boolean; message: string; data: ChatRecordDetail }>(`/analysis/tasks/${taskId}/chat-record/${recordId}`)
  }
}

// 配置相关API
export const configAPI = {
  // 获取过滤规则
  getFilterRules: () => {
    return api.get<any, { success: boolean; message: string; data: { rules: FilterRule[] } }>('/config/filter-rules')
  },

  // 更新过滤规则
  updateFilterRules: (rules: Record<string, Record<string, any>>) => {
    return api.put<any, { success: boolean; message: string; data: { updated_rules: string[] } }>('/config/filter-rules', rules)
  },

  // 获取售后名单
  getStaffList: () => {
    return api.get<any, { success: boolean; message: string; data: { staff_members: StaffMember[]; total_count: number } }>('/config/staff-list')
  },

  // 更新售后名单
  updateStaffList: (staffNames: string[]) => {
    return api.put<any, { success: boolean; message: string; data: { total_count: number; updated_names: string[] } }>('/config/staff-list', {
      staff_names: staffNames
    })
  },

  // 添加售后人员
  addStaffMember: (nickName: string) => {
    return api.post<any, { success: boolean; message: string; data: { nick_name: string } }>('/config/staff-list/add', {
      nick_name: nickName
    })
  },

  // 删除售后人员
  removeStaffMember: (nickName: string) => {
    return api.delete<any, { success: boolean; message: string; data: { nick_name: string } }>(`/config/staff-list/${encodeURIComponent(nickName)}`)
  },

  // 上传Excel解析售后人员名单
  uploadStaffExcel: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<any, { success: boolean; message: string; data: { total_count: number; imported_names: string[]; filename: string } }>('/config/staff-list/upload-excel', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 验证聊天记录Excel格式
  validateChatExcel: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<any, { success: boolean; message: string; data: { filename: string; total_rows: number; columns: string[]; validated_rows: number } }>('/config/validate-chat-excel', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 验证售后人员Excel格式
  validateStaffExcel: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<any, { success: boolean; message: string; data: { filename: string; total_rows: number; columns: string[]; expected_count: number; preview_names: string[] } }>('/config/staff-list/validate-excel', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}

// 系统相关API
export const systemAPI = {
  // 健康检查
  healthCheck: () => {
    return api.get<any, { success: boolean; message: string; data: any }>('/system/health')
  },

  // 获取系统统计
  getStats: () => {
    return api.get<any, { success: boolean; message: string; data: any }>('/system/stats')
  },

  // 获取系统配置
  getConfig: () => {
    return api.get<any, { success: boolean; message: string; data: any }>('/system/config')
  },

  // 系统清理
  cleanup: () => {
    return api.post<any, { success: boolean; message: string; data: any }>('/system/cleanup')
  },

  // 获取系统日志
  getLogs: () => {
    return api.get<any, { success: boolean; message: string; data: { logs: any[]; total: number } }>('/system/logs')
  }
}

// 导出过滤详情相关的便捷方法
export const getFilterDetails = analysisAPI.getFilterDetails
export const getChatRecordDetail = analysisAPI.getChatRecordDetail

export default api
