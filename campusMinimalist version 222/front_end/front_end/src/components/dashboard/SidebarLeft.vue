<template>
  <aside class="sidebar-left">
    <div class="sidebar-surface">
      <div class="section-group">
        <div class="section-head">
          <h3>功能菜单</h3>
          <p>切换视图</p>
        </div>
        <div class="nav-list">
          <button
            v-for="item in categories"
            :key="item.key"
            class="nav-item"
            :class="{ active: activeCategory === item.key }"
            @click="$emit('change-category', item.key)"
          >
            <div class="nav-content">
              <span class="nav-title">{{ item.label }}</span>
              <span class="nav-desc">{{ item.desc }}</span>
            </div>
          </button>
        </div>
      </div>

      <div class="section-divider"></div>

      <div class="section-group camera-group">
        <div class="section-head">
          <h3>监控点位</h3>
          <p>实时监控列表</p>
        </div>
        <div class="camera-list">
          <button
            v-for="cam in cameras"
            :key="cam.id"
            class="camera-item"
            :class="{ active: selectedCamera === cam.id, warning: cam.status === 'warning' }"
            @click="handleSelect(cam)"
          >
            <div class="camera-preview" :class="'preview-' + cam.status"></div>
            <div class="camera-info">
              <div class="camera-top">
                <span class="name">{{ cam.name }}</span>
                <span class="status-tag" :class="cam.status">{{ statusMap[cam.status] }}</span>
              </div>
              <div class="camera-meta">{{ cam.location }} | 1080P</div>
            </div>
          </button>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from 'vuex'

defineProps({ activeCategory: String })
defineEmits(['change-category'])

const store = useStore()
const statusMap = { online: '在线', warning: '告警', offline: '离线' }

const categories = [
  { key: 'realtime', label: '实时检测', desc: '视频流AI识别演示' },
  { key: 'logs', label: '识别日志', desc: '历史记录与处置状态' },
  { key: 'history', label: '历史记录', desc: '视频切片存档' }
]

const cameras = computed(() => [
  { id: 1, name: '东门出口', status: 'online', location: '教学楼A区' },
  { id: 2, name: '西区围栏', status: 'warning', location: '宿舍区后方' },
  { id: 3, name: '实验大楼', status: 'online', location: '实验区' }
])

const selectedCamera = computed(() => store?.state?.selectedCamera || 1)

function handleSelect(cam) {
  if (cam.status === 'offline') return
  store?.dispatch('selectCamera', cam.id)
}
</script>

<style scoped>
.sidebar-left {
  width: 280px;
  height: 100%;
  flex-shrink: 0;
}

.sidebar-surface {
  --bg-1: #060a11;
  --bg-2: #0b1220;
  --glass: rgba(255, 255, 255, 0.05);
  --glass-strong: rgba(255, 255, 255, 0.09);
  --glass-border: rgba(255, 255, 255, 0.09);
  --glass-border-strong: rgba(255, 255, 255, 0.16);
  --highlight: rgba(255, 255, 255, 0.18);

  --text-primary: #f4f7ff;
  --text-secondary: rgba(244, 247, 255, 0.72);
  --text-muted: rgba(244, 247, 255, 0.45);

  /* 只改这里：蓝紫色系（柔和高级） */
  --nav-blue-1: #2a3a70;
  --nav-blue-2: #5a69e5;
  --nav-blue-3: #3a4d8f;
  --nav-blue-glow: rgba(107, 122, 255, 0.24);

  --green: #22c55e;
  --orange: #f59e0b;
  --gray: #94a3b8;

  --radius: 18px;
  --radius-lg: 24px;

  --shadow-panel:
    0 24px 60px rgba(0, 0, 0, 0.42),
    inset 0 1px 0 rgba(255, 255, 255, 0.04);

  --shadow-soft: 0 10px 30px rgba(0, 0, 0, 0.22);
  --shadow-active:
    0 14px 34px rgba(0, 0, 0, 0.28),
    0 0 0 1px rgba(107, 122, 255, 0.18),
    0 0 22px rgba(107, 122, 255, 0.16);

  position: relative;
  height: 100%;
  border-radius: var(--radius-lg);
  background:
    radial-gradient(circle at top left, rgba(45, 84, 148, 0.18), transparent 28%),
    radial-gradient(circle at top right, rgba(74, 108, 173, 0.12), transparent 22%),
    linear-gradient(180deg, rgba(13, 19, 33, 0.97), rgba(7, 11, 18, 0.98));
  backdrop-filter: blur(24px) saturate(145%);
  -webkit-backdrop-filter: blur(24px) saturate(145%);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-panel);
  padding: 22px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;
}

