<template>
  <div class="system-container">
    <div class="page-header">
      <h1>系统状态</h1>
      <p>监控系统运行状态和性能指标</p>
    </div>

    <!-- 系统健康状态 -->
    <el-card class="health-card">
      <template #header>
        <div class="card-header">
          <span>系统健康检查</span>
          <el-button type="primary" size="small" @click="checkHealth" :loading="checkingHealth">
            <el-icon><Refresh /></el-icon>
            检查健康状态
          </el-button>
        </div>
      </template>

      <div v-if="healthStatus" class="health-content">
        <div class="health-overview">
          <div class="health-indicator">
            <el-icon 
              :size="32" 
              :color="getHealthColor(healthStatus.status)"
            >
              <CircleCheck v-if="healthStatus.status === 'healthy'" />
              <Warning v-else-if="healthStatus.status === 'warning'" />
              <CircleClose v-else />
            </el-icon>
            <div class="health-text">
              <div class="health-status">{{ getHealthText(healthStatus.status) }}</div>
              <div class="health-time">{{ formatDateTime(healthStatus.timestamp) }}</div>
            </div>
          </div>
        </div>

        <el-divider />

        <div class="health-details">
          <el-row :gutter="24">
            <el-col :span="8">
              <div class="detail-item">
                <div class="detail-title">上传目录</div>
                <div class="detail-content">
                  <el-tag :type="healthStatus.checks.upload_directory.exists ? 'success' : 'danger'">
                    {{ healthStatus.checks.upload_directory.exists ? '正常' : '异常' }}
                  </el-tag>
                  <div class="detail-desc">{{ healthStatus.checks.upload_directory.path }}</div>
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-item">
                <div class="detail-title">磁盘空间</div>
                <div class="detail-content">
                  <el-tag :type="healthStatus.checks.disk_space.sufficient ? 'success' : 'warning'">
                    {{ healthStatus.checks.disk_space.free_space_gb.toFixed(2) }} GB
                  </el-tag>
                  <div class="detail-desc">可用空间</div>
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-item">
                <div class="detail-title">内存使用</div>
                <div class="detail-content">
                  <el-tag :type="healthStatus.checks.memory.usage_percent < 80 ? 'success' : 'warning'">
                    {{ healthStatus.checks.memory.usage_percent }}%
                  </el-tag>
                  <div class="detail-desc">{{ healthStatus.checks.memory.available_mb.toFixed(0) }} MB 可用</div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
    </el-card>

    <el-row :gutter="24">
      <!-- 系统统计 -->
      <el-col :span="12">
        <el-card class="stats-card">
          <template #header>
            <div class="card-header">
              <span>系统统计</span>
              <el-button type="primary" size="small" @click="loadSystemStats" :loading="loadingStats">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>

          <div v-loading="loadingStats" class="stats-content">
            <div v-if="systemStats" class="stats-grid">
              <div class="stat-item">
                <div class="stat-icon">
                  <el-icon size="24" color="#409eff"><Document /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ systemStats.total_files_processed }}</div>
                  <div class="stat-label">处理文件总数</div>
                </div>
              </div>

              <div class="stat-item">
                <div class="stat-icon">
                  <el-icon size="24" color="#67c23a"><DataAnalysis /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ systemStats.total_records_analyzed.toLocaleString() }}</div>
                  <div class="stat-label">分析记录总数</div>
                </div>
              </div>

              <div class="stat-item">
                <div class="stat-icon">
                  <el-icon size="24" color="#e6a23c"><PieChart /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ systemStats.average_filter_rate }}%</div>
                  <div class="stat-label">平均过滤率</div>
                </div>
              </div>

              <div class="stat-item">
                <div class="stat-icon">
                  <el-icon size="24" color="#f56c6c"><Loading /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ systemStats.active_tasks }}</div>
                  <div class="stat-label">活跃任务数</div>
                </div>
              </div>

              <div class="stat-item full-width">
                <div class="stat-icon">
                  <el-icon size="24" color="#909399"><Timer /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ systemStats.system_uptime }}</div>
                  <div class="stat-label">系统运行时间</div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 系统配置 -->
      <el-col :span="12">
        <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <span>系统配置</span>
              <el-button type="primary" size="small" @click="loadSystemConfig" :loading="loadingConfig">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>

          <div v-loading="loadingConfig" class="config-content">
            <div v-if="systemConfig">
              <el-descriptions :column="1" border>
                <el-descriptions-item label="项目名称">
                  {{ systemConfig.project_name }}
                </el-descriptions-item>
                <el-descriptions-item label="版本号">
                  <el-tag size="small">{{ systemConfig.version }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="调试模式">
                  <el-tag :type="systemConfig.debug_mode ? 'warning' : 'success'">
                    {{ systemConfig.debug_mode ? '开启' : '关闭' }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="最大文件大小">
                  {{ systemConfig.upload_config.max_file_size_mb }} MB
                </el-descriptions-item>
                <el-descriptions-item label="支持格式">
                  <div class="file-formats">
                    <el-tag 
                      v-for="ext in systemConfig.upload_config.allowed_extensions" 
                      :key="ext"
                      size="small"
                      class="format-tag"
                    >
                      {{ ext }}
                    </el-tag>
                  </div>
                </el-descriptions-item>
                <el-descriptions-item label="最大并发分析">
                  {{ systemConfig.analysis_config.max_concurrent_analysis }}
                </el-descriptions-item>
                <el-descriptions-item label="分析超时">
                  {{ systemConfig.analysis_config.analysis_timeout_seconds }}s
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统操作 -->
    <el-card class="operations-card">
      <template #header>
        <span>系统操作</span>
      </template>

      <div class="operations-content">
        <div class="operation-item">
          <div class="operation-info">
            <div class="operation-title">系统清理</div>
            <div class="operation-desc">清理临时文件和过期数据</div>
          </div>
          <el-button type="warning" @click="cleanupSystem" :loading="cleaning">
            <el-icon><Delete /></el-icon>
            执行清理
          </el-button>
        </div>

        <el-divider />

        <div class="operation-item">
          <div class="operation-info">
            <div class="operation-title">查看日志</div>
            <div class="operation-desc">查看系统运行日志</div>
          </div>
          <el-button type="info" @click="showLogsDialog">
            <el-icon><View /></el-icon>
            查看日志
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 日志对话框 -->
    <el-dialog
      v-model="logsDialogVisible"
      title="系统日志"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-loading="loadingLogs" class="logs-content">
        <div v-if="systemLogs.length > 0" class="logs-list">
          <div v-for="log in systemLogs" :key="log.timestamp" class="log-item">
            <div class="log-time">{{ formatDateTime(log.timestamp) }}</div>
            <el-tag :type="getLogLevelType(log.level)" size="small">{{ log.level }}</el-tag>
            <div class="log-message">{{ log.message }}</div>
          </div>
        </div>
        <el-empty v-else description="暂无日志记录" />
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="loadSystemLogs">刷新</el-button>
          <el-button type="primary" @click="logsDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh,
  CircleCheck,
  Warning,
  CircleClose,
  Document,
  DataAnalysis,
  PieChart,
  Loading,
  Timer,
  Delete,
  View
} from '@element-plus/icons-vue'
import { systemAPI } from '@/api'
import dayjs from 'dayjs'

// 响应式数据
const checkingHealth = ref(false)
const loadingStats = ref(false)
const loadingConfig = ref(false)
const loadingLogs = ref(false)
const cleaning = ref(false)

const healthStatus = ref<any>(null)
const systemStats = ref<any>(null)
const systemConfig = ref<any>(null)
const systemLogs = ref<any[]>([])

const logsDialogVisible = ref(false)

// 检查系统健康状态
const checkHealth = async () => {
  try {
    checkingHealth.value = true
    const response = await systemAPI.healthCheck()
    healthStatus.value = response.data
  } catch (error) {
    console.error('Failed to check health:', error)
  } finally {
    checkingHealth.value = false
  }
}

// 加载系统统计
const loadSystemStats = async () => {
  try {
    loadingStats.value = true
    const response = await systemAPI.getStats()
    systemStats.value = response.data
  } catch (error) {
    console.error('Failed to load system stats:', error)
  } finally {
    loadingStats.value = false
  }
}

// 加载系统配置
const loadSystemConfig = async () => {
  try {
    loadingConfig.value = true
    const response = await systemAPI.getConfig()
    systemConfig.value = response.data
  } catch (error) {
    console.error('Failed to load system config:', error)
  } finally {
    loadingConfig.value = false
  }
}

// 加载系统日志
const loadSystemLogs = async () => {
  try {
    loadingLogs.value = true
    const response = await systemAPI.getLogs()
    systemLogs.value = response.data.logs
  } catch (error) {
    console.error('Failed to load system logs:', error)
  } finally {
    loadingLogs.value = false
  }
}

// 系统清理
const cleanupSystem = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要执行系统清理吗？这将删除临时文件和过期数据。',
      '确认清理',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    cleaning.value = true
    const response = await systemAPI.cleanup()
    
    ElMessage.success(
      `清理完成：清理了 ${response.data.cleaned_files} 个文件，释放 ${response.data.cleaned_size_mb} MB 空间`
    )
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to cleanup system:', error)
    }
  } finally {
    cleaning.value = false
  }
}

