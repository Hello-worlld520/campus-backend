<template>
  <div class="page-container">
    <div class="mobile-tip">移动端只支持查看，编辑请前往Web版</div>

    <header>
      <video class="img" autoplay muted loop playsinline>
        <source src="@/assets/background.mp4" type="video/mp4">
      </video>

      <div class="header-overlay-text">
        <div class="badge">
          <span class="dot"></span>
          校园智能安防解决方案
        </div>
        <h1 class="main-title en-text">VisionGuard AI</h1>
        <h1 class="main-title cn-text">智安·视见</h1>

        <div class="hero-action">
          <button
              ref="techBtn"
              class="glass-play-btn"
              :class="{ pressing: isPressing, hovering: isHovering }"
              @mousemove="handleBtnMove"
              @mouseenter="handleBtnEnter"
              @mouseleave="handleBtnLeave"
              @click="handleTechClick"
          >
            <span class="glass-play-btn__base"></span>
            <span class="glass-play-btn__inner"></span>
            <span class="glass-play-btn__aurora"></span>
            <span class="glass-play-btn__press"></span>
            <span class="glass-play-btn__shine"></span>
            <span class="glass-play-btn__text">Launch</span>

            <span
                v-for="ripple in ripples"
                :key="ripple.id"
                class="glass-ripple"
                :style="{
                left: ripple.x + 'px',
                top: ripple.y + 'px',
                width: ripple.size + 'px',
                height: ripple.size + 'px',
                '--ripple-scale': ripple.scale,
                '--ripple-duration': ripple.duration + 'ms'
              }"
            ></span>
          </button>
        </div>
      </div>
    </header>

    <div class="main">
      <main>
        <article>
          <h1>我们致力于......</h1>
          <h2 class="en-sub-title">WE ARE COMMITTED TO......</h2>
        </article>

        <!-- 三张图片卡片展示区域 -->
<section class="triple-image-section" id="image-section">
  <div class="triple-img-box fade-up-item">
    <div class="card-image">
      <img src="@/assets/img1.jpg" alt="场景1" />
    </div>
    <div class="card-text">
      <h3>算法模型创新</h3>
      <p>CNN+BiLSTM+Self-Attention混合架构，识别准确率≥92%</p>
    </div>
  </div>

  <div class="triple-img-box fade-up-item">
    <div class="card-image">
      <img src="@/assets/img2.jpg" alt="场景2" />
    </div>
    <div class="card-text">
      <h3>工程架构创新</h3>
      <p>多路视频并发处理，支持16路监控同时稳定接入</p>
    </div>
  </div>

  <div class="triple-img-box fade-up-item">
    <div class="card-image">
      <img src="@/assets/img3.jpg" alt="场景3" />
    </div>
    <div class="card-text">
      <h3>可视化交互创新</h3>
      <p>实时告警推送+热力图分析，安防管理更智能</p>
    </div>
  </div>
