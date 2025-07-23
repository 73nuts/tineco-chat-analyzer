<template>
  <div class="analysis-detail-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="$router.go(-1)" circle>
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <div class="header-info">
          <h1>分析详情</h1>
          <p v-if="taskInfo">{{ taskInfo.filename }}</p>
        </div>
      </div>
      <div class="header-actions">
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="8" animated />
    </div>

    <!-- 任务状态卡片 -->
    <el-card v-if="taskInfo && !loading" class="status-card">
      <div class="status-content">
        <div class="status-info">
          <div class="status-item">
            <span class="label">任务状态:</span>
            <el-tag :type="getStatusType(taskInfo.status)">
              {{ getStatusText(taskInfo.status) }}
            </el-tag>
          </div>
          <div class="status-item">
            <span class="label">创建时间:</span>
            <span>{{ formatDateTime(taskInfo.created_time) }}</span>
          </div>
          <div class="status-item" v-if="taskInfo.completed_time">
            <span class="label">完成时间:</span>
            <span>{{ formatDateTime(taskInfo.completed_time) }}</span>
          </div>
          <div class="status-item" v-if="taskInfo.error_message">
            <span class="label">错误信息:</span>
            <span class="error-message">{{ taskInfo.error_message }}</span>
          </div>
        </div>
        <div class="progress-section" v-if="taskInfo.status === 'processing'">
          <el-progress 
            :percentage="taskInfo.progress" 
            :stroke-width="12"
            :color="getProgressColor(taskInfo.status)"
          />
          <p class="progress-message">{{ taskInfo.status_message }}</p>
        </div>
      </div>
    </el-card>

    <!-- 分析结果 -->
    <div v-if="analysisResult && !loading" class="results-section">
      <!-- 概览统计卡片 -->
      <div class="overview-cards">
        <el-card class="overview-card">
          <div class="card-content">
            <div class="card-icon">
              <el-icon size="32" color="#409eff"><DataBoard /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-value">{{ analysisResult.total_records.toLocaleString() }}</div>
              <div class="card-label">总记录数</div>
            </div>
          </div>
        </el-card>

        <el-card class="overview-card">
          <div class="card-content">
            <div class="card-icon">
              <el-icon size="32" color="#f56c6c"><Filter /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-value">{{ analysisResult.filtered_records.toLocaleString() }}</div>
              <div class="card-label">过滤记录数</div>
            </div>
          </div>
        </el-card>

        <el-card class="overview-card">
          <div class="card-content">
            <div class="card-icon">
              <el-icon size="32" color="#67c23a"><CircleCheck /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-value">{{ analysisResult.valid_records.toLocaleString() }}</div>
              <div class="card-label">有效记录数</div>
            </div>
          </div>
        </el-card>

        <el-card class="overview-card">
          <div class="card-content">
            <div class="card-icon">
              <el-icon size="32" color="#e6a23c"><PieChart /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-value">{{ analysisResult.filter_rate }}%</div>
              <div class="card-label">过滤率</div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 图表区域 -->
      <div class="charts-section">
        <el-row :gutter="24">
          <el-col :span="12">
            <el-card class="chart-card">
              <template #header>
                <span>过滤条件分布</span>
              </template>
              <div ref="pieChartRef" class="chart-container"></div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="chart-card">
              <template #header>
                <span>过滤统计对比</span>
              </template>
              <div ref="barChartRef" class="chart-container"></div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 详细统计表格 -->
      <el-card class="details-card">
        <template #header>
          <span>详细统计信息</span>
        </template>
        <el-table 
          :data="statisticsData" 
          style="width: 100%"
          @row-click="handleTableRowClick"
          highlight-current-row
        >
          <el-table-column prop="category" label="过滤类别" width="200">
            <template #default="{ row }">
              <div class="category-cell">
                <div class="category-color" :style="{ backgroundColor: row.color }"></div>
                <span>{{ row.category }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="count" label="数量" width="120">
            <template #default="{ row }">
              <strong>{{ row.count.toLocaleString() }}</strong>
            </template>
          </el-table-column>
          <el-table-column prop="percentage" label="占比" width="120">
            <template #default="{ row }">
              <el-tag size="small">{{ row.percentage }}%</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="说明" min-width="300">
            <template #default="{ row }">
              <span class="description">{{ row.description }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button 
                v-if="row.count > 0"
                @click.stop="handleTableRowClick(row)"
                type="primary" 
                size="small"
                link
              >
                查看详情
              </el-button>
              <span v-else class="no-data-text">无数据</span>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 错误状态 -->
    <el-result
      v-if="error && !loading"
      icon="error"
      title="加载失败"
      :sub-title="error"
    >
      <template #extra>
        <el-button type="primary" @click="refreshData">重试</el-button>
      </template>
    </el-result>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as echarts from 'echarts'
import {
  ArrowLeft,
  Refresh,
  DataBoard,
  Filter,
  CircleCheck,
  PieChart
} from '@element-plus/icons-vue'
import { analysisAPI, type AnalysisTask, type AnalysisResult } from '@/api'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(true)
const error = ref('')
const taskInfo = ref<AnalysisTask | null>(null)
const analysisResult = ref<AnalysisResult | null>(null)

// 图表引用
const pieChartRef = ref<HTMLElement>()
const barChartRef = ref<HTMLElement>()

// 图表实例
let pieChart: echarts.ECharts | null = null
let barChart: echarts.ECharts | null = null

// 任务ID
const taskId = computed(() => route.params.taskId as string)

// 统计数据
const statisticsData = computed(() => {
  if (!analysisResult.value) return []
  
  const result = analysisResult.value
  const colors = ['#f56c6c', '#e6a23c', '#409eff', '#67c23a', '#909399', '#c0c4cc']
  
  return [
    {
      category: '早晨消息过滤',
      count: result.early_morning_count,
      percentage: ((result.early_morning_count / result.total_records) * 100).toFixed(2),
      description: '过滤0-8点之间发送的消息',
      color: colors[0]
    },
    {
      category: '售后人员参与',
      count: result.staff_involved_count,
      percentage: ((result.staff_involved_count / result.total_records) * 100).toFixed(2),
      description: '过滤包含售后人员的对话',
      color: colors[1]
    },
    {
      category: '服务助手消息',
      count: result.service_assistant_count,
      percentage: ((result.service_assistant_count / result.total_records) * 100).toFixed(2),
      description: '过滤纯服务助手发送的消息',
      color: colors[2]
    },
    {
      category: '地址确认消息',
      count: result.address_confirm_count,
      percentage: ((result.address_confirm_count / result.total_records) * 100).toFixed(2),
      description: '过滤收货地址确认相关消息',
      color: colors[3]
    },
    {
      category: '解析错误',
      count: result.parse_error_count,
      percentage: ((result.parse_error_count / result.total_records) * 100).toFixed(2),
      description: '消息格式解析失败的记录',
      color: colors[4]
    },
    {
      category: '空记录',
      count: result.empty_records_count,
      percentage: ((result.empty_records_count / result.total_records) * 100).toFixed(2),
      description: '没有消息内容的空记录',
      color: colors[5]
    }
  ]
})

// 过滤类型映射（从中文名称到后端类型标识）
const filterTypeMap: Record<string, string> = {
  '早晨消息过滤': 'early_morning',
  '售后人员参与': 'staff_involvement',
  '服务助手消息': 'service_assistant',
  '地址确认消息': 'address_confirmation',
  '解析错误': 'parse_error',
  '空记录': 'empty_record'
}

// 处理图表点击事件
const handleChartClick = (params: any) => {
  const categoryName = params.name || params.data?.name
  if (!categoryName) return
  
  const filterType = filterTypeMap[categoryName]
  if (filterType) {
    navigateToFilterDetail(filterType)
  }
}

// 处理表格行点击事件
const handleTableRowClick = (row: any) => {
  const filterType = filterTypeMap[row.category]
  if (filterType && row.count > 0) {
    navigateToFilterDetail(filterType)
  }
}

// 跳转到过滤详情页面
const navigateToFilterDetail = (filterType: string) => {
  router.push(`/analysis/${taskId.value}/filter-details/${filterType}`)
}

// 刷新数据
const refreshData = async () => {
  try {
    loading.value = true
    error.value = ''
    
    // 获取任务信息
    const taskResponse = await analysisAPI.getTaskStatus(taskId.value)
    taskInfo.value = taskResponse.data
    
    // 如果任务已完成，获取分析结果
    if (taskInfo.value.status === 'completed') {
      const resultResponse = await analysisAPI.getResult(taskId.value)
      analysisResult.value = resultResponse.data.result
      
      console.log('Analysis result loaded:', analysisResult.value)
      console.log('Statistics data:', statisticsData.value)
      
      // 渲染图表
      await nextTick()
      renderCharts()
    }
  } catch (err: any) {
    error.value = err.message || '加载数据失败'
    console.error('Failed to load analysis detail:', err)
  } finally {
    loading.value = false
  }
}

// 渲染图表
const renderCharts = async () => {
  if (!analysisResult.value) return
  
  // 等待DOM更新
  await nextTick()
  
  // 延迟渲染以确保容器完全可见
  setTimeout(() => {
    renderPieChart()
    renderBarChart()
  }, 300)
}

// 渲染饼图
const renderPieChart = () => {
  console.log('renderPieChart called', { 
    hasRef: !!pieChartRef.value, 
    hasResult: !!analysisResult.value,
    refDimensions: pieChartRef.value ? {
      width: pieChartRef.value.offsetWidth,
      height: pieChartRef.value.offsetHeight
    } : null
  })
  
  if (!pieChartRef.value || !analysisResult.value) {
    console.warn('Missing pieChartRef or analysisResult')
    return
  }
  
  if (pieChart) {
    pieChart.dispose()
  }
  
  try {
    pieChart = echarts.init(pieChartRef.value)
  } catch (error) {
    console.error('Failed to init pie chart:', error)
    return
  }
  
  const data = statisticsData.value.filter(item => item.count > 0).map(item => ({
    name: item.category,
    value: item.count,
    itemStyle: {
      color: item.color
    }
  }))
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      textStyle: {
        fontSize: 12
      }
    },
    series: [
      {
        name: '过滤统计',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['60%', '50%'],
        avoidLabelOverlap: false,
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '18',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: data
      }
    ]
  }
  
  pieChart.setOption(option)
  
  // 添加点击事件监听
  pieChart.off('click') // 移除之前的监听器
  pieChart.on('click', handleChartClick)
}

