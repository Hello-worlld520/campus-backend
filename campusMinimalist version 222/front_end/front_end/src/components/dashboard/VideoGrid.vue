<template>
  <section class="player-page">
    <div class="page-header">
      <div class="title-block">
        <div class="title-row">
          <el-icon class="title-icon"><VideoCameraFilled /></el-icon>
          <h2>实时检测</h2>
        </div>
        <p class="subtitle">
          当前视频源：{{ sourceLabel }}
        </p>
      </div>

      <div class="toolbar">
        <!-- 只保留：摄像头 -->
        <button class="toolbar-btn" @click="useCamera('0')">
          <span>摄像头</span>
        </button>

        <input
            v-model="rtspInput"
            class="rtsp-input"
            placeholder="输入 RTSP 地址，例如 rtsp://..."
        />

        <button class="toolbar-btn" @click="useRtsp">
          <span>连接 RTSP</span>
        </button>

        <label class="file-pill">
          <span>导入视频</span>
          <input type="file" accept="video/*" @change="handleVideoUpload" />
        </label>

        <button
            class="toolbar-btn danger"
            @click="handleStopCurrent"
            :disabled="!currentSourceId && !taskId"
        >
          <span>停止当前</span>
        </button>

        <button class="toolbar-btn danger" @click="handleStopAll">
          <span>停止全部</span>
        </button>
      </div>
    </div>

    <div class="player-card tesla-glass">
      <div class="player-stage">
        <div class="stage-inner">
          <!-- 实时摄像头 / RTSP -->
          <img
              v-if="displayMode === 'realtime' && streamUrl"
              :src="streamUrl"
              class="video-element"
              alt="识别后视频流"
              @load="handleStreamLoad"
              @error="handleStreamError"
          />

          <!-- 上传任务处理结果 -->
          <video
              v-else-if="displayMode === 'task_result' && resultVideoUrl"
              ref="resultVideoRef"
              :key="resultVideoUrl"
              class="video-element"
              controls
              preload="metadata"
              @loadedmetadata="handleResultVideoLoaded"
              @error="handleResultVideoError"
          >
            <source :src="resultVideoUrl" type="video/mp4" />
          </video>
          <!-- 空状态 -->
          <label v-else class="upload-overlay">
            <div class="upload-box">
              <el-icon class="empty-icon"><Film /></el-icon>
              <h3>请选择视频源</h3>
              <p>支持 摄像头 / RTSP / 上传本地视频</p>
            </div>
            <input type="file" accept="video/*" @change="handleVideoUpload" />
          </label>
        </div>
      </div>

      <div
          v-if="currentFileName && (uploadPercent < 100 || (taskId && taskStatus !== 'completed' && taskStatus !== 'failed' && taskStatus !== 'stopped'))"
          class="progress-wrap tesla-glass-progress"
      >
        <div class="progress-header">
          <span class="progress-label">视频上传中</span>
          <span class="progress-percent">
            {{ uploadPercent < 100 ? `${uploadPercent}%` : `${taskProgress}%` }}
          </span>
        </div>

        <div class="progress-bar">
          <div
              class="progress-inner"
              :style="{ width: `${uploadPercent < 100 ? uploadPercent : taskProgress}%` }"
          >
            <span class="progress-glow"></span>
          </div>
        </div>

        <div class="progress-meta">
          <span>{{ uploadPercent < 100 ? '长视频上传可能需要较长时间' : '视频识别处理中，请耐心等待' }}</span>
          <span>请勿关闭页面</span>
        </div>
      </div>

      <div class="info-strip">
        <div class="info-card">
          <span class="info-label">当前文件</span>
          <strong class="info-value">{{ currentFileName || '未导入' }}</strong>
        </div>

        <div class="info-card">
          <span class="info-label">当前来源ID</span>
          <strong class="info-value">{{ currentSourceId || '无' }}</strong>
        </div>

        <div class="info-card">
          <span class="info-label">任务ID</span>
          <strong class="info-value">{{ taskId || '无' }}</strong>
        </div>

        <div class="info-card">
          <span class="info-label">任务状态</span>
          <strong class="info-value">{{ taskStatus || '未开始' }}</strong>
        </div>

        <div class="info-card">
          <span class="info-label">状态提示</span>
          <strong class="info-value status-text">{{ statusText }}</strong>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoCameraFilled, Film } from '@element-plus/icons-vue'
import {
  uploadVideo,
  stopStream,
  stopAllStreams,
  stopTask,
  getTaskStatus,
  getVideoFeedUrl,
  getResultVideoUrl
} from '@/api'

