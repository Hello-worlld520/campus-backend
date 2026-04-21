<!-- <script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'

const videoRef = ref(null)
// 假设你用的是某种播放器实例
let player = null 

onMounted(() => {
  // 初始化播放器逻辑...
})

onBeforeUnmount(() => {
  // 专业优化：在这里释放内存，防止长时间监控网页卡死
  if (player) {
    player.dispose() 
    console.log('视频资源已释放')
  }
})
</script>

<template>
  <div class="video-container">
    <video ref="videoRef" autoplay muted></video>
  </div>
</template> -->