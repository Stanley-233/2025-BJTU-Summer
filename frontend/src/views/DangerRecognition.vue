<template>
  <div class="danger-layout">
    <!-- 侧边栏模型选择 -->
    <aside class="model-sidebar">
      <div
        v-for="model in models"
        :key="model"
        :class="['model-item', selectedModel === model ? 'active' : '']"
        @click="selectModel(model)"
      >
        {{ model }}
      </div>
    </aside>
    <!-- 主内容区 -->
    <main class="danger-main">
      <div class="danger-card">
        <!-- 图片显示模块 -->
        <div class="image-preview">
          <template v-if="imageSrc">
            <img :src="imageSrc" alt="占位图片" />
          </template>
          <template v-else>
            <p>尚无结果</p>
          </template>
        </div>
        <!-- 文字显示区域 -->
        <div class="text-display">
          <template v-if="placeholderText">
            <h3>{{ selectedModel }}</h3>
            <p>{{ placeholderText }}</p>
          </template>
          <template v-else>
            <p>尚无结果</p>
          </template>
        </div>
      </div>
      <!-- 上传视频按钮 -->
      <div class="upload-area" @dragover.prevent @drop.prevent="handleFileDrop">
        <template v-if="thumbnailSrc">
          <img :src="thumbnailSrc" alt="视频缩略图" class="thumbnail" />
        </template>
        <template v-else>
          <p>拖拽文件到此处上传，或点击下方按钮选择文件</p>
          <button class="upload-btn" @click="uploadVideo">上传视频</button>
        </template>
        <input type="file" ref="fileInput" accept="video/*" style="display: none" @change="handleFileChange" />
      </div>
      <!-- 悬浮按钮 -->
      <button class="floating-button" @click="onFloatingButtonClick">
        <svg width="36" height="36" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
          <path d="M7 5C7 3.89543 8.11929 3.18415 9.08359 3.72361L28 15.5C28.9643 16.0395 28.9643 17.9605 28 18.5L9.08359 30.2764C8.11929 30.8159 7 30.1046 7 29V5Z" fill="white" transform="translate(1,0)"/>
        </svg>
      </button>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const models = ['模型A', '模型B', '模型C'];
const selectedModel = ref(models[0]);
const placeholderText = ref('');
const imageSrc = ref(''); // 默认无图片
const fileInput = ref(null);
const thumbnailSrc = ref('');

function selectModel(model) {
  selectedModel.value = model;
}

function uploadVideo() {
  fileInput.value.click();
}

function handleFileChange(event) {
  const file = event.target.files[0];
  if (file) {
    const filePath = URL.createObjectURL(file);
    generateThumbnail(filePath);
    alert('视频已上传，文件路径已保存');
  }
}

function handleFileDrop(event) {
  const file = event.dataTransfer.files[0];
  if (file) {
    const filePath = URL.createObjectURL(file);
    try {
      generateThumbnail(filePath);
      alert('视频已上传，文件路径已保存');
    } catch (error) {
      console.error('文件处理失败:', error);
      alert('文件处理失败，请重试。');
    }
  } else {
    alert('未检测到文件，请重试。');
  }
}

function generateThumbnail(filePath) {
  const video = document.createElement('video');
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');

  video.src = filePath;
  video.crossOrigin = "anonymous"; // 防止跨域问题
  video.load();

  video.addEventListener('loadedmetadata', () => {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    video.currentTime = 0;
  });

  video.addEventListener('seeked', () => {
    try {
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      thumbnailSrc.value = canvas.toDataURL('image/png');
    } catch (error) {
      console.error('生成缩略图失败:', error);
      alert('生成缩略图失败，请检查视频文件是否有效。');
    } finally {
      URL.revokeObjectURL(video.src);
    }
  });

  video.addEventListener('error', () => {
    console.error('视频加载失败');
    alert('视频加载失败，请检查文件格式是否正确。');
  });
}

function onFloatingButtonClick() {
  // TODO: 这里预留点击事件接口
  alert('悬浮按钮被点击！');
}
</script>

<style scoped>
.danger-layout {
  display: flex;
  height: calc(100vh - 92px);
  min-height: 400px;
  margin-bottom: 20px;
}

.model-sidebar {
  width: 140px;
  background: #f7f7fa;
  border-right: 2px solid #ede7f6;
  box-shadow: 2px 0 8px rgba(79, 55, 138, 0.04);
  display: flex;
  flex-direction: column;
}

.model-item {
  padding: 16px 0;
  text-align: center;
  font-size: 16px;
  color: #666;
  cursor: pointer;
  border-left: 4px solid transparent;
  transition: background 0.2s, color 0.2s, border-color 0.2s;
}

.model-item.active {
  background: #ede7f6;
  color: #4F378A;
  border-left: 4px solid #4F378A;
  font-weight: 600;
}

.danger-main {
  flex: 1;
  padding: 40px 56px 32px 56px;
  background: #f8f9fa;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: stretch;
}

.danger-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(79, 55, 138, 0.06);
  padding: 24px 32px;
  margin-bottom: 32px;
  display: flex;
  gap: 24px;
}

.image-preview {
  flex: 3;
  background: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  overflow: hidden;
  color: #fff;
  font-size: 16px;
  min-width: 180px;
  min-height: 180px;
}

.image-preview img {
  width: auto;
  height: auto;
  max-width: 100%;
  max-height: 240px;
  display: block;
  margin: auto;
}

.text-display {
  flex: 2;
  background: #f9f9f9;
  padding: 24px 16px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
  min-height: 180px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #666;
}

.text-display h3 {
  margin: 0 0 8px;
}

.text-display p {
  margin: 0;
}

.upload-area {
  margin-top: 0;
  padding: 16px;
  border: 2px dashed #007bff;
  border-radius: 8px;
  text-align: center;
  color: #666;
  background-color: #f9f9f9;
  transition: background-color 0.3s;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  margin-bottom: 24px;
  height: 200px;
  position: relative;
}

.upload-area:hover {
  background-color: #e0e0e0;
}

.upload-area p {
  margin: 0 0 8px;
}

.upload-btn {
  margin-top: 12px;
  padding: 8px 24px;
  font-size: 1em;
  border: none;
  border-radius: 4px;
  background: #ede7f6;
  color: #4F378A;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.upload-btn:hover {
  background: #d1c4e9;
}

.thumbnail {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  display: block;
  margin: auto;
  border-radius: 8px;
  object-fit: contain;
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
}

.floating-button {
  position: fixed;
  right: 32px;
  bottom: 32px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #b39ddb;
  color: #fff;
  border: none;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  font-size: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 1000;
  transition: background 0.3s;
}
.floating-button:hover {
  background: #4F378A;
  color: #fff;
}
</style>