const streamUrl = ref('')
const resultVideoUrl = ref('')
const currentSourceId = ref('')
const currentFileName = ref('')
const rtspInput = ref('')
const statusText = ref('等待选择视频源')
const uploadPercent = ref(0)
const resultVideoRef = ref(null)
const taskId = ref('')
const taskStatus = ref('')
const taskProgress = ref(0)
let pollTimer = null

// realtime | task_result
const displayMode = ref('realtime')

const sourceLabel = computed(() => {
  if (taskId.value) {
    return currentFileName.value ? `上传任务：${currentFileName.value}` : '上传任务'
  }

  if (!currentSourceId.value) return '未选择'
  if (currentSourceId.value === 'stream_0') return '摄像头'
  if (currentSourceId.value.startsWith('stream_rtsp://')) return 'RTSP 视频流'
  return currentSourceId.value
})

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

function resetTaskState() {
  stopPolling()
  taskId.value = ''
  taskStatus.value = ''
  taskProgress.value = 0
  resultVideoUrl.value = ''
}

function clearRealtimeStream() {
  streamUrl.value = ''
  currentSourceId.value = ''
}

function clearAllDisplay() {
  clearRealtimeStream()
  resetTaskState()
}

function useCamera(source) {
  resetTaskState()
  currentFileName.value = ''
  currentSourceId.value = `stream_${source}`
  streamUrl.value = `${getVideoFeedUrl(source)}&_t=${Date.now()}`
  displayMode.value = 'realtime'
  statusText.value = '正在连接识别流...'
}

function useRtsp() {
  const value = rtspInput.value.trim()
  if (!value) {
    ElMessage.warning('请输入 RTSP 地址')
    return
  }

  resetTaskState()
  currentFileName.value = ''
  currentSourceId.value = `stream_${value}`
  streamUrl.value = `${getVideoFeedUrl(value)}&_t=${Date.now()}`
  displayMode.value = 'realtime'
  statusText.value = '正在连接 RTSP 识别流...'
}

function startPollingTask(id) {
  stopPolling()

  pollTimer = setInterval(async () => {
    try {
      const res = await getTaskStatus(id)
      const data = res.data

      taskStatus.value = data.status
      taskProgress.value = data.progress ?? 0

      if (data.status === 'queued') {
        statusText.value = `任务排队中... ${taskProgress.value}%`
      } else if (data.status === 'processing') {
        statusText.value = `视频识别处理中... ${taskProgress.value}%`
      } else if (data.status === 'transcoding') {
        statusText.value = `结果视频转码中... ${taskProgress.value}%`
      } else if (data.status === 'completed') {
        statusText.value = '识别完成，可播放结果视频'

        const url = data.result_url
            ? `/api${data.result_url}&_t=${Date.now()}`
            : `${getResultVideoUrl(id)}&_t=${Date.now()}`

        streamUrl.value = ''
        resultVideoUrl.value = url
        displayMode.value = 'task_result'
        uploadPercent.value = 100
        taskProgress.value = 100

        console.log('准备播放结果视频:', resultVideoUrl.value)

        stopPolling()

        await nextTick()

        if (resultVideoRef.value) {
          resultVideoRef.value.load()
          console.log('已手动调用 video.load()')
        } else {
          console.warn('resultVideoRef 为空，video 元素未挂载')
        }

        ElMessage.success('视频识别完成')
      } else if (data.status === 'failed') {
        statusText.value = `识别失败：${data.error || '未知错误'}`
        stopPolling()
        ElMessage.error('视频识别失败')
      } else if (data.status === 'stopped') {
        statusText.value = '任务已停止'
        stopPolling()
        ElMessage.warning('视频任务已停止')
      }
    } catch (error) {
      console.error(error)
      statusText.value = '获取任务状态失败'
      stopPolling()
    }
  }, 2000)
}

async function handleVideoUpload(e) {
  const file = e.target.files?.[0]
  if (!file) return

  clearAllDisplay()
  currentFileName.value = file.name
  uploadPercent.value = 0
  displayMode.value = 'task_result'
  statusText.value = '正在上传视频...'

  try {
    const res = await uploadVideo(file, (percent) => {
      uploadPercent.value = percent
      statusText.value = `正在上传视频... ${percent}%`
    })

    const data = res.data
    taskId.value = data.task_id
    currentSourceId.value = data.source_id
    taskStatus.value = data.status || 'queued'
    taskProgress.value = 0

    statusText.value = '上传成功，后端正在创建识别任务...'
    ElMessage.success('视频上传成功，开始后台识别')

    startPollingTask(taskId.value)
  } catch (error) {
    console.error(error)
    uploadPercent.value = 0
    statusText.value = '视频上传失败'
    ElMessage.error('视频上传失败')
  } finally {
    e.target.value = ''
  }
}