.sidebar-surface::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg, rgba(255,255,255,0.04), transparent 12%),
    linear-gradient(135deg, rgba(255,255,255,0.03), transparent 24%, transparent 76%, rgba(255,255,255,0.02));
  pointer-events: none;
}

.sidebar-surface::after {
  content: '';
  position: absolute;
  top: 0;
  left: 18px;
  right: 18px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.24), transparent);
  opacity: 0.75;
  pointer-events: none;
}

.section-group {
  position: relative;
  z-index: 1;
}

.section-head {
  margin-bottom: 12px;
}

.section-head h3 {
  margin: 0;
  font-size: 17px;
  font-weight: 700;
  letter-spacing: 0.2px;
  color: var(--text-primary);
}

.section-head p {
  margin: 4px 0 0;
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 0.3px;
}

.nav-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.nav-item {
  width: 100%;
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 15px 16px;
  border-radius: var(--radius);
  text-align: left;
  cursor: pointer;
  overflow: hidden;
  background:
    linear-gradient(180deg, rgba(255,255,255,0.055), rgba(255,255,255,0.03));
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,0.03),
    0 6px 16px rgba(0, 0, 0, 0.16);
  transition:
    transform 0.24s ease,
    border-color 0.24s ease,
    background 0.24s ease,
    box-shadow 0.24s ease;
}

.nav-item::before {
  content: '';
  position: absolute;
  inset: 1px;
  border-radius: inherit;
  background: linear-gradient(180deg, rgba(255,255,255,0.07), transparent 50%);
  opacity: 0.7;
  pointer-events: none;
}

.nav-item::after {
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

.nav-item:hover:not(.active) {
  transform: translateY(-2px);
  border-color: rgba(255, 255, 255, 0.14);
  background:
    linear-gradient(180deg, rgba(255,255,255,0.085), rgba(255,255,255,0.045));
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,0.05),
    0 12px 24px rgba(0, 0, 0, 0.22);
}

.nav-item:hover::after {
  transform: translateX(220%) rotate(18deg);
  opacity: 1;
}

/* 按钮激活颜色（只微调成蓝紫，效果完全不变） */
.nav-item.active {
  border-color: rgba(107, 122, 255, 0.34);
  background:
    radial-gradient(circle at 85% 20%, rgba(140, 153, 255, 0.16), transparent 28%),
    linear-gradient(145deg, rgba(42, 58, 112, 0.96), rgba(30, 44, 94, 0.98));
  box-shadow: var(--shadow-active);
  transform: translateY(-1px);
}

.nav-item.active::before {
  background: linear-gradient(180deg, rgba(255,255,255,0.11), rgba(255,255,255,0.02));
}

.nav-item.active::after {
  opacity: 1;
  background: linear-gradient(90deg, transparent, rgba(173, 210, 255, 0.12), transparent);
}

.nav-item.active .nav-content::before {
  content: '';
  position: absolute;
  left: -16px;
  top: 4px;
  bottom: 4px;
  width: 3px;
  border-radius: 999px;
  background: linear-gradient(180deg, rgba(198,223,255,0.95), rgba(140, 153, 255, 0.78));
  box-shadow:
    0 0 10px rgba(140, 153, 255, 0.3),
    0 0 20px rgba(107, 122, 255, 0.16);
}

.nav-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  position: relative;
  z-index: 1;
}

.nav-title {
  display: block;
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
  transition: color 0.24s ease;
}

.nav-desc {
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.35;
  transition: color 0.24s ease;
}

.nav-item.active .nav-title {
  color: #f8fbff;
}

.nav-item.active .nav-desc {
  color: rgba(234, 242, 255, 0.78);
}

.section-divider {
  height: 1px;
  margin: 20px 0 18px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.18), transparent);
  opacity: 0.75;
  position: relative;
  z-index: 1;
}

.camera-group {
  min-height: 0;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.camera-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-right: 4px;
}

