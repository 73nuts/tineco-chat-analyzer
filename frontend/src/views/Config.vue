<template>
  <div class="config-container">
    <div class="page-header">
      <h1>配置管理</h1>
      <p>管理过滤规则和售后人员名单</p>
    </div>

    <el-row :gutter="24">
      <!-- 过滤规则配置 -->
      <el-col :span="12">
        <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <span>过滤规则配置</span>
              <el-button type="primary" size="small" @click="saveFilterRules" :loading="savingRules">
                <el-icon><Check /></el-icon>
                保存规则
              </el-button>
            </div>
          </template>

          <div class="rules-list" v-loading="loadingRules">
            <div v-for="rule in filterRules" :key="rule.rule_id" class="rule-item">
              <div class="rule-header">
                <el-switch
                  v-model="rule.enabled"
                  :disabled="savingRules"
                  @change="onRuleChange"
                />
                <div class="rule-info">
                  <div class="rule-name">{{ rule.name }}</div>
                  <div class="rule-description">{{ rule.description }}</div>
                </div>
              </div>
              
              <!-- 规则参数配置 -->
              <div v-if="rule.rule_id === 'early_morning_filter' && rule.enabled" class="rule-params">
                <el-divider content-position="left">时间范围设置</el-divider>
                <div class="param-row">
                  <label>开始时间:</label>
                  <el-time-picker
                    v-model="earlyMorningStart"
                    format="HH:mm"
                    placeholder="选择开始时间"
                    :disabled="savingRules"
                  />
                </div>
                <div class="param-row">
                  <label>结束时间:</label>
                  <el-time-picker
                    v-model="earlyMorningEnd"
                    format="HH:mm"
                    placeholder="选择结束时间"
                    :disabled="savingRules"
                  />
                </div>
              </div>
            </div>
          </div>

          <el-alert
            v-if="rulesChanged"
            title="配置已修改"
            type="warning"
            description="请点击保存按钮保存您的更改"
            show-icon
            :closable="false"
            class="rules-alert"
          />
        </el-card>
      </el-col>

      <!-- 售后人员管理 -->
      <el-col :span="12">
        <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <span>售后人员管理 ({{ staffList.length }}人)</span>
              <div class="header-actions">
                <el-button type="success" size="small" @click="showAddStaffDialog">
                  <el-icon><Plus /></el-icon>
                  添加人员
                </el-button>
                <el-button type="warning" size="small" @click="showExcelUploadDialog">
                  <el-icon><Upload /></el-icon>
                  Excel导入
                </el-button>
                <el-button type="primary" size="small" @click="refreshStaffList">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
            </div>
          </template>

          <div class="staff-section" v-loading="loadingStaff">
            <!-- 搜索框 -->
            <el-input
              v-model="staffSearchText"
              placeholder="搜索售后人员..."
              :prefix-icon="Search"
              clearable
              class="staff-search"
            />

            <!-- 人员列表 -->
            <div class="staff-list">
              <div
                v-for="staff in filteredStaffList"
                :key="staff.nick_name"
                class="staff-item"
              >
                <div class="staff-info">
                  <el-avatar size="small">
                    <el-icon><User /></el-icon>
                  </el-avatar>
                  <div class="staff-details">
                    <div class="staff-name">{{ staff.nick_name }}</div>
                    <div class="staff-status">
                      <el-tag size="small" :type="staff.status === 'active' ? 'success' : 'info'">
                        {{ staff.status === 'active' ? '活跃' : '非活跃' }}
                      </el-tag>
                    </div>
                  </div>
                </div>
                <el-button
                  type="danger"
                  size="small"
                  text
                  @click="removeStaff(staff)"
                  :disabled="removingStaff"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>

            <!-- 空状态 -->
            <el-empty
              v-if="filteredStaffList.length === 0 && !loadingStaff"
              :description="staffSearchText ? '未找到匹配的人员' : '暂无售后人员'"
              :image-size="80"
            >
              <el-button v-if="!staffSearchText" type="primary" @click="showAddStaffDialog">
                添加第一个售后人员
              </el-button>
            </el-empty>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加售后人员对话框 -->
    <el-dialog
      v-model="addStaffDialogVisible"
      title="添加售后人员"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form :model="newStaffForm" :rules="staffFormRules" ref="staffFormRef" label-width="80px">
        <el-form-item label="昵称" prop="nick_name">
          <el-input
            v-model="newStaffForm.nick_name"
            placeholder="请输入售后人员昵称"
            :disabled="addingStaff"
          />
        </el-form-item>
        <el-form-item label="说明">
          <el-input
            v-model="newStaffForm.description"
            type="textarea"
            :rows="2"
            placeholder="可选的说明信息"
            :disabled="addingStaff"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addStaffDialogVisible = false" :disabled="addingStaff">取消</el-button>
          <el-button type="primary" @click="addStaff" :loading="addingStaff">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="批量导入售后人员"
      width="500px"
      :close-on-click-modal="false"
    >
      <div class="import-section">
        <el-alert
          title="导入说明"
          type="info"
          description="每行一个昵称，支持批量粘贴"
          show-icon
          :closable="false"
          class="import-alert"
        />
        <el-input
          v-model="importText"
          type="textarea"
          :rows="8"
          placeholder="请输入售后人员昵称，每行一个"
          :disabled="importing"
        />
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="importDialogVisible = false" :disabled="importing">取消</el-button>
          <el-button type="primary" @click="importStaff" :loading="importing">
            导入
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Excel上传对话框 -->
    <el-dialog
      v-model="excelUploadDialogVisible"
      title="Excel导入售后人员"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="excel-upload-section">
        <el-alert
          title="Excel格式要求"
          type="info"
          :closable="false"
          class="upload-alert"
        >
          <template #default>
            <ul class="format-requirements">
              <li>Excel文件必须包含 <strong>nick_name</strong> 列</li>
              <li>nick_name列包含售后人员的昵称数据</li>
              <li>支持 .xlsx 和 .xls 格式</li>
              <li>空值和重复值会自动过滤</li>
            </ul>
          </template>
        </el-alert>
        
        <div class="upload-area">
          <el-upload
            ref="uploadRef"
            class="upload-demo"
            drag
            :auto-upload="false"
            :show-file-list="true"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :before-upload="() => false"
            accept=".xlsx,.xls"
          >
            <el-icon class="el-icon--upload"><Upload /></el-icon>
            <div class="el-upload__text">
              将Excel文件拖拽到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                只能上传Excel文件，且不超过10MB
              </div>
            </template>
          </el-upload>
        </div>

        <!-- 预览信息 -->
        <div v-if="uploadPreview" class="preview-section">
          <el-divider content-position="left">预览信息</el-divider>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="文件名">{{ uploadPreview.filename }}</el-descriptions-item>
            <el-descriptions-item label="文件大小">{{ formatFileSize(uploadPreview.size) }}</el-descriptions-item>
            <el-descriptions-item label="预计导入">{{ uploadPreview.expectedCount }} 个售后人员</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="uploadPreview.valid ? 'success' : 'danger'">
                {{ uploadPreview.valid ? '格式正确' : '格式错误' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
          
          <div v-if="!uploadPreview.valid" class="error-info">
            <el-alert
              title="格式错误"
              type="error"
              :description="uploadPreview.error"
              show-icon
              :closable="false"
            />
          </div>
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cancelExcelUpload" :disabled="uploadingExcel">取消</el-button>
          <el-button 
            type="primary" 
            @click="confirmExcelUpload" 
            :loading="uploadingExcel"
            :disabled="!uploadFile || !uploadPreview?.valid"
          >
            确认导入
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Check,
  Plus,
  Refresh,
  Search,
  User,
  Delete,
  Upload
} from '@element-plus/icons-vue'
import { configAPI, type FilterRule, type StaffMember } from '@/api'

// 响应式数据
const loadingRules = ref(false)
const loadingStaff = ref(false)
const savingRules = ref(false)
const addingStaff = ref(false)
const removingStaff = ref(false)
const importing = ref(false)
const uploadingExcel = ref(false)

const filterRules = ref<FilterRule[]>([])
const staffList = ref<StaffMember[]>([])
const staffSearchText = ref('')
const rulesChanged = ref(false)

// 早晨消息过滤时间设置
const earlyMorningStart = ref(new Date(2023, 0, 1, 0, 0))
const earlyMorningEnd = ref(new Date(2023, 0, 1, 8, 0))

// 对话框状态
const addStaffDialogVisible = ref(false)
const importDialogVisible = ref(false)
const excelUploadDialogVisible = ref(false)

// 表单数据
const newStaffForm = ref({
  nick_name: '',
  description: ''
})

const importText = ref('')

// Excel上传相关
const uploadFile = ref<File | null>(null)
const uploadPreview = ref<{
  filename: string
  size: number
  valid: boolean
  expectedCount: number
  error?: string
} | null>(null)

// 表单引用
const staffFormRef = ref()
const uploadRef = ref()

// 表单验证规则
const staffFormRules = {
  nick_name: [
    { required: true, message: '请输入售后人员昵称', trigger: 'blur' },
    { min: 2, max: 50, message: '昵称长度在 2 到 50 个字符', trigger: 'blur' }
  ]
}

// 过滤后的人员列表
const filteredStaffList = computed(() => {
  if (!staffSearchText.value) return staffList.value
  
  return staffList.value.filter(staff =>
    staff.nick_name.toLowerCase().includes(staffSearchText.value.toLowerCase())
  )
})

// 加载过滤规则
const loadFilterRules = async () => {
  try {
    loadingRules.value = true
    const response = await configAPI.getFilterRules()
    filterRules.value = response.data.rules
    rulesChanged.value = false
  } catch (error) {
    console.error('Failed to load filter rules:', error)
  } finally {
    loadingRules.value = false
  }
}

// 加载售后人员列表
const loadStaffList = async () => {
  try {
    loadingStaff.value = true
    const response = await configAPI.getStaffList()
    staffList.value = response.data.staff_members
  } catch (error) {
    console.error('Failed to load staff list:', error)
  } finally {
    loadingStaff.value = false
  }
}

// 规则变更处理
const onRuleChange = () => {
  rulesChanged.value = true
}

// 保存过滤规则
const saveFilterRules = async () => {
  try {
    savingRules.value = true
    
    const rulesUpdate: Record<string, Record<string, any>> = {}
    
    filterRules.value.forEach(rule => {
      rulesUpdate[rule.rule_id] = {
        enabled: rule.enabled
      }
      
      // 添加早晨消息过滤的时间参数
      if (rule.rule_id === 'early_morning_filter') {
        rulesUpdate[rule.rule_id].parameters = {
          start_hour: earlyMorningStart.value.getHours(),
          end_hour: earlyMorningEnd.value.getHours()
        }
      }
    })
    
    await configAPI.updateFilterRules(rulesUpdate)
    ElMessage.success('过滤规则保存成功')
    rulesChanged.value = false
  } catch (error) {
    console.error('Failed to save filter rules:', error)
  } finally {
    savingRules.value = false
  }
}

// 刷新售后人员列表
const refreshStaffList = () => {
  loadStaffList()
}

// 显示添加人员对话框
const showAddStaffDialog = () => {
  newStaffForm.value = {
    nick_name: '',
    description: ''
  }
  addStaffDialogVisible.value = true
}

// 添加售后人员
const addStaff = async () => {
  try {
    await staffFormRef.value?.validate()
    
    addingStaff.value = true
    await configAPI.addStaffMember(newStaffForm.value.nick_name)
    
    ElMessage.success('添加售后人员成功')
    addStaffDialogVisible.value = false
    await loadStaffList()
  } catch (error) {
    if (error !== false) { // 不是表单验证错误
      console.error('Failed to add staff member:', error)
    }
  } finally {
    addingStaff.value = false
  }
}

// 删除售后人员
const removeStaff = async (staff: StaffMember) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除售后人员 "${staff.nick_name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    removingStaff.value = true
    await configAPI.removeStaffMember(staff.nick_name)
    
    ElMessage.success('删除售后人员成功')
    await loadStaffList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to remove staff member:', error)
    }
  } finally {
    removingStaff.value = false
  }
}