async function handleStopCurrent() {
  try {
    // 优先停止任务
    if (taskId.value) {
      await stopTask(taskId.value)
      statusText.value = '已请求停止当前视频任务'
      resetTaskState()
      currentSourceId.value = ''
      ElMessage.success('已停止当前视频任务')
      return
    }

    // 否则停止实时流
    if (currentSourceId.value) {
      await stopStream(currentSourceId.value)
      clearRealtimeStream()
      statusText.value = '已停止当前识别流'
      ElMessage.success('已停止当前视频流')
      return
    }

    ElMessage.warning('当前没有可停止的任务或视频流')
  } catch (error) {
    console.error(error)
    statusText.value = '停止失败'
    ElMessage.error('停止失败')
  }
}

async function handleStopAll() {
  try {
    await stopAllStreams()

    if (taskId.value) {
      try {
        await stopTask(taskId.value)
      } catch (e) {
        console.warn('停止任务失败:', e)
      }
    }

    clearAllDisplay()
    currentFileName.value = ''
    statusText.value = '已停止全部识别'
    ElMessage.success('已停止全部视频流/任务')
  } catch (error) {
    console.error(error)
    statusText.value = '停止全部失败'
    ElMessage.error('停止失败')
  }
}

function handleStreamLoad() {
  if (displayMode.value === 'realtime') {
    statusText.value = '实时识别流加载成功'
  }
}

function handleStreamError() {
  if (displayMode.value === 'realtime') {
    statusText.value = '识别流加载失败，请检查后端或视频源'
  }
}

function handleResultVideoLoaded() {
  statusText.value = '结果视频加载成功'
  console.log('结果视频加载成功:', resultVideoUrl.value)
}

function handleResultVideoError(e) {
  console.error('结果视频加载失败:', e)
  console.log('当前结果视频地址:', resultVideoUrl.value)
  statusText.value = '结果视频加载失败'
  ElMessage.error('结果视频加载失败，请检查播放地址或浏览器控制台')
}

onUnmounted(() => {
  stopPolling()
})
</script>
<style scoped>
.player-page {
  --card: rgba(20, 25, 35, 0.75);
  --border: rgba(255, 255, 255, 0.08);
  --text-main: #e8ecf3;
  --text-sub: rgba(255, 255, 255, 0.65);
  --text-muted: rgba(255, 255, 255, 0.4);

  /* 与左侧菜单完全统一的蓝紫色 */
  --nav-blue-1: #163a70;
  --nav-blue-2: #42628e;
  --nav-blue-3: #214d8f;
  --nav-blue-glow: rgba(49, 104, 186, 0.24);
  --danger: #e54c74;

  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  flex-wrap: wrap;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-row h2 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-main);
  margin: 0;
}

.title-icon {
  font-size: 20px;
  color: var(--nav-blue-2);
}

.subtitle {
  font-size: 13px;
  color: var(--text-sub);
  margin: 4px 0 0;
}

/* ===================== 工具栏按钮（统一左侧菜单风格） ===================== */
.toolbar {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.rtsp-input {
  height: 46px;
  min-width: 260px;
  padding: 0 16px;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(180deg, rgba(255,255,255,0.055), rgba(255,255,255,0.03));
  color: var(--text-main);
  font-size: 14px;
  outline: none;
  transition: all 0.24s ease;
}
.rtsp-input:focus {
  border-color: rgba(78, 132, 214, 0.28);
  background: linear-gradient(180deg, rgba(23, 58, 112, 0.22), rgba(12, 36, 72, 0.12));
}

/* 基础按钮 */
.toolbar-btn,
.file-pill {
  height: 46px;
  padding: 0 22px;
  border-radius: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.24s ease;
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(180deg, rgba(255,255,255,0.055), rgba(255,255,255,0.03));
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.03), 0 6px 16px rgba(0, 0, 0, 0.16);
  color: var(--text-main);
}
.file-pill input { display: none; }

/* 高光 */
.toolbar-btn::before,
.file-pill::before {
  content: '';
  position: absolute;
  inset: 1px;
  border-radius: inherit;
  background: linear-gradient(180deg, rgba(255,255,255,0.07), transparent 50%);
  opacity: 0.7;
  pointer-events: none;
}

