<template>
  <div class="app-container">
    <!-- 导航栏：非首页显示 -->
    <Navbar v-if="$route.path !== '/'"/>

    <!-- 路由视图：完全不限制样式 -->
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade-slide" mode="out-in">
          <component :is="Component"/>
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import Navbar from '@/components/Navbar.vue'
import { useRoute } from 'vue-router'
const route = useRoute()
</script>

<style>
/* 全局只保留最基础的样式，不干涉任何页面 */
:root {
  --brand-color: #0071e3;
  --bg-color: #f5f5f7;
}

/* 基础全局样式，不影响布局 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  width: 100%;
  height: auto;
  overflow-x: hidden;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background-color: var(--bg-color);
  color: #1d1d1f;
  -webkit-font-smoothing: antialiased;
}

.app-container {
  min-height: 100vh;
  width: 100%;
}

/* 🔥 关键：main 内容区域 不写任何 padding / margin / 高度 */
.main-content {
  /* 完全空的，不限制任何页面！ */
}

/* 页面切换动画（保留，不影响布局） */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>