<template>
  <div class="face-upload-layout">
    <div v-if="!hasPermission" class="permission-tip">
      <p>正在申请摄像头权限...</p>
    </div>
    <div v-else class="video-wrapper">
      <video ref="videoRef" autoplay playsinline class="video-preview"></video>
    </div>
    <div class="controls">
      <button class="upload-button" @click="capturePhoto">拍照</button>
      <div v-if="capturedUrl" class="upload-preview">
        <img :src="capturedUrl" alt="拍照预览" />
      </div>
      <button v-if="capturedBlob" class="upload-button" @click="onUpload">上传</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'

const videoRef = ref(null)
const hasPermission = ref(false)
let stream = null
const capturedBlob = ref(null)
const capturedUrl = ref('')

function capturePhoto() {
  const video = videoRef.value
  if (!video) return
  const canvas = document.createElement('canvas')
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  const ctx = canvas.getContext('2d')
  ctx && ctx.drawImage(video, 0, 0)
  canvas.toBlob(blob => {
    capturedBlob.value = blob
    capturedUrl.value = URL.createObjectURL(blob)
  }, 'image/jpeg')
}

function onUpload() {
  if (!capturedBlob.value) return
  // TODO: 上传拍摄的照片到服务器
  alert('上传人脸数据功能待实现')
}

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
  }
})

onBeforeUnmount(() => {
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
  }
})
</script>

<style scoped>
.face-upload-layout {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.permission-tip {
  font-size: 18px;
  color: #888;
  margin-bottom: 16px;
}
.video-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  background: transparent;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.15);
  padding: 24px;
  margin-bottom: 16px;
}
.video-preview {
  width: 360px;
  height: 270px;
  object-fit: cover;
  border-radius: 12px;
  background: #000;
}
.controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.upload-button {
  padding: 8px 16px;
  background: #4F378A;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.upload-preview img {
  max-width: 100%;
  max-height: 200px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
</style>
