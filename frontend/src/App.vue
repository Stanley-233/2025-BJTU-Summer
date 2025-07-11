<template>
  <div class="app-bg">
    <header class="app-bar">
      <nav>
        <router-link to="/" class="nav-link">首页</router-link>
        <router-link v-if="isLogin" to="/danger" class="nav-link">道路危险识别</router-link>
        <router-link v-if="isLogin" to="/city" class="nav-link">城市时空可视化</router-link>
        <router-link to="/face" class="nav-link">人脸识别</router-link>
        <div class="right-menu">
          <router-link v-if="isLogin" to="/console" class="nav-link">控制台</router-link>
          <router-link v-if="!isLogin" to="/login_select" class="nav-link">登录</router-link>
        </div>
      </nav>
    </header>
    <BubbleMessage :model-value="bubbleVisible" :message="bubbleMessage" type="warning" />
    <main class="main-content">
      <transition name="fade" mode="out-in">
        <router-view />
      </transition>
    </main>
  </div>
</template>

<script setup>
import { ref, provide } from 'vue'
import BubbleMessage from '@/components/BubbleMessage.vue'

const bubbleVisible = ref(false)
const bubbleMessage = ref('')

function showGlobalBubble(msg) {
  bubbleMessage.value = msg
  bubbleVisible.value = true
  setTimeout(() => { bubbleVisible.value = false }, 2000)
}

provide('showGlobalBubble', showGlobalBubble)

// 判断登录状态
const isLogin = ref(!!sessionStorage.getItem('token'))
window.addEventListener('storage', () => {
  isLogin.value = !!sessionStorage.getItem('token')
})
</script>

<style scoped>
.app-bg {
  min-height: 100vh;
  width: 100vw;
  background: #f5f5f5;
}
.app-bar {
  width: 100%;
  background: #f8f9fa;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;
}
.app-bar nav {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  padding: 0 16px;
  height: 56px;
}
.nav-link {
  margin-right: 24px;
  font-size: 16px;
  color: #333;
  text-decoration: none;
  position: relative;
  padding-bottom: 4px;
  transition: color 0.2s, background 0.2s;
  border-radius: 6px 6px 0 0;
}
.nav-link:hover {
  background: #ede7f6;
  color: #4F378A;
}
.router-link-active {
  font-weight: 500;
  color: #4F378A;
}
.router-link-active::after {
  content: '';
  display: block;
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 3px;
  background: #4F378A;
  border-radius: 2px 2px 0 0;
}
.right-menu {
  margin-left: auto;
  display: flex;
  align-items: center;
}
.right-menu .nav-link {
  margin-right: 16px;
}
.main-content {
  padding-top: 72px; /* 为固定顶部预留空间 */
  max-width: 1200px;
  margin: 0 auto;
}
</style>