/* 扫光 */
.toolbar-btn::after,
.file-pill::after {
  content: '';
  position: absolute;
  top: -30%;
  left: -16%;
  width: 36%;
  height: 180%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.14), transparent);
  transform: rotate(18deg);
  opacity: 0;
  transition: transform 0.65s ease, opacity 0.65s ease;
  pointer-events: none;
}

/* 普通hover */
.toolbar-btn:hover:not(:disabled):not(.danger) {
  transform: translateY(-2px);
  border-color: rgba(255, 255, 255, 0.14);
  background: linear-gradient(180deg, rgba(255,255,255,0.085), rgba(255,255,255,0.045));
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 12px 24px rgba(0, 0, 0, 0.22);
}

/* 🔥 导入视频按钮 hover 保持蓝色（不变成灰色） */
.file-pill:hover {
  transform: translateY(-2px);
  border-color: rgba(78, 132, 214, 0.4);
  background: radial-gradient(circle at 85% 20%, rgba(140, 170, 255, 0.2), transparent 28%),
  linear-gradient(145deg, rgba(33, 68, 122, 1), rgba(22, 46, 92, 1));
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.22);
  color: #fff;
}
.toolbar-btn:hover::after,
.file-pill:hover::after {
  transform: translateX(220%) rotate(18deg);
  opacity: 1;
}

/* 激活态 */
.toolbar-btn.active,
.file-pill {
  border-color: rgba(78, 132, 214, 0.34);
  background: radial-gradient(circle at 85% 20%, rgba(120, 170, 255, 0.16), transparent 28%),
  linear-gradient(145deg, rgba(23, 58, 112, 0.96), rgba(12, 36, 72, 0.98));
  box-shadow: 0 14px 34px rgba(0, 0, 0, 0.28),
  0 0 0 1px rgba(64, 123, 212, 0.18),
  0 0 22px rgba(49, 104, 186, 0.16);
  color: #fff;
}

/* 停止按钮 */
.toolbar-btn.danger {
  border-color: rgba(245, 76, 116, 0.28);
  background: linear-gradient(145deg, rgba(112, 23, 42, 0.96), rgba(72, 12, 24, 0.98));
  color: #fff;
}
.toolbar-btn.danger:hover {
  border-color: rgba(245, 76, 116, 0.4);
  background: linear-gradient(145deg, rgba(132, 23, 42, 0.96), rgba(92, 12, 24, 0.98));
}
.toolbar-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ===================== 玻璃卡片 ===================== */
.tesla-glass {
  padding: 20px;
  border-radius: 20px;
  background: var(--card);
  backdrop-filter: blur(20px);
  border: 1px solid var(--border);
}

/* 视频播放区域 */
.player-stage {
  height: 520px;
  border-radius: 16px;
  background: radial-gradient(circle at center, #0f1624, #000);
  overflow: hidden;
}

.stage-inner {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.video-element {
  width: 100%;
  height: 100%;
  object-fit: contain;
  z-index: 1;
  display: block;
}

.upload-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  cursor: pointer;
}

.upload-overlay input {
  display: none;
}

.upload-box {
  width: 420px;
  max-width: 90%;
  padding: 40px 30px;
  border-radius: 18px;
  background: rgba(25, 30, 45, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(20px);
  text-align: center;
  transition: all 0.35s ease;
}

.upload-overlay:hover .upload-box {
  transform: translateY(-6px) scale(1.03);
  box-shadow: 0 0 50px rgba(107, 122, 255, 0.25);
  border-color: var(--nav-blue-2);
}

.empty-icon {
  font-size: 38px;
  color: var(--nav-blue-2);
  margin-bottom: 12px;
}

.upload-box h3 {
  font-size: 18px;
  color: var(--text-main);
}

.upload-box p {
  font-size: 12px;
  color: var(--text-muted);
}

/* ===================== 🔥 下方5个信息卡片：统一左侧菜单样式 + 居中 ===================== */
.info-strip {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
  margin-top: 14px;
}

.info-card {
  padding: 14px 12px;
  border-radius: 16px;
  text-align: center;
  position: relative;
  overflow: hidden;
  transition: all 0.24s ease;

  /* 完全统一监控点位/菜单的玻璃风格 */
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(180deg, rgba(255,255,255,0.055), rgba(255,255,255,0.03));
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.03), 0 6px 16px rgba(0, 0, 0, 0.16);
}
.info-card::before {
  content: '';
  position: absolute;
  inset: 1px;
  border-radius: inherit;
  background: linear-gradient(180deg, rgba(255,255,255,0.07), transparent 50%);
  opacity: 0.7;
  pointer-events: none;
}
.info-card:hover {
  transform: translateY(-2px);
  border-color: rgba(78, 132, 214, 0.2);
  background: linear-gradient(180deg, rgba(23, 58, 112, 0.12), rgba(12, 36, 72, 0.08));
}

.info-label {
  font-size: 11px;
  color: var(--text-muted);
  display: block;
  text-align: center;
}

.info-value {
  display: block;
  margin-top: 6px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-main);
  word-break: break-all;
  text-align: center;
}

