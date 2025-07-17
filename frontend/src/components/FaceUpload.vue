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
import {ref, onMounted, onBeforeUnmount, nextTick, inject} from 'vue'
import { DefaultApi, Configuration } from '../api/generated'
import { blobToBase64 } from '../util/base64'
import CryptoJS from "crypto-js";
import {getUserInfo} from "@/viewmodels/VerifyInfoViewModel.js";

const showGlobalBubble = inject('showGlobalBubble')
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

async function onUpload() {
  if (!capturedBlob.value) return
  try {
    // convert blob to base64 string
    const dataUrl = await blobToBase64(capturedBlob.value)
    // strip prefix "data:*/*;base64,"
    let base64 = dataUrl.split(',')[1]
    base64 = CryptoJS.AES.encrypt(base64, 'BrPz0VgQzNmhw1KmHfEyUFu1DHnq0schBijdSm0P_K0=').toString();
    // call upload API
    const api = new DefaultApi(new Configuration({
      basePath: 'http://127.0.0.1:8000',
      accessToken: sessionStorage.getItem('token') ? () => sessionStorage.getItem('token') : undefined,
    }))
    const userInfo = await getUserInfo()
    if (userInfo == null) {
      showGlobalBubble ? showGlobalBubble('人脸注册失败，请重试') : alert('人脸注册失败，请重试')
      return
    }
    if( userInfo.face_data !== null) {
      await api.updateFaceDataUpdateFacePut({image: base64})
    }
    else {
      await api.postFaceDataPostFacePost({image: base64})
    }
    showGlobalBubble ? showGlobalBubble('人脸注册成功') : alert('人脸注册成功')
  } catch (error) {
    console.error(error)
    showGlobalBubble ? showGlobalBubble('人脸注册失败，请重试') : alert('人脸注册失败，请重试')
  }
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
