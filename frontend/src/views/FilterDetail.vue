<template>
  <div class="filter-detail-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <el-row justify="space-between" align="middle">
        <el-col :span="18">
          <h1>{{ filterTypeName }} - 过滤详情</h1>
          <p class="subtitle">共找到 {{ totalCount }} 条记录</p>
        </el-col>
        <el-col :span="6" class="text-right">
          <el-button @click="goBack" type="default">
            <el-icon><ArrowLeft /></el-icon>
            返回分析详情
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 加载状态 -->
    <el-card v-if="loading" v-loading="loading" class="loading-card">
      <div style="height: 200px; display: flex; align-items: center; justify-content: center;">
        <span>正在加载过滤详情...</span>
      </div>
    </el-card>

    <!-- 记录列表 -->
    <el-card v-else class="records-card">
      <template #header>
        <div class="card-header">
          <span>过滤记录列表</span>
          <el-tag :type="getFilterTypeTag(filterType)">{{ filterTypeName }}</el-tag>
        </div>
      </template>

      <!-- 记录表格 -->
      <el-table :data="records" stripe style="width: 100%" empty-text="暂无数据">
        <el-table-column prop="record_id" label="记录ID" width="200" />
        <el-table-column label="过滤原因" width="150">
          <template #default="{ row }">
            <span>{{ filterTypeNameMap[row.filter_type] || row.filter_reason }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="record_index" label="行号" width="80" />
        
        <!-- 根据filter_type显示不同的特定字段 -->
        <el-table-column label="详情信息" min-width="200">
          <template #default="{ row }">
            <div class="detail-info">
              <div v-if="row.staff_name" class="info-item">
                <el-tag size="small" type="warning">售后人员</el-tag>
                <span>{{ row.staff_name }}</span>
              </div>
              <div v-if="row.timestamp" class="info-item">
                <el-tag size="small" type="info">时间</el-tag>
                <span>{{ formatTime(row.timestamp) }}</span>
              </div>
              <div v-if="row.address_content" class="info-item">
                <el-tag size="small" type="success">地址</el-tag>
                <span class="address-text">{{ truncateText(row.address_content, 50) }}</span>
              </div>
              <div v-if="row.service_message" class="info-item">
                <el-tag size="small" type="primary">服务消息</el-tag>
                <span class="service-text">{{ truncateText(row.service_message, 50) }}</span>
              </div>
              <div v-if="row.error_message" class="info-item">
                <el-tag size="small" type="danger">错误</el-tag>
                <span class="error-text">{{ row.error_message }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <!-- 操作列 -->
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button 
              @click="viewChatDetail(row.record_id)" 
              type="primary" 
              size="small"
              :loading="chatDetailLoading === row.record_id"
            >
              查看完整对话
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="totalCount"
          :page-sizes="[20, 50, 100]"
          :small="false"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 聊天详情弹窗 -->
    <el-dialog
      v-model="chatDetailVisible"
      :title="`聊天记录详情 - ${selectedRecordId}`"
      width="80%"
      :before-close="handleCloseDialog"
    >
      <div v-if="chatDetailLoading === 'dialog'">
        <el-skeleton :rows="5" animated />
      </div>
      <div v-else-if="chatDetail">
        <!-- 过滤信息 -->
        <el-card class="filter-info-card" shadow="never">
          <template #header>
            <span>过滤信息</span>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="过滤类型">{{ filterTypeNameMap[chatDetail.filter_info.filter_type] || chatDetail.filter_info.filter_type }}</el-descriptions-item>
            <el-descriptions-item label="过滤原因">{{ filterTypeNameMap[chatDetail.filter_info.filter_type] || chatDetail.filter_info.filter_reason }}</el-descriptions-item>
            <el-descriptions-item label="售后人员" v-if="chatDetail.filter_info.staff_name">
              {{ chatDetail.filter_info.staff_name }}
            </el-descriptions-item>
            <el-descriptions-item label="时间戳" v-if="chatDetail.filter_info.timestamp">
              {{ formatTime(chatDetail.filter_info.timestamp) }}
            </el-descriptions-item>
            <el-descriptions-item label="地址内容" v-if="chatDetail.filter_info.address_content">
              {{ chatDetail.filter_info.address_content }}
            </el-descriptions-item>
            <el-descriptions-item label="服务消息" v-if="chatDetail.filter_info.service_message">
              {{ chatDetail.filter_info.service_message }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 原始聊天数据 -->
        <el-card class="raw-data-card" shadow="never">
          <template #header>
            <span>原始聊天记录</span>
          </template>
          <div class="chat-messages" v-if="chatDetail.raw_data.messages">
            <div 
              v-for="(message, index) in parsedMessages" 
              :key="index" 
              class="message-item"
            >
              <div class="message-header">
                <el-tag size="small" :type="message.sender_nick === 'tineco添可官方旗舰店:服务助手' ? 'primary' : 'info'">
                  {{ message.sender_nick || '未知发送者' }}
                </el-tag>
                <span class="message-time">{{ formatTime(message.time) }}</span>
              </div>
              <div class="message-content">
                {{ getMessageContent(message) }}
              </div>
            </div>
          </div>
          <div v-else>
            <el-empty description="无聊天消息数据" />
          </div>
        </el-card>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="chatDetailVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import * as api from '@/api'

// 路由相关
const route = useRoute()
const router = useRouter()
const taskId = route.params.taskId as string
const filterType = route.params.filterType as string

// 数据状态
const loading = ref(true)
const records = ref<any[]>([])
const totalCount = ref(0)
const totalPages = ref(0)
const currentPage = ref(1)
const pageSize = ref(50)

// 聊天详情相关
const chatDetailVisible = ref(false)
const chatDetailLoading = ref<string | null>(null)
const chatDetail = ref<any>(null)
const selectedRecordId = ref('')

// 过滤类型映射
const filterTypeNameMap: Record<string, string> = {
  'early_morning': '早晨消息(0-8点)',
  'staff_involvement': '售后人员参与',
  'service_assistant': '服务助手消息',
  'address_confirmation': '收货地址确认消息',
  'parse_error': '解析错误',
  'empty_record': '空记录'
}

// 计算属性
const filterTypeName = computed(() => {
  return filterTypeNameMap[filterType] || filterType
})

const parsedMessages = computed(() => {
  if (!chatDetail.value?.raw_data?.messages) return []
  try {
    const messages = typeof chatDetail.value.raw_data.messages === 'string' 
      ? JSON.parse(chatDetail.value.raw_data.messages)
      : chatDetail.value.raw_data.messages
    return Array.isArray(messages) ? messages : []
  } catch (e) {
    console.error('解析消息数据失败:', e)
    return []
  }
})

// 方法
const loadData = async (page: number = 1) => {
  try {
    loading.value = true
    console.log('Loading filter details:', { taskId, filterType, page, pageSize: pageSize.value })
    
    const response = await api.getFilterDetails(taskId, filterType, page, pageSize.value)
    console.log('Filter details response:', response)
    
    if (response.success) {
      const data = response.data
      records.value = data.records || []
      totalCount.value = data.total_count || 0
      totalPages.value = data.total_pages || 0
      currentPage.value = data.page || 1
      console.log('Data loaded successfully:', { totalCount: totalCount.value, recordsCount: records.value.length })
    } else {
      console.error('API returned error:', response.message)
      ElMessage.error(response.message || '加载数据失败')
    }
  } catch (error) {
    console.error('加载过滤详情失败:', error)
    ElMessage.error('加载数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const viewChatDetail = async (recordId: string) => {
  try {
    chatDetailLoading.value = recordId
    selectedRecordId.value = recordId
    console.log('Loading chat detail:', { taskId, recordId })
    
    const response = await api.getChatRecordDetail(taskId, recordId)
    console.log('Chat detail response:', response)
    
    if (response.success) {
      chatDetail.value = response.data
      chatDetailVisible.value = true
    } else {
      console.error('API returned error:', response.message)
      ElMessage.error(response.message || '获取聊天详情失败')
    }
  } catch (error) {
    console.error('获取聊天详情失败:', error)
    ElMessage.error('获取聊天详情失败，请稍后重试')
  } finally {
    chatDetailLoading.value = null
  }
}

const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize
  currentPage.value = 1
  loadData(1)
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadData(page)
}

const handleCloseDialog = () => {
  chatDetailVisible.value = false
  chatDetail.value = null
  selectedRecordId.value = ''
}

const goBack = () => {
  router.push(`/analysis/${taskId}`)
}

const getFilterTypeTag = (type: string): 'primary' | 'success' | 'warning' | 'info' | 'danger' => {
  const tagMap: Record<string, 'primary' | 'success' | 'warning' | 'info' | 'danger'> = {
    'early_morning': 'info',
    'staff_involvement': 'warning',
    'service_assistant': 'primary',
    'address_confirmation': 'success',
    'parse_error': 'danger',
    'empty_record': 'info'
  }
  return tagMap[type] || 'info'
}

const formatTime = (timestamp: string | null): string => {
  if (!timestamp) return '-'
  try {
    return new Date(timestamp).toLocaleString('zh-CN')
  } catch (e) {
    return timestamp
  }
}

const truncateText = (text: string, maxLength: number): string => {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

const getMessageContent = (message: any): string => {
  if (!message || !message.content) return '无内容'
  
  // 如果content直接是字符串
  if (typeof message.content === 'string') {
    return message.content || '无内容'
  }
  
  // 如果content是对象
  if (typeof message.content === 'object') {
    // 优先显示text字段
    if (message.content.text) {
      return message.content.text
    }
    
    // 如果是图片或其他特殊类型，显示summary或degradeText
    if (message.content.summary) {
      return `[${message.content.summary}]`
    }
    
    if (message.content.degradeText) {
      return `[${message.content.degradeText}]`
    }
    
    // 如果有data字段，可能是图片或其他媒体
    if (message.content.data) {
      return '[图片/媒体内容]'
    }
    
    // 其他情况，尝试将对象转为JSON字符串
    try {
      return JSON.stringify(message.content)
    } catch (e) {
      return '[复杂内容]'
    }
  }
  
  return '无内容'
}

// 生命周期
onMounted(() => {
  if (!taskId || !filterType) {
    ElMessage.error('参数错误')
    router.push('/analysis')
    return
  }
  
  loadData()
})
</script>

<style scoped>
.filter-detail-container {
  padding: 20px;
  min-height: calc(100vh - 80px);
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.page-header .subtitle {
  margin: 5px 0 0 0;
  color: #909399;
  font-size: 14px;
}

.loading-card {
  margin-bottom: 20px;
}

.records-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-info .info-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  gap: 8px;
}

.detail-info .info-item:last-child {
  margin-bottom: 0;
}

.address-text,
.service-text {
  font-size: 12px;
  color: #606266;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.error-text {
  font-size: 12px;
  color: #f56c6c;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.filter-info-card {
  margin-bottom: 20px;
}

.raw-data-card {
  max-height: 400px;
  overflow-y: auto;
}

.chat-messages {
  max-height: 350px;
  overflow-y: auto;
}

.message-item {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
  background: #fafafa;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.message-time {
  font-size: 12px;
  color: #909399;
}

.message-content {
  color: #303133;
  line-height: 1.5;
  font-size: 14px;
}

.text-right {
  text-align: right;
}

.dialog-footer {
  text-align: center;
}
</style>