</section>

        <div id="carousel-container">
          <div id="click-section">
            <div id="drawerboxes">
              <div class="drawerbox active">
                <button class="drawer-btn active" @click="slideTo(1)">算法创新<span
                    class="drawer-head">1</span></button>
              </div>
              <div class="drawerbox">
                <button class="drawer-btn" @click="slideTo(2)">系统功能<span
                    class="drawer-head">2</span></button>
              </div>
              <div class="drawerbox">
                <button class="drawer-btn" @click="slideTo(3)">技术难点<span class="drawer-head">3</span></button>
              </div>
              <div class="drawerbox">
                <button class="drawer-btn" @click="slideTo(4)">应用价值<span class="drawer-head">4</span></button>
              </div>
            </div>
          </div>
          <div id="slide-section">
            <div id="slide-bar">
              <div id="bar"></div>
            </div>
            <div id="card-section">
              <div id="card1" class="card">
                <div class="card-small-title">ALGORITHM INNOVATION</div>
                <div class="card-title">算法创新</div>
                <div class="card-content">采用CNN+BiLSTM+Self-Attention三阶段混合架构，结合卡尔曼滤波与几何规则辅助，实现11类行为精准识别，综合准确率达92.3%，有效降低误报漏报。</div>
                <div class="card-img">
                  <img src="@/assets/11.jpg" alt="预警体系">
                </div>
              </div>
              <div id="card2" class="card">
                <div class="card-small-title">SYSTEM FUNCTION</div>
                <div class="card-title">系统功能</div>
                <div class="card-content">支持多源视频接入、实时姿态估计、行为识别、告警推送、热力图统计、日志管理等全功能模块，覆盖校园安防全场景需求。</div>
                <div class="card-img">
                  <img src="@/assets/22.jpg" alt="智能监测">
                </div>
              </div>
              <div id="card3" class="card">
                <div class="card-small-title">TECHNICAL SOLUTIONS</div>
                <div class="card-title">技术难点</div>
                <div class="card-content">成功解决俯视视角骨架提取、长程时序依赖、多路并发资源竞争、低置信度误报、系统长时间稳定运行五大核心技术难题。</div>
                <div class="card-img">
                  <img src="@/assets/33.jpg" alt="应急响应">
                </div>
              </div>
              <div id="card4" class="card">
                <div class="card-small-title">APPLICATION VALUE</div>
                <div class="card-title">应用价值</div>
                <div class="card-content">项目可广泛应用于校园、商场、医院等场景，实现安全风险早发现、早预警、早处置，具备极高的社会价值与商业推广前景。</div>
                <div class="card-img">
                  <img src="@/assets/44.jpg" alt="安全守护">
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, nextTick } from 'vue';

const chosenSlideNumber = ref(1);
const offset = ref(0);
const barOffset = ref(0);
let intervalID = null;
let scrollHandler = null;
let carouselStarted = ref(false); // 控制轮播是否开始

/* 按钮交互 */
const techBtn = ref(null);
const isPressing = ref(false);
const isHovering = ref(false);
const ripples = ref([]);
let rippleSeed = 0;

// —————————————————— 修复：自动轮播（进入视口才启动）
const startSlide = () => {
  if (intervalID) clearInterval(intervalID);
  intervalID = setInterval(() => {
    slideTo(chosenSlideNumber.value % 4 + 1);
  }, 3000);
};

const stopSlide = () => {
  if (intervalID) {
    clearInterval(intervalID);
    intervalID = null;
  }
};

const slideTo = (slideNumber) => {
  stopSlide(); // 点击时暂停自动轮播
  nextTick(() => {
    const drawerboxes = document.querySelectorAll(".drawerbox");
    if (drawerboxes[chosenSlideNumber.value - 1]) {
      drawerboxes[chosenSlideNumber.value - 1].classList.remove("active");
    }
    if (drawerboxes[slideNumber - 1]) {
      drawerboxes[slideNumber - 1].classList.add("active");
    }

    const drawerBtns = document.querySelectorAll(".drawer-btn");
    if (drawerBtns[chosenSlideNumber.value - 1]) {
      drawerBtns[chosenSlideNumber.value - 1].classList.remove("active");
    }
    if (drawerBtns[slideNumber - 1]) {
      drawerBtns[slideNumber - 1].classList.add("active");
    }

    offset.value += (slideNumber - chosenSlideNumber.value) * (-100);
    barOffset.value += (slideNumber - chosenSlideNumber.value) * (100);

    const bar = document.querySelector("#bar");
    if (bar) {
      bar.style.transform = `translateY(${barOffset.value}%)`;
    }

    const slides = document.querySelectorAll(".card");
    slides.forEach(slide => {
      slide.style.transform = `translateY(${offset.value}%)`;
    });
    chosenSlideNumber.value = slideNumber;

    setTimeout(() => {
      startSlide();
    }, 1000);
  });
};

const handleBtnEnter = () => {
  isHovering.value = true;
};