// 批量导入售后人员
const importStaff = async () => {
  if (!importText.value.trim()) {
    ElMessage.warning('请输入要导入的售后人员昵称')
    return
  }
  
  try {
    importing.value = true
    
    // 解析导入文本
    const names = importText.value
      .split('\n')
      .map(name => name.trim())
      .filter(name => name.length > 0)
    
    if (names.length === 0) {
      ElMessage.warning('没有有效的昵称可导入')
      return
    }
    
    // 获取当前人员列表
    const currentNames = staffList.value.map(staff => staff.nick_name)
    const allNames = [...new Set([...currentNames, ...names])]
    
    await configAPI.updateStaffList(allNames)
    
    ElMessage.success(`成功导入 ${names.length} 个售后人员`)
    importDialogVisible.value = false
    importText.value = ''
    await loadStaffList()
  } catch (error) {
    console.error('Failed to import staff:', error)
  } finally {
    importing.value = false
  }
}

// Excel上传相关方法
const showExcelUploadDialog = () => {
  excelUploadDialogVisible.value = true
  uploadFile.value = null
  uploadPreview.value = null
}

const handleFileChange = async (_fileItem: any, uploadFiles: any[]) => {
  if (uploadFiles.length > 0) {
    const file = uploadFiles[0].raw
    uploadFile.value = file
    
    // 初始预览信息
    uploadPreview.value = {
      filename: file.name,
      size: file.size,
      valid: false,
      expectedCount: 0,
      error: '正在验证文件格式...'
    }
    
    console.log('开始验证Excel文件:', file.name, 'Size:', file.size)
    
    // 预验证文件内容
    try {
      const response = await configAPI.validateStaffExcel(file)
      console.log('售后人员Excel文件验证响应:', response)
      
      if (response.success) {
        uploadPreview.value = {
          filename: file.name,
          size: file.size,
          valid: true,
          expectedCount: response.data.expected_count || 0
        }
        console.log('文件验证通过，预计导入:', response.data.expected_count, '个售后人员')
        console.log('预览人员名单:', response.data.preview_names)
      } else {
        uploadPreview.value = {
          filename: file.name,
          size: file.size,
          valid: false,
          expectedCount: 0,
          error: response.message || '文件格式验证失败'
        }
        console.log('文件验证失败:', response.message)
      }
    } catch (error: any) {
      console.error('文件验证出错:', error)
      uploadPreview.value = {
        filename: file.name,
        size: file.size,
        valid: false,
        expectedCount: 0,
        error: error.response?.data?.detail || '文件格式验证失败'
      }
    }
  }
}

