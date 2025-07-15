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
      <!-- 添加过渡动画 -->
      <transition name="fade">
        <div class="danger-card" key="danger-card">
          <!-- 图片显示模块 -->
          <div class="image-preview">
            <template v-if="isLoading">
              <p>正在推理中</p>
            </template>
            <template v-else-if="mediaSrc">
              <!-- show result thumbnail and play on click -->
              <img :src="resultThumbnailSrc" alt="结果缩略图" class="thumbnail" @click="playVideo" />
            </template>
            <template v-else>
              <p>尚无结果</p>
            </template>
          </div>
          <!-- 文字显示区域 -->
          <div class="text-display">
            <template v-if="isLoading">
              <p>正在推理中</p>
            </template>
            <template v-else-if="Array.isArray(dangerList) ? dangerList.length > 0 : (dangerList && dangerList.value && dangerList.value.length > 0)">
              <h3>{{ selectedModel }} 检测结果</h3>
              <ul style="text-align:left;">
                <li v-for="(danger, idx) in (Array.isArray(dangerList) ? dangerList : dangerList.value)" :key="idx">
                  危险类型: {{ dangerTypeMap[danger.type] ?? danger.type }}，置信度: {{ (danger.confidence * 100).toFixed(1) }}%
                </li>
              </ul>
            </template>
            <template v-else>
              <p>尚无结果</p>
            </template>
          </div>
        </div>
      </transition>
      <!-- 上传视频按钮 -->
      <div class="upload-area" @dragover.prevent @drop.prevent="handleFileDrop">
        <template v-if="thumbnailSrc">
          <img :src="thumbnailSrc" alt="视频缩略图" @click="uploadVideo" class="thumbnail" />
        </template>
        <template v-else>
          <p>拖拽文件到此处上传，或点击下方按钮选择文件</p>
          <button class="upload-btn" @click="uploadVideo">上传视频</button>
        </template>
        <input type="file" ref="fileInput" accept="video/*" style="display: none" @change="handleFileChange" />
      </div>
      <!-- 推理按钮，移到主界面底部，文本更改 -->
      <!-- 普通按钮替代悬浮按钮 -->
      <button class="start-btn" @click="onFloatingButtonClick">
        开始推理
      </button>
    </main>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue';
import { requestVideoDangerDetect } from '../viewmodels/DangerDetectModel';

const models = ['yolov8n', 'yolo11n', 'yolo12n', 'yolo12s'];
const selectedModel = ref(models[0]);
const mediaSrc = ref('');
const dangerList = ref([]);
const isLoading = ref(false);
const fileInput = ref(null);
const thumbnailSrc = ref('');
const videoFile = ref(null);
const showGlobalBubble = inject('showGlobalBubble');
const resultThumbnailSrc = ref('');
const dangerTypeMap = {
  0: '🚧纵向',
  1: '🚧横向',
  2: '🚧龟裂',
  3: '🚧坑洼',
  4: '🚧补丁'
};

function selectModel(model) {
  selectedModel.value = model;
  // 切换模型时清空结果
  isLoading.value = false;
  mediaSrc.value = '';
  dangerList.value = [];
}

function uploadVideo() {
  // 清空之前的选中文件，以便可以重新选择同一文件或更换文件
  if (fileInput.value) fileInput.value.value = null;
  fileInput.value.click();
}

function handleFileChange(event) {
  const file = event.target.files[0];
  if (file) {
    videoFile.value = file; // 保存文件对象
    generateThumbnail(URL.createObjectURL(file));
    showGlobalBubble && showGlobalBubble('视频已上传，文件路径已保存');
  }
}

function handleFileDrop(event) {
  const file = event.dataTransfer.files[0];
  if (file) {
    videoFile.value = file; // 保存文件对象
    try {
      generateThumbnail(URL.createObjectURL(file));
      showGlobalBubble && showGlobalBubble('视频已上传，文件路径已保存');
    } catch (error) {
      showGlobalBubble && showGlobalBubble('文件处理失败，请重试。');
    }
  } else {
    showGlobalBubble && showGlobalBubble('未检测到文件，请重试。');
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
      showGlobalBubble && showGlobalBubble('生成缩略图失败，请检查视频文件是否有效。');
    } finally {
      URL.revokeObjectURL(video.src);
    }
  });

  video.addEventListener('error', () => {
    showGlobalBubble && showGlobalBubble('视频加载失败，请检查文件格式是否正确。');
  });
}

// play video in new window
function playVideo() {
  const win = window.open('', '_blank');
  if (!win) return;
  win.document.write(`<html lang="en"><body style="margin:0"><video src="${mediaSrc.value}" controls autoplay style="width:100%;height:100%;"></video></body></html>`);
}

function onFloatingButtonClick() {
  if (!videoFile.value) {
    showGlobalBubble && showGlobalBubble('请先上传视频文件');
    return;
  }
  // 开始推理，清空并显示loading
  isLoading.value = true;
  mediaSrc.value = '';
  dangerList.value = [];

  const reader = new FileReader();
  reader.onloadend = () => {
    const base64 = String(reader.result).split(',')[1];
    requestVideoDangerDetect(base64, selectedModel.value, (msg) => {
      showGlobalBubble && showGlobalBubble('检测失败: ' + msg);
    })
      .then((result) => {
        if (result) {
          mediaSrc.value = 'data:video/mp4;base64,' + result.predicted_image;
          // generate thumbnail for result video
          generateResultThumbnail(mediaSrc.value);
          dangerList.value = (result.dangers || []).map(item => ({ type: item.type, confidence: item.confidence }));
        }
      })
      .catch(err => {
        showGlobalBubble && showGlobalBubble('视频处理失败: ' + err);
      })
      .finally(() => {
        isLoading.value = false;
      });
  };
  reader.onerror = (err) => {
    showGlobalBubble && showGlobalBubble('读取视频文件失败: ' + err);
    isLoading.value = false;
  };
  reader.readAsDataURL(videoFile.value);
}

// generate thumbnail for result video
function generateResultThumbnail(filePath) {
  const video = document.createElement('video');
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  video.src = filePath;
  video.crossOrigin = 'anonymous';
  video.load();
  video.addEventListener('loadedmetadata', () => {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    video.currentTime = 0;
  });
  video.addEventListener('seeked', () => {
    try { ctx.drawImage(video, 0, 0, canvas.width, canvas.height); resultThumbnailSrc.value = canvas.toDataURL('image/png'); }
    catch {} finally { URL.revokeObjectURL(video.src); }
  });
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
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  overflow: hidden;
  color: #fff;
  font-size: 16px;
  min-width: 180px;
  min-height: 180px;
  max-width: 400px;
  max-height: 300px;
}

.image-preview img {
  width: 100%;
  height: auto;
  object-fit: contain;
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

/* 更换视频按钮可复用upload-btn样式，无需额外样式 */

/* 普通推理按钮样式 */
.start-btn {
  align-self: center;
  margin-top: 16px;
  padding: 12px 24px;
  font-size: 16px;
  border-radius: 24px;
  background: #b39ddb;
  color: #fff;
  border: none;
  cursor: pointer;
  transition: background 0.3s;
}
.start-btn:hover {
  background: #4F378A;
  color: #fff;
}

/* fade transition */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* .thumbnail styles */
.thumbnail {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
  cursor: pointer;
}
</style>
