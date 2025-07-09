<template>
  <div class="face-recognition-page">
    <div class="face-recognition-title">人脸识别</div>
    <div class="face-recognition-content">
      <template v-if="!showCamera">
        <div class="face-recognition-placeholder">
          <span>请上传图片或启用摄像头进行人脸识别</span>
        </div>
        <select v-if="cameraDevices.length > 1" v-model="selectedDeviceId" class="camera-select">
          <option v-for="device in cameraDevices" :key="device.deviceId" :value="device.deviceId">
            {{ device.label || `摄像头${cameraDevices.indexOf(device) + 1}` }}
          </option>
        </select>
        <button class="camera-btn" @click="requestCamera">申请摄像头权限</button>
        <div v-if="cameraError" class="camera-error">{{ cameraError }}</div>
      </template>
      <template v-else>
        <video
          ref="videoRef"
          class="camera-preview"
          autoplay
          playsinline
          width="360"
          height="270"
          style="object-fit: cover; background: #000; border-radius: 8px;"
        ></video>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'

const videoRef = ref(null)
const cameraError = ref('')
const showCamera = ref(false)
const cameraDevices = ref([])
const selectedDeviceId = ref('')
let stream = null

const router = useRouter()

function stopCamera() {
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
    stream = null
  }
  showCamera.value = false
}

async function getCameraDevices() {
  const devices = await navigator.mediaDevices.enumerateDevices()
  cameraDevices.value = devices.filter(d => d.kind === 'videoinput')
  if (cameraDevices.value.length > 0 && !selectedDeviceId.value) {
    selectedDeviceId.value = cameraDevices.value[0].deviceId
  }
}

async function requestCamera() {
  cameraError.value = ''
  if (showCamera.value && stream) {
    // 已有权限且已打开摄像头，直接显示
    return
  }
  try {
    const constraints = selectedDeviceId.value
      ? { video: { deviceId: { exact: selectedDeviceId.value } } }
      : { video: { facingMode: 'user' } }
    stream = await navigator.mediaDevices.getUserMedia(constraints)
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      // videoRef.value.load() // 通常不需要
      setTimeout(() => {
        videoRef.value.play()
      }, 100)
    }
    showCamera.value = true
  } catch (err) {
    cameraError.value = '无法访问摄像头：' + (err.message || err)
    showCamera.value = false
  }
}

// 页面挂载时自动检测是否已有摄像头权限
onMounted(async () => {
  await getCameraDevices()
  try {
    const devices = await navigator.mediaDevices.enumerateDevices()
    const hasVideoInput = devices.some(d => d.kind === 'videoinput')
    if (hasVideoInput) {
      // 检查权限状态
      if (navigator.permissions) {
        try {
          const status = await navigator.permissions.query({ name: 'camera' })
          if (status.state === 'granted') {
            await requestCamera()
          }
        } catch {}
      }
    }
  } catch {}
})

// 路由切换时停止摄像头
router.beforeEach((to, from, next) => {
  stopCamera()
  next()
})

onBeforeUnmount(() => {
  stopCamera()
})
</script>

<style scoped>
.face-recognition-page {
  min-height: 100vh;
  background: #f8f9fa;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding-top: 60px;
}
.face-recognition-title {
  font-size: 2em;
  font-weight: bold;
  color: #4F378A;
  margin-bottom: 32px;
}
.face-recognition-content {
  width: 420px;
  min-height: 320px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(79,55,138,0.10);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}
.face-recognition-placeholder {
  color: #bbb;
  font-size: 1.1em;
}
.camera-select {
  margin-top: 16px;
  padding: 8px;
  font-size: 1em;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: #fff;
  width: 100%;
  max-width: 300px;
}
.camera-btn {
  margin-top: 24px;
  padding: 8px 24px;
  font-size: 1em;
  background: #4F378A;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}
.camera-btn:hover {
  background: #6c4bb6;
}
.camera-error {
  color: #d32f2f;
  margin-top: 12px;
  font-size: 0.98em;
}
.camera-preview {
  margin-top: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(79,55,138,0.10);
  background: #000;
}
</style>
