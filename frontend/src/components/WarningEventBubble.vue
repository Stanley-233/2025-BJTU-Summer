<template>
  <transition name="fade">
    <div v-if="visible" class="warning-bubble">
      <div class="header">
        <span class="title">安全告警</span>
        <button class="close-btn" @click="hide">×</button>
      </div>
      <div class="body">
        <p><strong>类型：</strong>{{ typeIconMap[eventData.event_type] }}{{ LogType[eventData.event_type] }}</p>
        <p><strong>描述：</strong>{{ eventData.description }}</p>
        <p><strong>时间：</strong>{{ eventData.timestamp }}</p>
        <p><strong>等级：</strong>{{ LogLevel[eventData.log_level] }}</p>
        <p v-if="eventData.link_username"><strong>用户：</strong>{{ eventData.link_username }}</p>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, defineExpose } from 'vue';

// 引入类型和等级映射
const LogType = { 0: '非法用户', 1: '人脸欺诈', 2: '道路安全', 3: '操作事件' }
const typeIconMap = { 0: '🔒', 1: '😡', 2: '🚧', 3: '📝' }
const LogLevel = { 0: '信息', 1: '警告', 2: '错误' }

const visible = ref(false);
const eventData = ref({
  event_type: '',
  description: '',
  timestamp: '',
  log_level: '',
  link_username: ''
});

function show(event) {
  eventData.value = event;
  visible.value = true;
}

function hide() {
  visible.value = false;
}

defineExpose({ show, hide });
</script>

<style scoped>
.warning-bubble {
  position: fixed;
  top: 16px;
  right: 16px;
  background: #fff2f0;
  border: 1px solid #ffa39e;
  border-radius: 4px;
  width: 300px;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  z-index: 2000;
}
.warning-bubble .header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.warning-bubble .title {
  font-weight: bold;
  color: #cf1322;
}
.warning-bubble .close-btn {
  background: transparent;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #cf1322;
}
.warning-bubble .body p {
  margin: 4px 0;
  font-size: 14px;
  color: #333;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity .3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