// 渲染柱状图
const renderBarChart = () => {
  console.log('renderBarChart called', { 
    hasRef: !!barChartRef.value, 
    hasResult: !!analysisResult.value,
    refDimensions: barChartRef.value ? {
      width: barChartRef.value.offsetWidth,
      height: barChartRef.value.offsetHeight
    } : null
  })
  
  if (!barChartRef.value || !analysisResult.value) {
    console.warn('Missing barChartRef or analysisResult')
    return
  }
  
  if (barChart) {
    barChart.dispose()
  }
  
  try {
    barChart = echarts.init(barChartRef.value)
  } catch (error) {
    console.error('Failed to init bar chart:', error)
    return
  }
  
  const data = statisticsData.value
  const categories = data.map(item => item.category)
  const values = data.map(item => item.count)
  const colors = data.map(item => item.color)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params: any) {
        const item = params[0]
        const percentage = ((item.value / analysisResult.value!.total_records) * 100).toFixed(2)
        return `${item.name}<br/>数量: ${item.value.toLocaleString()}<br/>占比: ${percentage}%`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: {
        interval: 0,
        rotate: 45,
        fontSize: 10
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: function(value: number) {
          return value.toLocaleString()
        }
      }
    },
    series: [
      {
        name: '过滤数量',
        type: 'bar',
        data: values.map((value, index) => ({
          value,
          itemStyle: {
            color: colors[index]
          }
        })),
        emphasis: {
          focus: 'series'
        }
      }
    ]
  }
  
  barChart.setOption(option)
  
  // 添加点击事件监听
  barChart.off('click') // 移除之前的监听器
  barChart.on('click', (params: any) => {
    // 对于柱状图，需要通过索引获取类别名称
    const categoryName = categories[params.dataIndex]
    if (categoryName) {
      handleChartClick({ name: categoryName })
    }
  })
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