const handleBtnLeave = () => {
  isHovering.value = false;
  if (!techBtn.value) return;

  techBtn.value.style.setProperty('--mx', '50%');
  techBtn.value.style.setProperty('--my', '50%');
  techBtn.value.style.setProperty('--px', '50%');
  techBtn.value.style.setProperty('--py', '50%');
  techBtn.value.style.setProperty('--tilt-x', '0px');
  techBtn.value.style.setProperty('--tilt-y', '0px');
  techBtn.value.style.transform = 'translate3d(0, 0, 0) scale(1)';
};

const handleBtnMove = (e) => {
  const btn = techBtn.value;
  if (!btn) return;

  const rect = btn.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;

  const mx = (x / rect.width) * 100;
  const my = (y / rect.height) * 100;

  btn.style.setProperty('--mx', `${mx}%`);
  btn.style.setProperty('--my', `${my}%`);

  const dx = (x - rect.width / 2) / rect.width;
  const dy = (y - rect.height / 2) / rect.height;

  btn.style.setProperty('--tilt-x', `${dx * 8}px`);
  btn.style.setProperty('--tilt-y', `${dy * 6}px`);
  btn.style.transform = `translate3d(${dx * 5}px, ${dy * 4}px, 0) scale(1.01)`;
};

const createRipple = (x, y, rect) => {
  const ripple = {
    id: `${Date.now()}-${rippleSeed++}`,
    x,
    y,
    size: Math.max(rect.width, rect.height) * 0.52,
    scale: 2.25,
    duration: 760
  };

  ripples.value = [...ripples.value, ripple];

  setTimeout(() => {
    ripples.value = ripples.value.filter((item) => item.id !== ripple.id);
  }, ripple.duration + 80);
};

const handleTechClick = (e) => {
  const btn = techBtn.value;
  if (!btn) return;

  const rect = btn.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;

  const px = (x / rect.width) * 100;
  const py = (y / rect.height) * 100;

  btn.style.setProperty('--px', `${px}%`);
  btn.style.setProperty('--py', `${py}%`);
  btn.style.setProperty('--mx', `${px}%`);
  btn.style.setProperty('--my', `${py}%`);

  isPressing.value = false;
  requestAnimationFrame(() => {
    isPressing.value = true;
  });

  createRipple(x, y, rect);

  setTimeout(() => {
    isPressing.value = false;
  }, 620);
};

const checkImageInView = () => {
  const section = document.querySelector('#image-section');
  if (!section) return;
  const rect = section.getBoundingClientRect();
  const windowHeight = window.innerHeight;
  
  if (rect.top < windowHeight * 0.7 && rect.bottom > 0) {
    document.querySelectorAll('.fade-up-item').forEach((el, i) => {
      setTimeout(() => {
        el.classList.add('fade-up-active');
      }, i * 180);
    });
  } else {
    document.querySelectorAll('.fade-up-item').forEach(el => {
      el.classList.remove('fade-up-active');
    });
  }
};

// —————————————————— 修复：轮播进入视口才启动
const checkCarouselInView = () => {
  const carousel = document.querySelector('#carousel-container');
  if (!carousel) return;
  const rect = carousel.getBoundingClientRect();
  const windowHeight = window.innerHeight;

  if (rect.top < windowHeight * 0.7 && rect.bottom > 0) {
    if (!carouselStarted.value) {
      carouselStarted.value = true;
      startSlide();
    }
  }
};

onMounted(() => {
  const header = document.querySelector('header');
  const img = document.querySelector('.img');

  document.documentElement.style.overflowY = 'scroll';

  scrollHandler = () => {
    const scroll = window.scrollY;
    if (img) {
      img.style.transform = `scale(${1 + scroll / 1200})`;
    }
    if (header) {
      header.style.clipPath = `polygon(
        0 0,
        100% 0,
        100% ${Math.max(30, 100 - scroll * 0.25)}%,
        0 ${Math.max(30, 100 - scroll * 0.08)}%
      )`;
    }
    checkImageInView();
    checkCarouselInView();
  };

  window.addEventListener('scroll', scrollHandler);
  scrollHandler();
});

