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
    <WarningEventBubble ref="warningBubble" />
    <main class="main-content">
      <transition name="fade" mode="out-in">
        <router-view />
      </transition>
    </main>
  </div>
</template>

<script setup>
import { ref, provide, onMounted, watch } from 'vue'
import BubbleMessage from '@/components/BubbleMessage.vue'
import WarningEventBubble from '@/components/WarningEventBubble.vue'
import { DefaultApi, Configuration } from '@/api/generated'
import { EventSourcePolyfill } from 'event-source-polyfill'

const bubbleVisible = ref(false)
const bubbleMessage = ref('')

const warningBubble = ref(null)

function showGlobalBubble(msg) {
  bubbleMessage.value = msg
  bubbleVisible.value = true
  setTimeout(() => { bubbleVisible.value = false }, 2000)
}

// 定义可关闭的安全告警事件显示函数
function showWarningEvent(event) {
  warningBubble.value && warningBubble.value.show(event)
}

provide('showGlobalBubble', showGlobalBubble)
provide('showWarningEvent', showWarningEvent)

// 判断登录状态
const isLogin = ref(!!sessionStorage.getItem('token'))
window.addEventListener('storage', () => {
  isLogin.value = !!sessionStorage.getItem('token')
})

// 初始化 API 客户端，自动使用 sessionStorage 中的 token 进行 Bearer 认证
const api = new DefaultApi(new Configuration({
  basePath: 'http://127.0.0.1:8000',
  accessToken: () => sessionStorage.getItem('token')
}))
let alarmSource = null

function startAlarmStream() {
  console.log('startAlarmStream called, isLogin:', isLogin.value)
  const token = sessionStorage.getItem('token')
  if (!token) {
    console.warn('No auth token found, abort SSE subscription')
    return
  }
  // 获取用户角色并订阅对应 SSE
  api.getUserInfoGetUserInfoGet()
    .then(res => {
      console.log('Fetched user info:', res.data)
      const role = res.data.user_type
      let path = ''
      if (role === 'sysadmin') path = '/alarm/sys_warning/stream'
      else if (role === 'gov_admin') path = '/alarm/gov_warning/stream'
      else if (role === 'road_maintainer') path = '/alarm/road_warning/stream'
      else {
        console.warn('User not authorized for SSE, role:', role)
        return
      }
      const url = `http://127.0.0.1:8000${path}`
      console.log('Subscribing to SSE URL:', url)
      // TODO: Remove alert in production
      alert("测试订阅告警流: " + url)
      alarmSource = new EventSourcePolyfill(url, { headers: { Authorization: `Bearer ${token}` }, heartbeatTimeout: Number.MAX_SAFE_INTEGER })
      alarmSource.onopen = () => { console.log('SSE connection opened') }
      alarmSource.onmessage = e => {
        console.log('SSE message received:', e.data)
        try {
          const alarm = JSON.parse(e.data)
          showWarningEvent(alarm)
        } catch (err) {
          console.error('Failed to parse SSE data', err)
        }
      }
      alarmSource.onerror = err => {
        console.error('SSE error', err)
        // do not close on timeout, keep retrying
      }
    })
    .catch(err => { console.error('Failed to fetch user info for SSE', err) })
}

// 在组件挂载后及登录状态变化时启动订阅
onMounted(() => { if (isLogin.value) startAlarmStream() })
watch(isLogin, val => { if (val) startAlarmStream() })
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