// 组件挂载
onMounted(() => {
  refreshData()
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    if (pieChart) pieChart.resize()
    if (barChart) barChart.resize()
  })
})
</script>

<style scoped>
.analysis-detail-container {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-info h1 {
  font-size: 24px;
  color: #303133;
  margin-bottom: 4px;
}

.header-info p {
  color: #606266;
  font-size: 14px;
  margin: 0;
}

.loading-container {
  margin: 40px 0;
}

.status-card {
  margin-bottom: 24px;
}

.status-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-info {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-item .label {
  color: #606266;
  font-weight: 500;
}

.error-message {
  color: #f56c6c;
}

.progress-section {
  min-width: 300px;
}

.progress-message {
  margin-top: 8px;
  color: #606266;
  font-size: 12px;
  text-align: center;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.overview-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.card-icon {
  flex-shrink: 0;
}

.card-info {
  flex: 1;
}

.card-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
}

.card-label {
  font-size: 14px;
  color: #606266;
  margin-top: 4px;
}

.charts-section {
  margin-bottom: 24px;
}

.chart-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.chart-container {
  height: 300px;
  width: 100%;
}

.details-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.category-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.description {
  color: #606266;
  font-size: 12px;
}

/* 增强表格行的可点击样式 */
:deep(.el-table__row) {
  cursor: pointer;
  transition: background-color 0.2s;
}

:deep(.el-table__row:hover) {
  background-color: var(--el-table-row-hover-bg-color);
}

.no-data-text {
  color: #c0c4cc;
  font-size: 12px;
}

/* 图表容器增强点击提示 */
.chart-container {
  cursor: pointer;
  transition: opacity 0.2s;
}

.chart-container:hover {
  opacity: 0.9;
}
</style>