onUnmounted(() => {
  window.removeEventListener('scroll', scrollHandler);
  stopSlide();
});
</script>
<style scoped>
/* ———————————————————————————————————— */
/* Google Fonts 英文粗斜体 */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,700;1,700&family=Nunito:wght@400;600;700&display=swap');
@font-face {
  font-family: 'douyu';
  src: url('@/assets/fonts/youshe.ttf') format('truetype');
  font-weight: normal;
  font-style: normal;
  font-display: swap;
}
/* ———————————————————————————————————— */

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.page-container {
  width: 100%;
  margin: 0;
  padding: 0;
}

.mobile-tip {
  display: none;
}

header {
  width: 100%;
  height: 700px;
  position: relative;
  top: 0;
  left: 0;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden;
  transition: clip-path 0.3s ease;
  clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%);
}

.img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.header-overlay-text {
  position: absolute;
  left: 80px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 2;
  max-width: 700px;
  color: #fff;
  pointer-events: none;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 99px;
  border: 1px solid rgba(67, 56, 202, 0.3);
  background: rgba(67, 56, 202, 0.15);
  font-size: 16px;
  letter-spacing: 0.28em;
  margin-bottom: 20px;
  color: #c7d2fe;
  font-style: italic;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4f46e5;
}

.main-title {
  font-weight: 60;
  line-height: 1.2;
  letter-spacing: -0.04em;
  margin-bottom: 3px;
  white-space: nowrap;
}

/* VisionGuard AI */
.en-text {
  font-size: 80px;
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
  font-style: italic;
}

/* 修复：英文副标题字体统一 */
.en-sub-title {
  font-size: 30px !important;
  font-family: 'Montserrat', sans-serif !important;
  font-weight: 700 !important;
  font-style: italic !important;
  letter-spacing: 1px !important;
  opacity: 0.9 !important;
}

