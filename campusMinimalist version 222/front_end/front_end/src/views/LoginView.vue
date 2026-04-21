<template>
  <div class="login-bg">
    <!-- 全屏清晰背景视频 -->
    <video 
      src="@/assets/loginbg.mp4" 
      class="bg-video"
      autoplay
      muted
      loop
      playsinline
    />

    <!-- 中间单个毛玻璃登录卡片 -->
    <div class="login-card">
      <div class="login-form-section">
        <div class="logo-area">
          <div class="logo-icon">🛡️</div>
          <h2>WELCOME</h2>
          <p class="subtitle">智安·视见</p>
        </div>
        
        <div class="input-group">
          <input v-model="username" type="text" placeholder="管理员账号" @keyup.enter="handleLogin" />
          <input v-model="password" type="password" placeholder="授权密钥" @keyup.enter="handleLogin" />
        </div>

        <button @click="handleLogin" :class="{ 'loading': isLoggingIn }">
          {{ isLoggingIn ? '正在授权...' : '授权进入' }}
        </button>

        <div class="footer"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const username = ref('');
const password = ref('');
const isLoggingIn = ref(false);

const handleLogin = () => {
  if (!username.value || !password.value) {
    alert('请填写账号和密钥');
    return;
  }

  isLoggingIn.value = true;

  setTimeout(() => {
    localStorage.setItem('sentinel_logged_in', '1');
    router.push('/home');
    isLoggingIn.value = false;
  }, 600);
};
</script>

<style scoped>
/* 全屏背景 不变 */
.login-bg { 
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex; 
  align-items: center; 
  justify-content: center; 
  overflow: hidden;
}

/* 清晰背景视频 不变 */
.bg-video {
  position: absolute;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 0;
}

/* ———————————————————————————————————— */
/* 🔥 液态玻璃静态边框 · 慢速流动 · 高亮 */
/* ———————————————————————————————————— */
.login-card { 
  width: 550px;
  background-color: rgba(13, 10, 72, 0.88);
  padding: 80px;
  border-radius: 50px;
  box-shadow: 0 0 100px rgba(138, 138, 207, 0.8) inset;
  animation: zoomIn 1s ease forwards;
  z-index: 10;
  position: relative;
  border: 2px solid rgba(255,255,255,0.15);
}

/* 🔥 高亮液态流动光效 · 慢速 · 边框再加粗 */
.login-card::before {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: 50px;
  z-index: -1;
  
  /* 更亮的浅蓝紫色 */
  background: linear-gradient(90deg, 
    rgba(165, 145, 255, 0.3), 
    rgba(205, 195, 255, 0.85), 
    rgba(165, 145, 255, 0.3)
  );
  background-size: 200% 100%;
  animation: flow-light 2s linear infinite;
  
  /* 只显示边框 */
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  padding: 4px;
}

/* 流动动画（更慢） */
@keyframes flow-light {
  0% { background-position: 200% 0; }
  100% { background-position: 0% 0; }
}

.login-form-section {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.logo-icon { 
  font-size: 52px; 
  margin-bottom: 15px; 
  text-align: center;
  color: #ffffff;
}

h2 { 
  color: #f0f0f6d6;
  font-size: 70px;
  font-weight: 700;
  margin: 0 0 10px 0;
  text-align: center;
}

.subtitle {
  color: #f4f4f7d6;
  font-size: 18px;
  margin-bottom: 40px;
  text-align: center;
}

.input-group { 
  width: 100%;
  margin-bottom: 15px;
}

/* ———————————————————————————————————— */
/* 🔥 输入框修改：输入文字白色 + 光标白色 */
/* ———————————————————————————————————— */
input { 
  width: 100%;
  height: 40px;
  margin: 10px 0;
  border: none;
  outline: none;
  border-radius: 100px;
  padding: 5px 20px;
  font-size: 18px;
  background: rgba(132, 117, 188, 0.5);
  transition: 0.4s;
  box-sizing: border-box;
  
  /* 输入出来的文字 白色 */
  color: #ffffff;
  
  /* 鼠标光标 白色 */
  caret-color: #ffffff;
}

input:hover {
  background: rgba(0, 20, 170, 0.114);
  border: 4px solid rgb(149, 139, 220);
}

input::placeholder {
  color: #dfdeed;
}

/* ———————————————————————————————————— */
/* 🔥 按钮渐变（不变） */
/* ———————————————————————————————————— */
button { 
  width: 100%;
  height: 50px;
  margin: 15px 0;
  border-radius: 100px;
  border: none;
  background: linear-gradient(200deg, #3835c8a0, #a493db);
  font-size: 20px;
  color: rgb(226, 226, 226);
  cursor: pointer;
}

.footer { 
  width: 100%;
  text-align: center;
  margin-top: 20px;
  padding-top: 20px;
  font-size: 14px;
  color: #0d0b92;
}

/* 入场动画 */
@keyframes zoomIn {
  0% { transform: scale(0); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

.loading {
  opacity: 0.8;
  cursor: not-allowed;
}
</style>