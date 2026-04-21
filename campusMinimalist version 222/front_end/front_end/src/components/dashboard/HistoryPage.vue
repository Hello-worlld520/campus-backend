<template>
  <div class="history-page">
    <div class="page-header">
      <h2>回放记录</h2>
      <p>异常行为切片缓存与本地历史回放</p>
    </div>

    <div class="history-grid">
      <div
        class="history-card"
        v-for="item in historyList"
        :key="item.id"
      >
        <div class="history-thumb">
          <el-icon class="play-icon"><VideoPlay /></el-icon>
        </div>
        <div class="history-info">
          <div class="title">{{ item.title }}</div>
          <div class="meta">
            {{ item.camera }} · {{ item.time }}
          </div>
          <div class="row">
            <el-tag :type="item.type === '打架' ? 'danger' : 'warning'" size="small" round>
              {{ item.type }}
            </el-tag>
            <span class="conf">{{ item.conf }}%</span>
          </div>
        </div>
        <div class="history-actions">
          <el-button type="primary" size="small" @click="playSlice(item)">
            <el-icon><VideoPlay /></el-icon>回放
          </el-button>
          <el-button size="small" @click="exportSlice(item)">
            <el-icon><Download /></el-icon>导出
          </el-button>
        </div>
      </div>
    </div>

    <div v-if="historyList.length === 0" class="empty-hint">
      <el-icon><Clock /></el-icon>
      <p>暂无历史记录，产生异常行为后会自动缓存</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoPlay, Download, Clock } from '@element-plus/icons-vue'

const historyList = ref([])

// 从本地缓存读取历史切片
const loadHistory = () => {
  const data = localStorage.getItem('behavior_history')
  if (data) historyList.value = JSON.parse(data)
  else {
    // 演示数据
    historyList.value = [
      {
        id: 101,
        title: '异常行为片段 #001',
        camera: '东门出口',
        time: '10:05:22',
        type: '打架',
        conf: 98
      },
      {
        id: 102,
        title: '异常行为片段 #002',
        camera: '西区围栏',
        time: '10:12:45',
        type: '翻墙',
        conf: 92
      }
    ]
  }
}

const playSlice = (item) => {
  ElMessage.success(`正在回放：${item.title}`)
}

const exportSlice = (item) => {
  ElMessage.success(`已导出视频切片：${item.title}`)
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.history-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.page-header h2 {
  font-size: 28px;
  color: #f0f1f5;
  margin: 0 0 6px;
}
.page-header p {
  font-size: 15px;
  color: #c5c8d0;
}

.history-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}
.history-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  border-radius: 16px;

  background: rgba(255,255,255,0.06);
  backdrop-filter: blur(14px) saturate(140%);
  -webkit-backdrop-filter: blur(14px) saturate(140%);

  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: 0 6px 24px rgba(0,0,0,0.25);

  transition: all 0.3s ease;
}
.history-card:hover {
  transform: translateY(-4px) scale(1.01);
  background: rgba(255,255,255,0.1);
  box-shadow: 0 12px 40px rgba(0,0,0,0.35);
}
.history-thumb {
  width: 70px;
  height: 50px;
  background: #1e222a;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.play-icon {
  color: #0071e3;
  font-size: 20px;
}
.history-info {
  flex: 1;
  min-width: 0;
}
.history-info .title {
  font-size: 15px;
  font-weight: 600;
  color: #f0f1f5;
  margin-bottom: 4px;
}
.history-info .meta {
  font-size: 12px;
  color: #8a8e9a;
  margin-bottom: 6px;
}
.row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.conf {
  font-size: 12px;
  color: #c5c8d0;
  font-weight: 600;
}
.history-actions {
  display: flex;
  gap: 6px;
}

.empty-hint {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #8a8e9a;
}
.empty-hint i {
  font-size: 40px;
  margin-bottom: 12px;
}
</style>