/* 智安·视见 */
.cn-text {
  font-size: 160px;
  font-family: 'douyu', sans-serif;
  font-weight: 100;
  letter-spacing: 12px;
  opacity: 0.95;
  animation: slideInLeft 3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes slideInLeft {
  0% {
    opacity: 0;
    transform: translateX(-100px);
  }
  100% {
    opacity: 0.95;
    transform: translateX(0);
  }
}

.main-title span {
  background: linear-gradient(to right, #ffffff, #c2c7f1, #302ea4);
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
}

.sub-title {
  font-size: 18px;
  line-height: 1.6;
  color: rgba(199, 210, 254, 0.85);
  max-width: 600px;
}

.main {
  width: 100%;
  display: block;
  padding-top: 30px;
}

/* ===== 按钮 ===== */
.hero-action {
  margin-top: 40px;
  margin-left: 3px;
  pointer-events: auto;
}

.glass-play-btn {
  --mx: 50%;
  --my: 50%;
  --px: 50%;
  --py: 50%;
  --tilt-x: 0px;
  --tilt-y: 0px;

  position: relative;
  width: 210px;
  height: 64px;
  border: none;
  border-radius: 999px;
  cursor: pointer;
  overflow: hidden;
  isolation: isolate;
  outline: none;

  display: flex;
  align-items: center;
  justify-content: center;

  background: rgba(245, 248, 255, 0.24);
  backdrop-filter: blur(22px) saturate(120%);
  -webkit-backdrop-filter: blur(22px) saturate(120%);

  box-shadow:
      inset 0 1px 0 rgba(255, 255, 255, 0.95),
      inset 0 -10px 18px rgba(210, 218, 230, 0.30),
      0 18px 30px rgba(186, 195, 209, 0.22),
      0 2px 8px rgba(255, 255, 255, 0.72),
      0 0 0 1px rgba(255, 255, 255, 0.62);

  transform: translate3d(0, 0, 0) scale(1);
  transition:
      transform 0.22s ease,
      box-shadow 0.28s ease,
      filter 0.28s ease;
}

.glass-play-btn::before {
  content: "";
  position: absolute;
  inset: -2px;
  border-radius: inherit;
  pointer-events: none;
  z-index: 2;
  background:
      radial-gradient(circle at 30% 100%, rgba(140, 110, 255, 0.18), transparent 28%),
      radial-gradient(circle at 55% 100%, rgba(105, 90, 255, 0.20), transparent 26%),
      radial-gradient(circle at 78% 100%, rgba(86, 210, 255, 0.18), transparent 24%);
  filter: blur(14px);
  opacity: 0.95;
}

.glass-play-btn__base,
.glass-play-btn__inner,
.glass-play-btn__aurora,
.glass-play-btn__press,
.glass-play-btn__shine {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
}

.glass-play-btn__base {
  z-index: 0;
}

.glass-play-btn__base::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background:
      linear-gradient(180deg, rgba(255,255,255,0.88), rgba(243,246,252,0.86));
}

.glass-play-btn__base::after {
  content: "";
  position: absolute;
  inset: 1.5px;
  border-radius: inherit;
  box-shadow:
      inset 0 1px 0 rgba(255,255,255,0.92),
      inset 0 -1px 0 rgba(221,228,238,0.48);
}

.glass-play-btn__inner {
  z-index: 1;
  inset: 2px;
  border-radius: inherit;
  background:
      radial-gradient(circle at 50% -10%, rgba(255,255,255,0.95), transparent 42%),
      linear-gradient(180deg, rgba(255,255,255,0.74), rgba(241,244,250,0.74) 58%, rgba(233,238,246,0.80) 100%);
}

.glass-play-btn__aurora {
  z-index: 2;
  inset: 3px;
  border-radius: inherit;
  overflow: hidden;
}

.glass-play-btn__aurora::before {
  content: "";
  position: absolute;
  left: -12%;
  right: -12%;
  bottom: -12%;
  height: 64%;
  border-radius: 999px;
  background:
      radial-gradient(circle at 42% 72%, rgba(132, 94, 255, 0.34), transparent 18%),
      radial-gradient(circle at 54% 72%, rgba(109, 76, 255, 0.42), transparent 20%),
      radial-gradient(circle at 67% 70%, rgba(87, 124, 255, 0.38), transparent 20%),
      radial-gradient(circle at 79% 66%, rgba(76, 214, 255, 0.34), transparent 18%),
      linear-gradient(
          90deg,
          rgba(255,255,255,0) 8%,
          rgba(150, 120, 255, 0.16) 28%,
          rgba(110, 86, 255, 0.24) 48%,
          rgba(87, 124, 255, 0.22) 68%,
          rgba(76, 214, 255, 0.22) 84%,
          rgba(255,255,255,0) 96%
      );
  filter: blur(18px) saturate(130%);
  opacity: 1;
  transform: translate3d(calc(var(--tilt-x) * 0.2), calc(var(--tilt-y) * 0.16), 0);
  animation: auroraFloat 6.5s ease-in-out infinite alternate;
  transition: transform 0.18s ease;
}

.glass-play-btn__aurora::after {
  content: "";
  position: absolute;
  left: 6%;
  right: 6%;
  bottom: 8%;
  height: 26%;
  border-radius: 999px;
  background:
      linear-gradient(
          90deg,
          rgba(255,255,255,0) 0%,
          rgba(145, 116, 255, 0.18) 24%,
          rgba(112, 86, 255, 0.30) 46%,
          rgba(92, 125, 255, 0.28) 68%,
          rgba(88, 220, 255, 0.24) 100%
      );
  filter: blur(16px);
  opacity: 0.95;
  transform: translate3d(calc(var(--tilt-x) * -0.14), calc(var(--tilt-y) * -0.1), 0);
  animation: auroraFloat2 7.8s ease-in-out infinite alternate;
  transition: transform 0.18s ease;
}

.glass-play-btn__press {
  z-index: 3;
  inset: 3px;
  border-radius: inherit;
  overflow: hidden;
}

.glass-play-btn__press::before {
  content: "";
  position: absolute;
  left: var(--px);
  top: var(--py);
  width: 132px;
  height: 132px;
  transform: translate(-50%, -50%) scale(0.15);
  border-radius: 50%;
  background:
      radial-gradient(
          circle,
          rgba(255,255,255,0.30) 0%,
          rgba(170, 136, 255, 0.24) 22%,
          rgba(112, 86, 255, 0.24) 40%,
          rgba(92, 125, 255, 0.18) 56%,
          rgba(88, 220, 255, 0.14) 68%,
          rgba(255,255,255,0) 82%
      );
  filter: blur(11px);
  opacity: 0;
}

.glass-play-btn__press::after {
  content: "";
  position: absolute;
  left: var(--px);
  top: var(--py);
  width: 180px;
  height: 180px;
  transform: translate(-50%, -50%) scale(0.12);
  border-radius: 50%;
  background:
      radial-gradient(
          circle,
          rgba(255,255,255,0) 0%,
          rgba(255,255,255,0) 24%,
          rgba(120, 100, 255, 0.22) 40%,
          rgba(96, 128, 255, 0.16) 54%,
          rgba(88, 220, 255, 0.12) 64%,
          rgba(255,255,255,0) 76%
      );
  filter: blur(6px);
  opacity: 0;
}

.glass-play-btn__shine {
  z-index: 4;
}

.glass-play-btn__shine::before {
  content: "";
  position: absolute;
  top: 6px;
  left: 8%;
  width: 84%;
  height: 38%;
  border-radius: 999px;
  background: linear-gradient(
      180deg,
      rgba(255,255,255,0.84),
      rgba(255,255,255,0.18) 58%,
      transparent
  );
  filter: blur(2px);
}

.glass-play-btn__shine::after {
  content: "";
  position: absolute;
  top: -120%;
  left: -18%;
  width: 26%;
  height: 320%;
  background: linear-gradient(
      90deg,
      transparent,
      rgba(255,255,255,0.10),
      rgba(255,255,255,0.38),
      rgba(255,255,255,0.12),
      transparent
  );
  transform: rotate(16deg);
  filter: blur(2px);
  animation: glassSweep 5.6s linear infinite;
}

.glass-play-btn__text {
  position: relative;
  z-index: 5;
  font-size: 19px;
  font-weight: 700;
  font-family: 'Montserrat', sans-serif;
  font-style: italic;
  letter-spacing: 0.01em;
  color: #55596a;
  text-shadow:
      0 1px 0 rgba(255,255,255,0.75),
      0 0 12px rgba(114, 108, 255, 0.12);
  transition: transform 0.22s ease, color 0.22s ease;
}

.glass-play-btn.hovering,
.glass-play-btn:hover {
  box-shadow:
      inset 0 1px 0 rgba(255, 255, 255, 0.98),
      inset 0 -10px 18px rgba(206, 216, 232, 0.34),
      0 22px 34px rgba(186, 195, 209, 0.24),
      0 4px 12px rgba(255, 255, 255, 0.80),
      0 0 0 1px rgba(255, 255, 255, 0.72),
      0 0 26px rgba(103, 109, 255, 0.12),
      0 0 42px rgba(83, 190, 255, 0.08);
  filter: brightness(1.03);
}

.glass-play-btn.hovering .glass-play-btn__text,
.glass-play-btn:hover .glass-play-btn__text {
  transform: scale(1.012);
  color: #4d5262;
}

.glass-play-btn:active {
  transform: translate3d(0, 1px, 0) scale(0.985) !important;
  transition: transform 0.08s ease;
}

.glass-play-btn.pressing .glass-play-btn__press::before {
  animation: pressBloom 0.62s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.glass-play-btn.pressing .glass-play-btn__press::after {
  animation: pressDisplace 0.72s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.glass-play-btn.pressing .glass-play-btn__aurora::before {
  animation:
      auroraFloat 6.5s ease-in-out infinite alternate,
      auroraPush 0.72s cubic-bezier(0.2, 0.78, 0.2, 1);
}

.glass-play-btn.pressing .glass-play-btn__aurora::after {
  animation:
      auroraFloat2 7.8s ease-in-out infinite alternate,
      auroraPush2 0.72s cubic-bezier(0.2, 0.78, 0.2, 1);
}

.glass-play-btn:focus-visible {
  box-shadow:
      inset 0 1px 0 rgba(255, 255, 255, 0.98),
      inset 0 -10px 18px rgba(206, 216, 232, 0.34),
      0 0 0 1px rgba(255, 255, 255, 0.78),
      0 0 0 4px rgba(255,255,255,0.28),
      0 18px 30px rgba(186, 195, 209, 0.22);
}

.glass-ripple {
  position: absolute;
  z-index: 3;
  border-radius: 50%;
  pointer-events: none;
  transform: translate(-50%, -50%) scale(0.14);
  opacity: 0;
  background:
      radial-gradient(
          circle,
          rgba(255,255,255,0.18) 0%,
          rgba(168, 138, 255, 0.18) 22%,
          rgba(112, 86, 255, 0.22) 40%,
          rgba(92, 125, 255, 0.18) 56%,
          rgba(88, 220, 255, 0.14) 68%,
          rgba(255,255,255,0) 80%
      );
  filter: blur(12px);
  mix-blend-mode: screen;
  animation: glassRipple var(--ripple-duration, 760ms) cubic-bezier(0.18, 0.78, 0.2, 1) forwards;
}

/* ===== 文章 ===== */
article {
  width: 100%;
  padding: 0 180px;
  margin-bottom: 50px;
}

article h1 {
  font-size: 100px;
  line-height: 1.2;
  margin-bottom: 12px;
  font-family: 'douyu', sans-serif !important;
}

article h2 {
  font-size: 30px;
  font-weight: 500;
}

/* ========== 三张图片展示样式 ========== */
.triple-image-section {
  width: 100%;
  padding: 0 180px 120px;
  display: flex;
  gap: 30px;
  justify-content: center;
  align-items: stretch;
}

.triple-img-box {
  flex: 1;
  height: 520px;
  border-radius: 24px;
  overflow: hidden;
  background: #ffffff;
  box-shadow: 0 10px 50px rgba(0, 0, 0, 0.1);
  transition: 0.4s;
  display: flex;
  flex-direction: column;
  padding: 20px;
  font-family: 'Nunito', sans-serif; /* 圆润字体 */
}

/* 卡片图片区域 */
.card-image {
  width: 100%;
  height: 320px;
  border-radius: 16px;
  overflow: hidden;
}
.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: 0.5s;
}

/* 卡片文字区域 */
.card-text {
  padding: 28px 10px 20px;
  text-align: center;
}
.card-text h3 {
  font-size: 26px;
  font-weight: 700;
  margin-bottom: 10px;
  color: #1f2937;
  font-family: 'Nunito', sans-serif;
}
.card-text p {
  font-size: 17px;
  color: #6b7280;
  line-height: 1.5;
  font-family: 'Nunito', sans-serif;
}

.triple-img-box:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}
.triple-img-box:hover .card-image img {
  transform: scale(1.08);
}

.fade-up-item {
  opacity: 0;
  transform: translateY(60px) scale(0.95);
  transition: 0.5s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.fade-up-active {
  opacity: 1;
  transform: translateY(0) scale(1);
}

#carousel-container {
  width: 100%;
  height: 80vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: transparent;
  margin: 100px 0;
}

#click-section {
  width: 35%;
  height: 100%;
  padding: 20px 0;
  position: relative;
  background: transparent;
}

