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
  message: String,
  type: { type: String, default: 'warning' },
  duration: { type: Number, default: 2000 }
});

const visible = ref(props.modelValue);
const typeClass = props.type ? `bubble-message--${props.type}` : '';

watch(() => props.modelValue, (val) => {
  visible.value = val;
  if (val && props.duration > 0) {
    setTimeout(() => visible.value = false, props.duration);
  }
});

defineExpose({
  show(msg) {
    visible.value = true;
    if (msg) {
      // @ts-ignore
      this.message = msg;
    }
    if (props.duration > 0) {
      setTimeout(() => visible.value = false, props.duration);
    }
  },
  hide() {
    visible.value = false;
  }
});
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
  box-shadow: 0 2px 8px rgba(255,214,0,0.10);
  padding: 10px 20px;
  display: inline-flex;
  align-items: center;
  z-index: 1200;
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 0.02em;
  opacity: 0.98;
  transition: box-shadow 0.2s;
}
.bubble-message .icon {
  margin-right: 10px;
  display: flex;
  align-items: center;
}
.bubble-message .content {
  flex: 1;
  text-align: center;
}
.bubble-message--warning {
  background: #fffbe6;
  color: #ad6800;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
