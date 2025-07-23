<template>
  <div class="analysis-container">
    <div class="page-header">
      <h1>分析报告</h1>
      <p>查看聊天记录分析任务和结果</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-card class="stats-card">
        <div class="stats-content">
          <div class="stats-icon">
            <el-icon size="32" color="#409eff"><DataAnalysis /></el-icon>
          </div>
          <div class="stats-info">
            <div class="stats-value">{{ stats.total_tasks || 0 }}</div>
            <div class="stats-label">总任务数</div>
          </div>
        </div>
      </el-card>

      <el-card class="stats-card">
        <div class="stats-content">
          <div class="stats-icon">
            <el-icon size="32" color="#67c23a"><CircleCheck /></el-icon>
          </div>
          <div class="stats-info">
            <div class="stats-value">{{ stats.completed_tasks || 0 }}</div>
            <div class="stats-label">已完成</div>
          </div>
        </div>
      </el-card>

      <el-card class="stats-card">
        <div class="stats-content">
          <div class="stats-icon">
            <el-icon size="32" color="#e6a23c"><Loading /></el-icon>
          </div>
          <div class="stats-info">
            <div class="stats-value">{{ stats.processing_tasks || 0 }}</div>
            <div class="stats-label">处理中</div>
          </div>
        </div>
      </el-card>

      <el-card class="stats-card">
        <div class="stats-content">
          <div class="stats-icon">
            <el-icon size="32" color="#f56c6c"><CircleClose /></el-icon>
          </div>
          <div class="stats-info">
            <div class="stats-value">{{ stats.failed_tasks || 0 }}</div>
            <div class="stats-label">失败</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 任务列表 -->
    <el-card class="tasks-card">
      <template #header>
        <div class="card-header">
          <span>分析任务列表</span>
          <div class="header-actions">
            <el-button type="primary" size="small" @click="refreshTasks">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="tasks" style="width: 100%" v-loading="loading">
        <el-table-column prop="filename" label="文件名" min-width="200">
          <template #default="{ row }">
            <div class="file-info">
              <el-icon><Document /></el-icon>
              <span>{{ row.filename }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="progress" label="进度" width="150">
          <template #default="{ row }">
            <div class="progress-container">
              <el-progress 
                :percentage="row.progress" 
                :stroke-width="6"
                :show-text="false"
                :color="getProgressColor(row.status)"
              />
              <span class="progress-text">{{ row.progress }}%</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="created_time" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_time) }}
          </template>
        </el-table-column>

        <el-table-column prop="status_message" label="状态信息" min-width="150">
          <template #default="{ row }">
            <span class="status-message">{{ row.status_message || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="viewResult(row)"
              :disabled="row.status !== 'completed'"
            >
              <el-icon><View /></el-icon>
              查看结果
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="deleteTask(row)"
              :disabled="row.status === 'processing'"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <el-empty
        v-if="tasks.length === 0 && !loading"
        description="暂无分析任务"
        class="empty-state"
      >
        <el-button type="primary" @click="$router.push('/home')">
          <el-icon><Plus /></el-icon>
          上传文件开始分析
        </el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  DataAnalysis,
  CircleCheck,
  Loading,
  CircleClose,
  Refresh,
  Document,
  View,
  Delete,
  Plus
} from '@element-plus/icons-vue'
import { analysisAPI, type AnalysisTask } from '@/api'
import dayjs from 'dayjs'

const router = useRouter()

// 响应式数据
const tasks = ref<AnalysisTask[]>([])
const stats = ref({
  total_tasks: 0,
  completed_tasks: 0,
  processing_tasks: 0,
  failed_tasks: 0,
  average_filter_rate: 0
})
const loading = ref(false)

// 定时器
let refreshTimer: number | null = null

// 刷新任务列表
const refreshTasks = async () => {
  try {
    loading.value = true
    const [tasksResponse, statsResponse] = await Promise.all([
      analysisAPI.getTasks(),
      analysisAPI.getStats()
    ])
    
    tasks.value = tasksResponse.data.tasks
    stats.value = statsResponse.data
  } catch (error) {
    console.error('Failed to refresh tasks:', error)
  } finally {
    loading.value = false
  }
}

// 查看结果
const viewResult = (task: AnalysisTask) => {
  router.push(`/analysis/${task.task_id}`)
}

// 删除任务
const deleteTask = async (task: AnalysisTask) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除任务 "${task.filename}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await analysisAPI.deleteTask(task.task_id)
    ElMessage.success('任务删除成功')
    refreshTasks()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete task:', error)
    }
  }
}

// 获取状态类型
const getStatusType = (status: string) => {
  switch (status) {
    case 'completed':
      return 'success'
    case 'processing':
      return 'warning'
    case 'pending':
      return 'info'
    case 'failed':
      return 'danger'
    default:
      return 'info'
  }
}

// 获取状态文本
const getStatusText = (status: string) => {
  switch (status) {
    case 'completed':
      return '已完成'
    case 'processing':
      return '处理中'
    case 'pending':
      return '等待中'
    case 'failed':
      return '失败'
    default:
      return status
  }
}

// 获取进度条颜色
const getProgressColor = (status: string) => {
  switch (status) {
    case 'completed':
      return '#67c23a'
    case 'processing':
      return '#409eff'
    case 'failed':
      return '#f56c6c'
    default:
      return '#e4e7ed'
  }
}

// 格式化日期时间
const formatDateTime = (dateTime: string) => {
  return dayjs(dateTime).format('YYYY-MM-DD HH:mm:ss')
}

// 开始定时刷新
const startAutoRefresh = () => {
  refreshTimer = setInterval(() => {
    // 只有当有处理中的任务时才自动刷新
    const hasProcessingTasks = tasks.value.some(task => task.status === 'processing')
    if (hasProcessingTasks) {
      refreshTasks()
    }
  }, 3000) // 每3秒刷新一次
}

// 停止定时刷新
const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 组件挂载
onMounted(() => {
  refreshTasks()
  startAutoRefresh()
})

// 组件卸载
onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.analysis-container {
  max-width: 1200px;
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

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stats-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.stats-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stats-icon {
  flex-shrink: 0;
}

.stats-info {
  flex: 1;
}

.stats-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
}

.stats-label {
  font-size: 14px;
  color: #606266;
  margin-top: 4px;
}

.tasks-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-text {
  font-size: 12px;
  color: #606266;
  min-width: 35px;
}

.status-message {
  color: #606266;
  font-size: 12px;
}

.empty-state {
  margin: 40px 0;
}

:deep(.el-progress-bar__outer) {
  background-color: #f0f2f5;
}
</style>