.camera-item {
  position: relative;
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: var(--radius);
  cursor: pointer;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.08);
  background:
    linear-gradient(180deg, rgba(255,255,255,0.055), rgba(255,255,255,0.03));
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,0.03),
    0 6px 16px rgba(0,0,0,0.16);
  transition:
    transform 0.24s ease,
    border-color 0.24s ease,
    background 0.24s ease,
    box-shadow 0.24s ease;
}

.camera-item::before {
  content: '';
  position: absolute;
  inset: 1px;
  border-radius: inherit;
  background: linear-gradient(180deg, rgba(255,255,255,0.07), transparent 48%);
  opacity: 0.68;
  pointer-events: none;
}

.camera-item:hover:not(.active) {
  transform: translateY(-2px);
  border-color: rgba(255,255,255,0.14);
  background:
    linear-gradient(180deg, rgba(255,255,255,0.085), rgba(255,255,255,0.045));
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,0.05),
    0 12px 24px rgba(0,0,0,0.22);
}

.camera-item.active {
  border-color: rgba(78, 132, 214, 0.28);
  background:
    linear-gradient(180deg, rgba(23, 58, 112, 0.22), rgba(12, 36, 72, 0.12));
  box-shadow:
    0 10px 26px rgba(9, 20, 38, 0.32),
    0 0 0 1px rgba(64, 123, 212, 0.12);
}

.camera-item.active::after {
  content: '';
  position: absolute;
  left: 0;
  top: 12%;
  bottom: 12%;
  width: 3px;
  border-radius: 999px;
  background: linear-gradient(180deg, rgba(194,220,255,0.92), rgba(92,149,236,0.82));
  box-shadow: 0 0 12px rgba(67, 121, 205, 0.26);
}

.camera-item.warning {
  border-color: rgba(245, 158, 11, 0.18);
}

.camera-item.warning:not(.active) {
  background:
    linear-gradient(180deg, rgba(255,255,255,0.055), rgba(245,158,11,0.04));
}

.camera-preview {
  width: 52px;
  height: 40px;
  border-radius: 12px;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.08);
  background:
    linear-gradient(135deg, rgba(255,255,255,0.12), rgba(255,255,255,0.04)),
    linear-gradient(135deg, rgba(45,84,148,0.16), rgba(85,112,168,0.06));
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,0.08),
    0 4px 10px rgba(0,0,0,0.18);
}

.camera-preview::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    linear-gradient(135deg, transparent 0 35%, rgba(255,255,255,0.05) 50%, transparent 65%),
    repeating-linear-gradient(
      0deg,
      rgba(255,255,255,0.018) 0px,
      rgba(255,255,255,0.018) 1px,
      transparent 1px,
      transparent 5px
    );
  pointer-events: none;
}

.preview-online {
  background:
    linear-gradient(135deg, rgba(34,197,94,0.14), rgba(45,84,148,0.08)),
    linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
}

.preview-warning {
  background:
    linear-gradient(135deg, rgba(245,158,11,0.24), rgba(239,68,68,0.08)),
    linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
}

.preview-offline {
  background:
    linear-gradient(135deg, rgba(148,163,184,0.16), rgba(71,85,105,0.08)),
    linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
}

.camera-info {
  flex: 1;
  min-width: 0;
}

.camera-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.name {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-tag {
  flex-shrink: 0;
  font-size: 10px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 999px;
  border: 1px solid transparent;
  letter-spacing: 0.2px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.08);
}

.status-tag.online {
  color: #5ee38f;
  background: rgba(34, 197, 94, 0.12);
  border-color: rgba(34, 197, 94, 0.18);
}

.status-tag.warning {
  color: #ffb84d;
  background: rgba(245, 158, 11, 0.12);
  border-color: rgba(245, 158, 11, 0.18);
}

.status-tag.offline {
  color: #cbd5e1;
  background: rgba(148, 163, 184, 0.1);
  border-color: rgba(148, 163, 184, 0.12);
}

.camera-meta {
  margin-top: 4px;
  font-size: 11px;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.camera-list::-webkit-scrollbar {
  width: 5px;
}

.camera-list::-webkit-scrollbar-track {
  background: transparent;
}

.camera-list::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.12);
  border-radius: 999px;
}

.camera-list::-webkit-scrollbar-thumb:hover {
  background: rgba(255,255,255,0.2);
}
</style>