<template>
  <div class="log-container">
    <div class="header">
      <div class="title">
        <el-icon><Document /></el-icon>
        <span>实时识别日志</span>
      </div>

      <div class="actions">
        <!-- 日志类型 改回白色 默认样式 -->
        <el-select
          v-model="logType"
          style="width: 120px"
          @change="handleTypeChange"
        >
          <el-option label="运行日志" value="app" />
          <el-option label="错误日志" value="error" />
          <el-option label="告警日志" value="alert" />
        </el-select>

        <!-- 搜索框 -->
        <el-input
          v-model="search"
          placeholder="检索日志内容..."
          clearable
          style="flex:1;max-width:320px"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>

        <!-- 自动刷新按钮 -->
        <el-button class="auto-refresh-btn" round @click="autoRefresh = !autoRefresh">
          {{ autoRefresh ? '自动刷新' : '手动刷新' }}
        </el-button>

        <!-- 刷新日志 -->
        <el-button type="primary" round @click="fetchLogs">刷新日志</el-button>
        
        <!-- 导出日志 -->
        <el-button type="success" round @click="exportLogs">导出日志</el-button>
      </div>
    </div>

    <div class="summary">
      <span>日志类型：{{ typeText }}</span>
      <span>总行数：{{ totalLines }}</span>
      <span>当前展示：{{ displayLogs.length }}</span>
      <span v-if="loading">加载中...</span>
      <span v-if="errorMsg" class="error-msg">{{ errorMsg }}</span>
    </div>

    <el-table :data="displayLogs" height="calc(100% - 100px)" stripe>
      <el-table-column prop="index" label="#" width="70" />
      <el-table-column prop="time" label="时间" width="180" />
      <el-table-column prop="level" label="级别" width="110">
        <template #default="scope">
          <el-tag :type="getLevelTagType(scope.row.level)" effect="dark">
            {{ scope.row.level || '-' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="source" label="来源" width="180" show-overflow-tooltip />
      <el-table-column prop="message" label="日志内容" min-width="520" show-overflow-tooltip />
    </el-table>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { Document, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getLogs } from '@/api'

const search = ref('')
const logType = ref('app')
const lineCount = ref(50)
const autoRefresh = ref(true)
const loading = ref(false)
const errorMsg = ref('')
const totalLines = ref(0)
const tableRows = ref([])

let timer = null

const typeText = computed(() => {
  if (logType.value === 'app') return '运行日志'
  if (logType.value === 'error') return '错误日志'
  if (logType.value === 'alert') return '告警日志'
  return '-'
})

const tableData = computed(() => tableRows.value)

const displayLogs = computed(() => {
  if (!search.value) return tableData.value
  const keyword = search.value.toLowerCase()
  return tableData.value.filter(item =>
    String(item.raw || '').toLowerCase().includes(keyword) ||
    String(item.message || '').toLowerCase().includes(keyword) ||
    String(item.source || '').toLowerCase().includes(keyword) ||
    String(item.level || '').toLowerCase().includes(keyword)
  )
})

const fetchLogs = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await getLogs(logType.value, lineCount.value)
    tableRows.value = Array.isArray(res.data?.items) ? res.data.items : []
    totalLines.value = Number(res.data?.total_lines || 0)
  } catch (error) {
    console.error(error)
    errorMsg.value = '获取日志失败'
    ElMessage.error('获取日志失败')
  } finally {
    loading.value = false
  }
}

const startPolling = () => {
  stopPolling()
  fetchLogs()
  timer = setInterval(() => { fetchLogs() }, 3000)
}

const stopPolling = () => {
  if (timer) { clearInterval(timer); timer = null }
}

const handleTypeChange = () => {
  autoRefresh.value ? startPolling() : fetchLogs()
}

const getLevelTagType = (level) => {
  const map = {
    INFO: 'info',
    DEBUG: '',
    WARNING: 'warning',
    ERROR: 'danger',
    CRITICAL: 'danger'
  }
  return map[level] ?? 'info'
}

