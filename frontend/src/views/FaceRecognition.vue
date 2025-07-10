<template>
  <div class="face-recognition-container">
    <div v-if="!hasPermission" class="permission-tip">
      <p>正在申请摄像头权限...</p>
    </div>
    <div v-else class="video-wrapper">
      <video ref="videoRef" autoplay playsinline class="video-preview"></video>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'

const videoRef = ref(null)
const hasPermission = ref(false)
let stream = null

onMounted(async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true })
    hasPermission.value = true
    await nextTick()
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      videoRef.value.play && videoRef.value.play()
    }
  } catch (e) {
    hasPermission.value = false
    alert('无法获取摄像头权限，请检查浏览器设置。')
  }
})

onBeforeUnmount(() => {
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
  }
})
</script>

<style scoped>
.face-recognition-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80vh;
}
.video-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  background: #222;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.15);
  padding: 24px;
}
.video-preview {
  width: 480px;
  height: 360px;
  object-fit: cover;
  border-radius: 12px;
  background: #000;
}
.permission-tip {
  font-size: 18px;
  color: #888;
}
</style>
