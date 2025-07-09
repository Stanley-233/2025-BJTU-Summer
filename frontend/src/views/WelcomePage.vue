<template>
  <div class="welcome-container">
    <h1 class="app-title">滴嘟出行</h1>
    <p class="app-subtitle">欢迎使用滴嘟出行综合平台</p>
    <button class="enter-btn" @click="router.push('/login_select')">进入应用</button>
  </div>
</template>
<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>
<style scoped>
.welcome-container {
  height: calc(100vh - 72px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}
.app-title {
  font-size: 48px;
  color: #4F378A;
  margin-bottom: 16px;
}
.app-subtitle {
  font-size: 20px;
  color: #666;
  margin-bottom: 32px;
}
.enter-btn {
  padding: 12px 36px;
  font-size: 18px;
  color: #fff;
  background-color: #4F378A;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}
.enter-btn:hover {
  background-color: #3a296f;
}
@media (max-width: 600px) {
  .app-title { font-size: 32px; }
  .app-subtitle { font-size: 16px; }
  .enter-btn { font-size: 16px; padding: 10px 24px; }
}
</style>