#drawerboxes {
  margin-left: 22%;
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
  gap: 20px;
}

.drawerbox {
  height: calc(100% / 5.5);
  width: 70%;
  position: relative;
  z-index: 100;
  transform: translateX(-70%);
  transition: transform .5s ease-in-out;
}

.drawerbox.active {
  transform: translateX(0);
}

.drawer-btn {
  width: 100%;
  height: 100%;
  font: 800 30px '';
background: linear-gradient(170deg, #f9f9f9, #ffffff,#e4f1fc,#afd2f0);
  border: none;
  transition: background-color .5s ease-in-out;
  color: #000000;
  cursor: pointer;
}

.drawer-btn.active {
  background-image: url('@/assets/lunbo.jpg');
  background-size: cover;
  color: rgb(0, 0, 0);
}

.drawer-head {
  position: absolute;
  color: rgb(255, 255, 255);
  font-size: 150px;
  font-weight: 700;
  right: -28px;
  top: calc(50% - 100px);
  text-shadow: 8px -2px 8px rgba(0, 0, 0, 0.323);
}

#slide-section {
  position: relative;
  height: 100%;
  width: 65%;
  display: flex;
  justify-content: center;
  padding: 0 40px;
  background: transparent;
  backdrop-filter: none;
}

#slide-bar {
  position: absolute;
  top: 5%;
  left: 50px;
  height: 90%;
  width: 1px;
  background-color: rgb(223, 223, 223);
}

