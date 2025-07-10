<template>
  <div class="console-layout">
    <main class="console-main face-recognition-main">
      <div class="tab-title">
        <h2>人脸识别</h2>
        <div class="tab-title-underline"></div>
      </div>
      <div v-if="!hasPermission" class="permission-tip">
        <p>正在申请摄像头权限...</p>
      </div>
      <div v-else class="video-wrapper">
        <video ref="videoRef" autoplay playsinline class="video-preview"></video>
      </div>
      <div class="tip-text">请正对摄像头，保持面部居中，并确保环境光线充足</div>
      <button class="action-button" @click="startCapture" :disabled="recording">
        {{ recording ? '采集中...' : '开始采集' }}
      </button>
    </main>
  </div>
</template>

<script setup>
import useFaceRecognition from '../viewmodels/FaceRecognitionViewModel'

const { videoRef, hasPermission, recording, startCapture } = useFaceRecognition()
</script>

<style scoped>
.console-layout {
  display: flex;
  height: calc(100vh - 92px);
}
.console-main {
  flex: 1;
  padding: 40px 56px;
  background: #f8f9fa;
  box-shadow: 0 4px 24px rgba(79,55,138,0.10), 0 1.5px 6px rgba(0,0,0,0.08);
}
.face-recognition-main {
  display: flex;
  flex-direction: column;
}
.permission-tip {
  font-size: 18px;
  color: #888;
}
.video-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  background: transparent;
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
.tab-title {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-bottom: 24px;
}
.tab-title h2 {
  font-size: 28px;
  color: #333;
  margin: 0;
}
.tab-title-underline {
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, #4F378A, #9B7EBE);
  border-radius: 2px;
  margin-top: 8px;
}
.tip-text {
  margin-top: 16px;
  font-size: 16px;
  color: #666;
  text-align: center;
}
.action-button {
  margin-top: 24px;
  padding: 12px 24px;
  background: #4F378A;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}
</style>
