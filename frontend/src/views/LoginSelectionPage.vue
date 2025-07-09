<template>
  <div class="start-page">
    <h1 class="welcome-title">欢迎！</h1>
    <div class="card">
      <button class="fab-btn" @click="goLogin" style="width: 100%; display: flex; align-items: center; justify-content: center; gap: 10px;">
        <span class="icon">
          <!-- 账户图标SVG线性风格 -->
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="#4F378A" stroke-width="2"/>
            <circle cx="12" cy="10" r="4" stroke="#4F378A" stroke-width="2"/>
            <path d="M6 18c0-2.21 3.58-4 6-4s6 1.79 6 4" stroke="#4F378A" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </span>
        <span class="label">登录现有账户</span>
      </button>
      <div class="divider">或</div>
      <button class="fab-btn" @click="goRegister" style="width: 100%; display: flex; align-items: center; justify-content: center; gap: 10px;">
        <span class="icon">
          <!-- 添加图标SVG线性风格 -->
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="#4F378A" stroke-width="2"/>
            <path d="M12 8v8M8 12h8" stroke="#4F378A" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </span>
        <span class="label">注册一个新账户</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
const goLogin = () => {
  router.push('/login')
}
const goRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.start-page {
  height: calc(100vh - 72px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.welcome-title {
  font-family: 'Roboto', 'PingFang SC', 'Microsoft YaHei', Arial, sans-serif;
  font-size: 36px;
  font-weight: 500;
  color: #4F378A;
  margin-bottom: 48px;
  letter-spacing: 1px;
}
.card {
  background: #fff;
  box-shadow: 0px 4px 24px 0px rgba(79, 55, 138, 0.10), 0px 1.5px 6px 0px rgba(0,0,0,0.08);
  border-radius: 20px;
  width: 420px;
  max-width: 90vw;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 32px;
  gap: 28px;
}
.fab-btn {
  display: flex;
  align-items: center;
  background: #EADDFF;
  color: #4F378A;
  border: none;
  border-radius: 16px;
  box-shadow: 0px 1px 3px 0px rgba(0,0,0,0.10), 0px 4px 8px 3px rgba(0,0,0,0.06);
  font-size: 22px;
  font-family: 'Roboto', 'PingFang SC', 'Microsoft YaHei', Arial, sans-serif;
  font-weight: 400;
  padding: 0 32px;
  height: 56px;
  min-width: 240px;
  cursor: pointer;
  transition: background 0.2s, box-shadow 0.2s;
  gap: 10px;
  outline: none;
}
.fab-btn:active {
  background: #d1bfff;
  box-shadow: 0px 2px 8px 0px rgba(79, 55, 138, 0.10);
}
.fab-btn:hover {
  background: #d1bfff;
}
.icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
}
.label {
  margin-left: 8px;
  font-size: 22px;
  font-weight: 400;
  color: #4F378A;
}
.divider {
  font-size: 18px;
  color: #888;
  letter-spacing: 2px;
}
@media (max-width: 600px) {
  .card {
    width: 98vw;
    padding: 20px 2vw;
    gap: 18px;
  }
  .welcome-title {
    font-size: 26px;
    margin-bottom: 24px;
  }
  .fab-btn {
    font-size: 18px;
    min-width: 120px;
    padding: 0 12px;
    height: 44px;
  }
}
</style>
