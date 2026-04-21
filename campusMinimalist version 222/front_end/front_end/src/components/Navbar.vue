<template setup>
  <div class="nav-container" :class="{ 'nav-scrolled': isScrolled }">
    <div class="nav-capsule">

      <!-- LOGO -->
      <div class="nav-logo">
        <div class="logo-dot"></div>
        <div class="logo-text-group">
          <span class="logo-cn">智安·视见</span>
          <span class="logo-en">VisionGuard AI</span>
        </div>
      </div>

      <div class="nav-divider"></div>

      <!-- 菜单 -->
      <div 
        class="nav-menu" 
        ref="navRef"
        @mousemove="handleMouseMove"
      >

        <!-- 光晕 -->
        <div 
          class="nav-glow"
          :style="{
            left: glow.x + 'px',
            top: glow.y + 'px'
          }"
        ></div>

        <!-- 点击滑块 -->
        <div 
          class="slide1"
          :style="slide1Style"
        ></div>

        <!-- hover 滑块 -->
        <div 
          class="slide2"
          :style="slide2Style"
        ></div>

        <!-- 菜单项 -->
        <div 
          v-for="(item, index) in menuItems" 
          :key="item.path"
          class="nav-item"
          :ref="el => itemRefs[index] = el"
        >
          <a
            @click="handleNav(item.path)"
            @mouseenter="handleHover(index)"
            @mouseleave="clearHover"
          >
            {{ item.label }}
          </a>
        </div>

      </div>

      <div class="nav-divider"></div>

      <!-- 状态 -->
      <div class="nav-status">
        <span class="pulse-dot"></span>
        <!-- 显示时间 -->
        <span class="current-time">{{ currentTime }}</span>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const navRef = ref(null)
const itemRefs = ref([])

const activePath = ref(route.path)
const isScrolled = ref(false)

// 光晕
const glow = ref({ x: 0, y: 0 })

// 滑块
const slide1 = ref({ left: 0, width: 0, opacity: 0 })
const slide2 = ref({ left: 0, width: 0, opacity: 0 })

// ✅ 只保留 首页 + 功能
const menuItems = [
  { label: '首页', path: '/home' },
  { label: '功能', path: '/dashboard' }
]

// style
const slide1Style = computed(() => ({
  left: slide1.value.left + 'px',
  width: slide1.value.width + 'px',
  opacity: slide1.value.opacity
}))

const slide2Style = computed(() => ({
  left: slide2.value.left + 'px',
  width: slide2.value.width + 'px',
  opacity: slide2.value.opacity
}))

// 更新选中滑块
const updateSlide1 = async () => {
  await nextTick()

  const index = menuItems.findIndex(i => i.path === activePath.value)
  const el = itemRefs.value[index]

  if (!el || !navRef.value) return

  const pos = el.getBoundingClientRect()
  const navPos = navRef.value.getBoundingClientRect()

  slide1.value = {
    left: pos.left - navPos.left,
    width: pos.width,
    opacity: 1
  }
}

// hover
const handleHover = (index) => {
  const el = itemRefs.value[index]
  if (!el || !navRef.value) return

  const pos = el.getBoundingClientRect()
  const navPos = navRef.value.getBoundingClientRect()

  slide2.value = {
    left: pos.left - navPos.left,
    width: pos.width,
    opacity: 1
  }
}

const clearHover = () => {
  slide2.value.opacity = 0
}

// 鼠标光晕
const handleMouseMove = (e) => {
  if (!navRef.value) return
  const rect = navRef.value.getBoundingClientRect()
  glow.value = {
    x: e.clientX - rect.left,
    y: e.clientY - rect.top
  }
}

// 跳转
const handleNav = (path) => {
  router.push(path)
}

// 路由监听
watch(() => route.path, (val) => {
  activePath.value = val
  updateSlide1()
})

// 初始化
onMounted(() => {
  updateSlide1()

  window.addEventListener('scroll', () => {
    isScrolled.value = window.scrollY > 20
  })
})

// 当前时间
const currentTime = ref('')

// 更新当前时间的函数
const updateTime = () => {
  const date = new Date()
  currentTime.value = date.toLocaleTimeString() // 格式化时间为 HH:MM:SS
}

