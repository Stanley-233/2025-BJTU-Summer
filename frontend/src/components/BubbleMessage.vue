<template>
  <transition name="fade">
    <div v-if="visible" class="bubble-message" :class="typeClass">
      <span class="icon">
        <!-- 更简洁的警告SVG图标 -->
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="10" fill="#FFD600"/><rect x="9" y="5" width="2" height="7" rx="1" fill="#AD6800"/><rect x="9" y="14" width="2" height="2" rx="1" fill="#AD6800"/></svg>
      </span>
      <span class="content">{{ message }}</span>
    </div>
  </transition>
</template>

<script setup>
import { ref, watch, defineProps, defineExpose } from 'vue';

const props = defineProps({
  modelValue: Boolean,
  type: { type: String, default: 'warning' },
  duration: { type: Number, default: 2000 }
});

const visible = ref(false);
const message = ref('');
const typeClass = ref('');

function show(msg, type = 'warning', duration = props.duration) {
  message.value = msg;
  typeClass.value = `bubble-message--${type}`;
  visible.value = true;
  if (duration > 0) {
    setTimeout(() => visible.value = false, duration);
  }
}

function hide() {
  visible.value = false;
}

defineExpose({ show, hide });
</script>

<style scoped>
.bubble-message {
  position: fixed;
  top: 72px; /* appbar高度56px+16px间距 */
  left: 50%;
  transform: translateX(-50%);
  width: auto;
  max-width: 90vw;
  background: #fffbe6;
  color: #ad6800;
  border: none;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(173,104,0,0.08);
  padding: 10px 24px 10px 16px;
  display: flex;
  align-items: center;
  font-size: 1.08em;
  z-index: 9999;
  animation: fadeInDown 0.3s;
}
.bubble-message--error {
  background: #fff1f0;
  color: #d32f2f;
}
.bubble-message--success {
  background: #f6ffed;
  color: #389e0d;
}
.bubble-message--warning {
  background: #fffbe6;
  color: #ad6800;
}
.bubble-message .icon {
  margin-right: 10px;
  display: flex;
  align-items: center;
}
.bubble-message .content {
  word-break: break-all;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
@keyframes fadeInDown {
  from { opacity: 0; transform: translate(-50%, -20px); }
  to { opacity: 1; transform: translate(-50%, 0); }
}
</style>
