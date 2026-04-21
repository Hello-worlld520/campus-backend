<template>
  <div class="dashboard-wrapper">
    <!-- 背景动态光影层 -->
    <div class="bg-gradient"></div>
    <div class="bg-light-effect"></div>

    <div class="dashboard-body">
      <SidebarLeft
        :active-category="activeCategory"
        @change-category="handleCategoryChange"
      />

      <main class="content-shell">       <section class="content-panel tesla-glass">
          <!-- 实时检测 -->
          <template v-if="activeCategory === 'realtime'">
            <VideoGrid />
          </template>

          <!-- 识别日志 -->
          <template v-else-if="activeCategory === 'logs'">
            <div class="page-block">
              <div class="page-header">
                <h2>识别日志</h2>
                <p>查看识别结果、处理记录与导出内容</p>
              </div>
              <LogTable />
            </div>
          </template>

          <!-- 历史记录 -->
          <template v-else-if="activeCategory === 'history'">
            <div class="page-block">
              <div class="page-header">
                <h2>历史记录</h2>
                <p>异常行为切片缓存与本地历史回放</p>
              </div>
              <div class="empty-card tesla-glass-card">
                <el-icon class="empty-icon"><Clock /></el-icon>
                <p>暂无历史记录，产生异常行为后会自动缓存</p>
              </div>
            </div>
          </template>

          <!-- 兜底 -->
          <template v-else>
            <div class="page-block">
              <div class="empty-card tesla-glass-card">
                <el-icon class="empty-icon"><Warning /></el-icon>
                <p>暂无对应内容，请切换左侧菜单查看</p>
              </div>
            </div>
          </template>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useStore } from 'vuex'
import { Clock, Warning } from '@element-plus/icons-vue'
import SidebarLeft from '@/components/dashboard/SidebarLeft.vue'
import VideoGrid from '@/components/dashboard/VideoGrid.vue'
import LogTable from '@/components/dashboard/LogTable.vue'

let store = null
try {
  store = useStore()
} catch (error) {
  console.warn('Vuex store 初始化失败，使用本地默认数据:', error)
  store = { state: { stats: {} } }
}

const activeCategory = ref('realtime')

const handleCategoryChange = (val) => {
  const validCategories = ['realtime', 'logs', 'history']
  if (validCategories.includes(val)) {
    activeCategory.value = val
  } else {
    activeCategory.value = 'realtime'
  }
}
</script>

<style scoped>
/* ======================
   Tesla 风格核心变量（增强版）
   ====================== */
.dashboard-wrapper {
  --tesla-bg: #0a0d14;
  --tesla-glass: rgba(255, 255, 255, 0.08);
  --tesla-glass-border: rgba(255, 255, 255, 0.12);
  --tesla-highlight: rgba(255, 255, 255, 0.15);
  --tesla-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.05);
  --tesla-text-primary: #ffffff;
  --tesla-text-secondary: rgba(255, 255, 255, 0.7);
  --tesla-text-muted: rgba(255, 255, 255, 0.5);
  --tesla-blue: #0071e3;
  --tesla-radius: 20px;
  --tesla-radius-lg: 24px;
  --nav-height: 80px;

  width: 100vw;
  height: 100vh;
  padding-top: var(--nav-height);
  display: flex;
  flex-direction: column;
  background: var(--tesla-bg);
  overflow: hidden;
  position: relative;
}

/* ======================
   背景层（已去掉流动光）
   ====================== */
.bg-gradient {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(1200px 800px at 20% 20%, rgba(0, 113, 227, 0.18), transparent 60%),
    radial-gradient(900px 700px at 80% 80%, rgba(255, 255, 255, 0.06), transparent 60%);
  z-index: 0;
  animation: bgPulse 10s ease-in-out infinite alternate;
}

.bg-light-effect {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.03), transparent 50%);
  z-index: 1;
}

/* 关键：删掉了原来的扫描流动光动画 */

@keyframes bgPulse {
  0% { opacity: 0.6; transform: scale(1); }
  100% { opacity: 1; transform: scale(1.05); }
}

/* ======================
   布局
   ====================== */
.dashboard-body {
  flex: 1;
  display: flex;
  gap: 16px;
  padding: 16px;
  position: relative;
  z-index: 2;
}

.content-shell {
  flex: 1;
  min-width: 0;
}

/* ======================
   主面板（增强光泽）
   ====================== */
.tesla-glass {
  width: 100%;
  height: 100%;
  border-radius: var(--tesla-radius-lg);

  background: var(--tesla-glass);
  backdrop-filter: blur(20px) saturate(150%);
  border: 1px solid var(--tesla-glass-border);

  box-shadow: var(--tesla-shadow);
  padding: 32px;
  position: relative;
  overflow: hidden;

  transition: all 0.45s cubic-bezier(0.22,1,0.36,1);
}

/* 顶部高光 */
.tesla-glass::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--tesla-highlight), transparent);
}

/* 光泽层 */
.tesla-glass::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: radial-gradient(
    600px circle at 20% 0%,
    rgba(255,255,255,0.08),
    transparent 60%
  );
  pointer-events: none;
}

/* ======================
   页面块
   ====================== */
.page-block {
  height: 100%;
  overflow-y: auto;
  padding-right: 8px;
}

/* 滚动条 */
.page-block::-webkit-scrollbar {
  width: 6px;
}
.page-block::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.12);
  border-radius: 99px;
}

/* ======================
   标题
   ====================== */
.page-header {
  margin-bottom: 30px;
}
.page-header h2 {
  font-size: 30px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--tesla-text-primary);
}
.page-header p {
  font-size: 14px;
  color: var(--tesla-text-secondary);
}

/* ======================
   空状态卡片（升级版）
   ====================== */
.tesla-glass-card {
  padding: 50px 20px;
  border-radius: var(--tesla-radius);

  background: linear-gradient(
    135deg,
    rgba(255,255,255,0.08),
    rgba(255,255,255,0.03)
  );

  backdrop-filter: blur(18px);
  border: 1px solid rgba(255,255,255,0.08);

  box-shadow: 0 8px 30px rgba(0,0,0,0.3);

  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  transition: all 0.3s ease;
}

/* hover 高级感 */
.tesla-glass-card:hover {
  transform: translateY(-6px) scale(1.02);
  box-shadow: 0 16px 50px rgba(0,0,0,0.45);
}

/* 图标动效 */
.empty-icon {
  font-size: 52px;
  color: var(--tesla-blue);
  margin-bottom: 16px;
  animation: iconFloat 3s ease-in-out infinite;
}

@keyframes iconFloat {
  0%,100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* ======================
   响应式
   ====================== */
@media (max-width: 768px) {
  .tesla-glass {
    padding: 20px;
  }
}
</style>