// 每秒更新一次时间
onMounted(() => {
  updateTime()
  setInterval(updateTime, 1000) // 每秒更新一次时间
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Poppins:wght@500;600;700&family=Montserrat:ital,wght@0,700;1,700&display=swap');

/* 容器 */
.nav-container {
  position: fixed;
  top: 0;
  width: 100%;
  height: 90px;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  background: rgba(10, 14, 34, 0.893);
  backdrop-filter: blur(20px) saturate(160%);
  -webkit-backdrop-filter: blur(20px) saturate(160%);
  border-bottom: 1px solid rgba(255,255,255,0.08);
  box-shadow: 
    0 8px 30px rgba(0,0,0,0.45),
    0 2px 8px rgba(0,0,0,0.3);
  transition: all 0.4s ease;
}

.nav-scrolled {
  background: rgba(10,14,34,0.85);
  backdrop-filter: blur(24px) saturate(180%);
}

/* 内部 */
.nav-capsule {
  width: 100%;
  max-width: 1500px;
  padding: 0 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* LOGO */
.nav-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 180px;
}

.nav-status {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  min-width: 180px;
}

.logo-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: linear-gradient(135deg,#4f46e5,#2e8bff);
  box-shadow: 0 0 14px rgba(79,70,229,0.7);
  animation: breathe 3s infinite;
}

@keyframes breathe {
  0%,100% { transform: scale(1); }
  50% { transform: scale(1.3); }
}

.logo-text-group {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
}
.logo-cn {
  font-family: 'douyu', sans-serif !important;
  font-weight: 100;
  font-size: 22px;
  color: #fff;
  letter-spacing: 1px;
}
.logo-en {
  font-family: 'Montserrat', sans-serif !important;
  font-weight: 700;
  font-style: italic;
  font-size: 11px;
  color: rgba(200,210,255,0.7);
  letter-spacing: 0.5px;
}

.nav-divider {
  width: 1px;
  height: 32px;
  background: rgba(100,120,200,0.3);
  margin: 0 20px;
}

.nav-menu {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 100px;
  flex: 1;
}

.nav-glow {
  position: absolute;
  width: 220px;
  height: 220px;
  pointer-events: none;
  background: radial-gradient(circle,
    rgba(99,102,241,0.35),
    transparent 70%
  );
  transform: translate(-50%, -50%);
  filter: blur(40px);
  z-index: 0;
}

.slide1, .slide2 {
  position: absolute;
  height: 54px;
  border-radius: 100px;
  top: 50%;
  transform: translateY(-50%);
  transition: all 0.4s ease;
}

.slide1 {
  z-index: 2;
  border: 2px solid transparent;
  background:
    linear-gradient(#0000008a,#010101d9) padding-box,
    linear-gradient(120deg,#4f46e5,#3b82f6,#a5b4fc) border-box;
  box-shadow: 0 0 20px rgba(79,70,229,0.4);
}

.slide2 {
  background: linear-gradient(
    120deg,
    #4f46e5 0%,
    #3b82f6 25%,
    #a5b4fc 50%,
    #3b82f6 75%,
    #4f46e5 100%
  );

  background-size: 200% 100%;
  animation: flow 2.5s linear infinite;
}

@keyframes flow {
  0% { background-position: 0% 50%; }
  100% { background-position: 100% 50%; }
}

.nav-item {
  padding: 14px 0px;
  z-index: 3;
}

.nav-item a {
  padding: 12px 60px;
  cursor: pointer;
  color: rgba(255,255,255,0.85);
  font-size: 22px;
  transition: all 0.25s ease;
}

.nav-item a:hover {
  transform: translateY(-2px) scale(1.05);
  color: #fff;
}

.pulse-dot {
  width: 10px;
  height: 10px;
  background: #34c759;
  border-radius: 50%;
  box-shadow: 0 0 10px #34c759;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); opacity:1;}
  100% { transform: scale(2.5); opacity:0;}
}

/* 更加精致的时间样式 */
.current-time {
  font-size: 32px; /* 更大的字体 */
  background: linear-gradient(120deg, #4f46e5, #3b82f6); /* 更蓝的渐变色 */
  -webkit-background-clip: text;
  color: transparent;
  margin-left: 15px;
  font-family: 'Poppins', sans-serif;
  font-weight: 700;
  letter-spacing: 1px;
  text-shadow: 0 0 8px rgba(79, 70, 229, 0.5), 0 0 20px rgba(79, 70, 229, 0.3); /* 蓝色光晕和阴影效果 */
}
</style>