.status-text {
  color: var(--nav-blue-2);
}

@media (max-width: 900px) {
  .info-strip {
    grid-template-columns: repeat(2, 1fr);
  }

  .player-stage {
    height: 380px;
  }
}

@media (max-width: 640px) {
  .info-strip {
    grid-template-columns: 1fr;
  }

  .rtsp-input {
    min-width: 100%;
  }
}

/* ===================== 进度条样式 ===================== */
.progress-wrap {
  margin-top: 18px;
  padding: 18px 20px;
  border-radius: 18px;
  position: relative;
  overflow: hidden;
}

.tesla-glass-progress {
  background:
    linear-gradient(135deg, rgba(255,255,255,0.07), rgba(255,255,255,0.025)),
    radial-gradient(circle at top right, rgba(49, 104, 186, 0.14), transparent 45%);
  border: 1px solid rgba(255,255,255,0.08);
  backdrop-filter: blur(18px) saturate(150%);
  box-shadow:
    0 10px 30px rgba(0,0,0,0.35),
    inset 0 1px 0 rgba(255,255,255,0.06);
}

.tesla-glass-progress::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    115deg,
    transparent 15%,
    rgba(255,255,255,0.06) 35%,
    transparent 55%
  );
  transform: translateX(-120%);
  animation: progressSweep 3.8s linear infinite;
  pointer-events: none;
}

@keyframes progressSweep {
  0% { transform: translateX(-120%); }
  100% { transform: translateX(120%); }
}

.progress-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.progress-label {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255,255,255,0.88);
}

.progress-percent {
  font-size: 15px;
  font-weight: 700;
  color: #dfe9ff;
  text-shadow: 0 0 12px rgba(49, 104, 186, 0.35);
}

.progress-bar {
  width: 100%;
  height: 14px;
  border-radius: 999px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
  border: 1px solid rgba(255,255,255,0.06);
  box-shadow: inset 0 2px 10px rgba(0,0,0,0.45);
}

.progress-bar::before {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    90deg,
    rgba(255,255,255,0.015) 0px,
    rgba(255,255,255,0.015) 10px,
    transparent 10px,
    transparent 20px
  );
  opacity: 0.55;
  pointer-events: none;
}

.progress-inner {
  height: 100%;
  border-radius: 999px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(
    90deg,
    #d7e5ff 0%,
    #9fc3ff 18%,
    #649eff 42%,
    #3a7aff 65%,
    #68b8ff 82%,
    #eef5ff 100%
  );
  box-shadow:
    0 0 18px rgba(49, 104, 186, 0.45),
    0 0 40px rgba(49, 104, 186, 0.22),
    inset 0 1px 0 rgba(255,255,255,0.35);
  transition: width 0.35s cubic-bezier(0.22, 1, 0.36, 1);
}

.progress-inner::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    120deg,
    rgba(255,255,255,0) 10%,
    rgba(255,255,255,0.28) 28%,
    rgba(255,255,255,0.55) 40%,
    rgba(255,255,255,0.12) 52%,
    rgba(255,255,255,0) 70%
  );
  transform: translateX(-120%);
  animation: innerLightMove 1.8s linear infinite;
}

@keyframes innerLightMove {
  0% { transform: translateX(-120%); }
  100% { transform: translateX(120%); }
}

.progress-glow {
  position: absolute;
  top: 50%;
  right: -8px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  transform: translateY(-50%);
  background: radial-gradient(circle, rgba(255,255,255,0.95) 0%, rgba(173,212,255,0.55) 40%, rgba(49, 104, 186, 0) 75%);
  filter: blur(2px);
  opacity: 0.95;
  animation: glowPulse 1.6s ease-in-out infinite;
}

@keyframes glowPulse {
  0%, 100% { transform: translateY(-50%) scale(0.9); opacity: 0.75; }
  50% { transform: translateY(-50%) scale(1.12); opacity: 1; }
}

.progress-meta {
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-size: 11px;
  color: rgba(255,255,255,0.48);
}

@media (max-width: 640px) {
  .progress-wrap { padding: 16px; }
  .progress-meta { flex-direction: column; gap: 4px; }
  .progress-bar { height: 12px; }
}
</style>