const handleFileRemove = () => {
  uploadFile.value = null
  uploadPreview.value = null
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const cancelExcelUpload = () => {
  excelUploadDialogVisible.value = false
  uploadFile.value = null
  uploadPreview.value = null
  uploadRef.value?.clearFiles()
}

const confirmExcelUpload = async () => {
  if (!uploadFile.value) {
    ElMessage.warning('请选择要上传的Excel文件')
    return
  }
  
  try {
    uploadingExcel.value = true
    
    const response = await configAPI.uploadStaffExcel(uploadFile.value)
    
    ElMessage.success(response.message)
    excelUploadDialogVisible.value = false
    
    // 重新加载人员列表
    await loadStaffList()
    
    // 清理上传状态
    uploadFile.value = null
    uploadPreview.value = null
    uploadRef.value?.clearFiles()
    
  } catch (error: any) {
    console.error('Excel upload failed:', error)
    
    // 显示详细错误信息
    if (error.response?.data?.detail) {
      ElMessage({
        message: error.response.data.detail,
        type: 'error',
        duration: 10000,
        showClose: true
      })
    } else {
      ElMessage.error('Excel导入失败，请检查文件格式')
    }
  } finally {
    uploadingExcel.value = false
  }
}

// 组件挂载
onMounted(() => {
  loadFilterRules()
  loadStaffList()
})
</script>

<style scoped>
.config-container {
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

.config-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  height: 600px;
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

.rules-list {
  max-height: 480px;
  overflow-y: auto;
}

.rule-item {
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 12px;
  background-color: #fafafa;
}

.rule-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.rule-info {
  flex: 1;
}

.rule-name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.rule-description {
  font-size: 12px;
  color: #606266;
}

.rule-params {
  margin-top: 16px;
}

.param-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.param-row label {
  min-width: 80px;
  color: #606266;
  font-size: 14px;
}

.rules-alert {
  margin-top: 16px;
}

.staff-section {
  height: 480px;
  display: flex;
  flex-direction: column;
}

.staff-search {
  margin-bottom: 16px;
}

.staff-list {
  flex: 1;
  overflow-y: auto;
}

.staff-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 8px;
  background-color: #fafafa;
  transition: all 0.3s;
}

.staff-item:hover {
  background-color: #f0f9ff;
  border-color: #409eff;
}

.staff-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.staff-details {
  flex: 1;
}

.staff-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.staff-status {
  font-size: 12px;
}

.import-section {
  margin-bottom: 16px;
}

.import-alert {
  margin-bottom: 16px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* Excel上传对话框样式 */
.excel-upload-section {
  margin-bottom: 16px;
}

.upload-alert {
  margin-bottom: 20px;
}

.format-requirements {
  margin: 0;
  padding-left: 20px;
}

.format-requirements li {
  margin-bottom: 4px;
  color: #606266;
}

.upload-area {
  margin-bottom: 20px;
}

.preview-section {
  margin-top: 20px;
}

.error-info {
  margin-top: 16px;
}
</style>
