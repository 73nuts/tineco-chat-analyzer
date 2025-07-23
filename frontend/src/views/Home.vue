<template>
  <div class="home-container">
    <div class="page-header">
      <h1>文件上传</h1>
      <p>上传Excel聊天记录文件进行分析</p>
    </div>

    <!-- 文件上传区域 -->
    <el-card class="upload-card">
      <template #header>
        <div class="card-header">
          <span>上传聊天记录文件</span>
        </div>
      </template>

      <el-upload
        ref="uploadRef"
        class="upload-dragger"
        drag
        :action="uploadAction"
        :before-upload="beforeUpload"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        :on-progress="handleUploadProgress"
        :show-file-list="false"
        :disabled="uploading"
      >
        <div class="upload-content">
          <el-icon class="upload-icon" size="48">
            <UploadFilled v-if="!uploading" />
            <Loading v-else />
          </el-icon>
          <div class="upload-text">
            <p v-if="!uploading">将文件拖拽到此处，或<em>点击上传</em></p>
            <p v-else>上传中... {{ uploadProgress }}%</p>
          </div>
          <div class="upload-hint">
            支持 .xlsx 和 .xls 格式，文件大小不超过 50MB
          </div>
        </div>
      </el-upload>

      <!-- 上传进度条 -->
      <el-progress
        v-if="uploading"
        :percentage="uploadProgress"
        :stroke-width="8"
        class="upload-progress"
      />
    </el-card>

    <!-- 已上传文件列表 -->
    <el-card class="files-card" v-if="uploadedFiles.length > 0">
      <template #header>
        <div class="card-header">
          <span>已上传文件 ({{ uploadedFiles.length }})</span>
          <el-button type="primary" size="small" @click="refreshFileList">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-table :data="uploadedFiles" style="width: 100%">
        <el-table-column prop="filename" label="文件名" min-width="200">
          <template #default="{ row }">
            <div class="file-info">
              <el-icon><Document /></el-icon>
              <span>{{ row.filename }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="file_size" label="文件大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.file_size) }}
          </template>
        </el-table-column>
        <el-table-column prop="upload_time" label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.upload_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="startAnalysis(row)"
              :disabled="row.status !== 'uploaded'"
            >
              <el-icon><DataAnalysis /></el-icon>
              开始分析
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="deleteFile(row)"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 空状态 -->
    <el-empty
      v-if="uploadedFiles.length === 0 && !loading"
      description="暂无上传文件"
      class="empty-state"
    >
      <el-button type="primary" @click="triggerUpload">
        <el-icon><Plus /></el-icon>
        上传第一个文件
      </el-button>
    </el-empty>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  UploadFilled,
  Loading,
  Refresh,
  Document,
  DataAnalysis,
  Delete,
  Plus
} from '@element-plus/icons-vue'
import { uploadAPI, analysisAPI, type FileUploadResponse } from '@/api'
import dayjs from 'dayjs'

const router = useRouter()
const uploadRef = ref()

// 响应式数据
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadedFiles = ref<FileUploadResponse[]>([])
const loading = ref(false)

// 上传配置
const getUploadAction = () => {
  // 开发环境使用代理
  if (import.meta.env.DEV) {
    return '/api/upload/'
  }
  
  // 生产环境使用完整的后端URL
  return import.meta.env.VITE_API_BASE_URL + '/upload/' || 'https://tineco-analyzer-backend.onrender.com/api/upload/'
}

const uploadAction = getUploadAction()

// 文件上传前的验证
const beforeUpload = (file: File) => {
  const allowedTypes = ['.xlsx', '.xls']
  const fileExt = '.' + file.name.split('.').pop()?.toLowerCase()
  
  if (!allowedTypes.includes(fileExt)) {
    ElMessage.error('只支持 .xlsx 和 .xls 格式的文件')
    return false
  }
  
  const maxSize = 50 * 1024 * 1024 // 50MB
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 50MB')
    return false
  }
  
  uploading.value = true
  uploadProgress.value = 0
  return true
}