#bar {
  position: absolute;
  height: calc(100% / 4);
  width: 5px;
  top: 0;
  left: -1.2px;
  background-color: rgba(100, 103, 116, 0.715);
  transition: transform .5s ease-in-out;
}

#card-section {
  height: 100%;
  width: 80%;
  overflow: hidden;
}

.card {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  padding: 3% 0;
  color: white;
  font-size: 30px;
  transition: transform .5s ease-in-out;
}

.card-small-title {
  font-size: 24px;
  font-weight: 60;
  padding-bottom: 8px;
  color: rgb(89, 54, 54);
}

.card-title {
  font-size: 52px;
  font-weight: 700;
  padding-bottom: 20px;
  color: rgb(33, 33, 34);
}

.card-content {
  font-size: 20px;
  font-weight: 400;
  color: rgba(9, 14, 34, 0.653);
  margin-bottom: 30px;
}

.card-img {
  width: 100%;
  height: 430px;
  overflow: hidden;
  border-radius: 20px;
}

.card-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

:deep(html), :deep(body), :deep(#app) {
  margin: 0 !important;
  padding: 0 !important;
  overflow: visible !important;
  height: auto !important;
}

/* ===== 按钮动画 ===== */
@keyframes auroraFloat {
  0% {
    transform: translate3d(calc(var(--tilt-x) * 0.18 - 1%), calc(var(--tilt-y) * 0.18), 0) scale(1);
  }
  100% {
    transform: translate3d(calc(var(--tilt-x) * 0.18 + 1%), calc(var(--tilt-y) * 0.18 + 1%), 0) scale(1.06);
  }
}