// 显示日志对话框
const showLogsDialog = () => {
  logsDialogVisible.value = true
  loadSystemLogs()
}

// 获取健康状态颜色
const getHealthColor = (status: string) => {
  switch (status) {
    case 'healthy':
      return '#67c23a'
    case 'warning':
      return '#e6a23c'
    case 'error':
      return '#f56c6c'
    default:
      return '#909399'
  }
}

// 获取健康状态文本
const getHealthText = (status: string) => {
  switch (status) {
    case 'healthy':
      return '系统健康'
    case 'warning':
      return '系统警告'
    case 'error':
      return '系统错误'
    default:
      return '未知状态'
  }
}

// 获取日志级别类型
const getLogLevelType = (level: string) => {
  switch (level.toLowerCase()) {
    case 'error':
      return 'danger'
    case 'warning':
      return 'warning'
    case 'info':
      return 'success'
    case 'debug':
      return 'info'
    default:
      return 'info'
  }
}

// 格式化日期时间
const formatDateTime = (dateTime: string) => {
  return dayjs(dateTime).format('YYYY-MM-DD HH:mm:ss')
}

// 组件挂载
onMounted(() => {
  checkHealth()
  loadSystemStats()
  loadSystemConfig()
})
</script>

<style scoped>
.system-container {
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

.health-card {
  margin-bottom: 24px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.health-content {
  padding: 8px 0;
}

.health-overview {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.health-indicator {
  display: flex;
  align-items: center;
  gap: 16px;
}

.health-text {
  text-align: left;
}

.health-status {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.health-time {
  font-size: 12px;
  color: #606266;
  margin-top: 4px;
}

.health-details {
  margin-top: 16px;
}

.detail-item {
  text-align: center;
}

.detail-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.detail-desc {
  font-size: 12px;
  color: #606266;
}

.stats-card,
.config-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.stats-content {
  min-height: 200px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background-color: #fafafa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.stat-item.full-width {
  grid-column: 1 / -1;
}

.stat-icon {
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: #606266;
  margin-top: 4px;
}

.config-content {
  min-height: 200px;
}

.file-formats {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.format-tag {
  margin: 0;
}

.operations-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.operations-content {
  padding: 8px 0;
}

.operation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
}

.operation-info {
  flex: 1;
}

.operation-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.operation-desc {
  font-size: 12px;
  color: #606266;
}

.logs-content {
  max-height: 400px;
  overflow-y: auto;
}

.logs-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background-color: #fafafa;
  border-radius: 4px;
  font-size: 12px;
}

.log-time {
  color: #606266;
  min-width: 140px;
}

.log-message {
  flex: 1;
  color: #303133;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