const exportLogs = () => {
  try {
    const header = '序号,时间,级别,来源,日志内容\n'
    const content = displayLogs.value
      .map(item => [
        item.index,
        `"${item.time || '-'}"`,
        `"${item.level || '-'}"`,
        `"${item.source || '-'}"`,
        `"${String(item.message || '-').replace(/"/g, '""')}"`
      ].join(','))
      .join('\n')
    const blob = new Blob([header + content], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${logType.value}_logs.csv`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error(error)
    ElMessage.error('导出失败')
  }
}

onMounted(() => {
  autoRefresh.value ? startPolling() : fetchLogs()
})

onBeforeUnmount(() => {
  stopPolling()
})
</script>

<style scoped>
.log-container {
  --text-main: #e8ecf3;
  --text-sub: rgba(255,255,255,0.65);
  --text-muted: rgba(255,255,255,0.4);
  --border-color: rgba(255,255,255,0.08);
  --card-bg: rgba(20,25,35,0.75);
  height: 100%;
  padding: 20px;
  box-sizing: border-box;
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid var(--border-color);
}

.header {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-bottom: 12px;
  gap: 10px;
  flex-wrap: wrap;
}
.title { display: none; }

.actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
  width: 100%;
}

/* 输入框通用样式 */
:deep(.el-input__wrapper) {
  height: 40px !important;
  border-radius: 14px !important;
  background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.03)) !important;
  border: 1px solid var(--border-color) !important;
  box-shadow: none !important;
  transition: all 0.2s ease;
}
:deep(.el-input__inner),
:deep(.el-select .el-input__inner) {
  color: var(--text-main) !important;
  font-size: 13px !important;
}

/* 按钮统一大小 */
.actions :deep(.el-button) {
  height: 40px !important;
  border-radius: 14px !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  padding: 0 16px !important;
  transition: all 0.2s ease !important;
  border: 1px solid var(--border-color) !important;
  white-space: nowrap;
}

/* 自动刷新按钮：深色区分 */
.auto-refresh-btn {
  background: linear-gradient(145deg, #2d3447, #1f2436) !important;
  border-color: rgba(255,255,255,0.15) !important;
  color: #e8ecf3 !important;
}
.auto-refresh-btn:hover {
  background: linear-gradient(145deg, #3b4256, #2a3045) !important;
  border-color: rgba(255,255,255,0.25) !important;
}

/* 刷新日志：原有高级样式 */
.actions :deep(.el-button--primary) {
  background: radial-gradient(circle at 85% 20%, rgba(120,170,255,0.15), transparent 25%),
  linear-gradient(145deg, rgba(23,58,112,0.95), rgba(12,36,72,0.98)) !important;
  border-color: rgba(78,132,214,0.3) !important;
}
.actions :deep(.el-button--primary:hover) {
  background: radial-gradient(circle at 85% 20%, rgba(140,170,255,0.2), transparent 28%),
  linear-gradient(145deg, rgba(33,68,122,1), rgba(22,46,92,1)) !important;
  border-color: rgba(78,132,214,0.4) !important;
}

/* 导出日志：原有高级样式 */
.actions :deep(.el-button--success) {
  background: linear-gradient(145deg, #1a6d48, #0f4a30) !important;
  border-color: rgba(66,190,122,0.3) !important;
}
.actions :deep(.el-button--success:hover) {
  background: linear-gradient(145deg, #238a5d, #175c3d) !important;
}

/* 统计信息 */
.summary {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 12px;
  color: var(--text-sub);
  font-size: 12px;
}
.error-msg { color: #ff7a9c; }

/* 表格样式 */
:deep(.el-table) {
  background: transparent !important;
  border-radius: 14px !important;
  overflow: hidden;
  border: 1px solid var(--border-color) !important;
}
:deep(.el-table__header-wrapper),
:deep(.el-table__header) {
  background: #1a2235 !important;
  border-bottom: 1px solid var(--border-color) !important;
}
:deep(.el-table th) {
  background: #1a2235 !important;
  color: var(--text-sub) !important;
  font-weight: 600 !important;
  padding: 10px 0 !important;
  font-size: 12px !important;
}
:deep(.el-table td) {
  background: transparent !important;
  color: var(--text-main) !important;
  padding: 8px 0 !important;
  font-size: 13px !important;
}
:deep(.el-table tbody tr) {
  background: rgba(20,25,35,0.4) !important;
}
:deep(.el-table tbody tr:hover) {
  background: rgba(49,104,186,0.12) !important;
}
:deep(.el-table tbody tr td:first-child) {
  position: relative;
}
:deep(.el-table tbody tr:hover td:first-child::before) {
  content: "";
  position: absolute;
  left: 0;
  top: 10%;
  bottom: 10%;
  width: 3px;
  border-radius: 3px;
  background: linear-gradient(180deg, #6b9dff, #8c99ff);
  pointer-events: none;
}
:deep(.el-tag) {
  border-radius: 12px !important;
  font-weight: 500 !important;
  padding: 0 8px !important;
  font-size: 12px !important;
}
</style>