@keyframes auroraFloat2 {
  0% {
    transform: translate3d(calc(var(--tilt-x) * -0.12 + 1%), calc(var(--tilt-y) * -0.12), 0) scale(1);
  }
  100% {
    transform: translate3d(calc(var(--tilt-x) * -0.12 - 1%), calc(var(--tilt-y) * -0.12 + 1%), 0) scale(1.05);
  }
}

@keyframes glassSweep {
  0% {
    transform: translateX(-180%) rotate(16deg);
    opacity: 0;
  }
  18% {
    opacity: 1;
  }
  42% {
    opacity: 1;
  }
  100% {
    transform: translateX(320%) rotate(16deg);
    opacity: 0;
  }
}

@keyframes pressBloom {
  0% {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.15);
  }
  18% {
    opacity: 1;
  }
  100% {
    opacity: 0;
    transform: translate(-50%, -50%) scale(1.18);
  }
}

@keyframes pressDisplace {
  0% {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.12);
  }
  24% {
    opacity: 0.85;
  }
  100% {
    opacity: 0;
    transform: translate(-50%, -50%) scale(1.45);
  }
}

@keyframes auroraPush {
  0% {
    filter: blur(16px) saturate(115%);
  }
  26% {
    filter: blur(10px) saturate(122%);
  }
  100% {
    filter: blur(16px) saturate(115%);
  }
}

@keyframes auroraPush2 {
  0% {
    filter: blur(14px);
    opacity: 0.7;
  }
  28% {
    filter: blur(8px);
    opacity: 0.9;
  }
  100% {
    filter: blur(14px);
    opacity: 0.7;
  }
}

@keyframes glassRipple {
  0% {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.14);
  }
  18% {
    opacity: 0.72;
  }
  100% {
    opacity: 0;
    transform: translate(-50%, -50%) scale(var(--ripple-scale));
  }
}
</style>