// 上传进度处理
const handleUploadProgress = (event: any) => {
  uploadProgress.value = Math.round(event.percent)
}

// 上传成功处理
const handleUploadSuccess = (response: any) => {
  uploading.value = false
  uploadProgress.value = 0
  
  console.log('Upload response:', response)
  
  // 处理可能的响应格式差异
  const responseData = response.data || response
  if (responseData.success || response.success) {
    ElMessage.success('文件上传成功')
    refreshFileList()
  } else {
    ElMessage.error(responseData.message || response.message || '上传失败')
  }
}

// 上传失败处理
const handleUploadError = (error: any) => {
  uploading.value = false
  uploadProgress.value = 0
  ElMessage.error('文件上传失败')
  console.error('Upload error:', error)
}

// 手动触发上传
const triggerUpload = () => {
  uploadRef.value?.clearFiles()
  const input = uploadRef.value?.$el.querySelector('input[type="file"]')
  input?.click()
}

// 刷新文件列表
const refreshFileList = async () => {
  try {
    loading.value = true
    const response = await uploadAPI.getFiles()
    uploadedFiles.value = response.data.files
  } catch (error) {
    console.error('Failed to refresh file list:', error)
  } finally {
    loading.value = false
  }
}

// 开始分析
const startAnalysis = async (file: FileUploadResponse) => {
  try {
    const response = await analysisAPI.startAnalysis(file.file_id)
    ElMessage.success('分析任务已启动，正在跳转到分析页面...')
    
    // 先跳转到分析列表页面，让用户看到任务进度
    router.push('/analysis')
    
    // 2秒后再跳转到具体的分析详情页
    setTimeout(() => {
      router.push(`/analysis/${response.data.task_id}`)
    }, 2000)
  } catch (error) {
    console.error('Failed to start analysis:', error)
    ElMessage.error('启动分析任务失败')
  }
}

// 删除文件
const deleteFile = async (file: FileUploadResponse) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文件 "${file.filename}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await uploadAPI.deleteFile(file.file_id)
    ElMessage.success('文件删除成功')
    refreshFileList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete file:', error)
    }
  }
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化日期时间
const formatDateTime = (dateTime: string) => {
  return dayjs(dateTime).format('YYYY-MM-DD HH:mm:ss')
}

// 获取状态类型
const getStatusType = (status: string) => {
  switch (status) {
    case 'uploaded':
      return 'success'
    case 'analyzing':
      return 'warning'
    case 'completed':
      return 'info'
    case 'error':
      return 'danger'
    default:
      return 'info'
  }
}

// 获取状态文本
const getStatusText = (status: string) => {
  switch (status) {
    case 'uploaded':
      return '已上传'
    case 'analyzing':
      return '分析中'
    case 'completed':
      return '已完成'
    case 'error':
      return '错误'
    default:
      return status
  }
}

// 组件挂载时获取文件列表
onMounted(() => {
  refreshFileList()
})
</script>

<style scoped>
.home-container {
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  color: #303133;
  margin-bottom: 8px;
}

.page-header p {
  color: #606266;
  font-size: 14px;
}

.upload-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-dragger {
  width: 100%;
}

:deep(.el-upload-dragger) {
  width: 100%;
  height: 200px;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  background-color: #fafafa;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

:deep(.el-upload-dragger:hover) {
  border-color: #409eff;
  background-color: #f5f7fa;
}

:deep(.el-upload-dragger.is-dragover) {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.upload-content {
  text-align: center;
}

.upload-icon {
  color: #c0c4cc;
  margin-bottom: 16px;
}

.upload-text {
  font-size: 16px;
  color: #606266;
  margin-bottom: 8px;
}

.upload-text em {
  color: #409eff;
  font-style: normal;
}

.upload-hint {
  font-size: 12px;
  color: #909399;
}

.upload-progress {
  margin-top: 16px;
}

.files-card {
  margin-bottom: 24px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.empty-state {
  margin-top: 40px;
}
</style>
