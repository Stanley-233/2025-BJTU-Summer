<template>
  <div class="auth-container">
    <h1 class="title">登录</h1>
    <form @submit.prevent="onEmailLogin" class="form">
      <div class="form-group">
        <label for="email">邮箱</label>
        <input id="email" v-model="email" type="email" required />
      </div>
      <div class="form-group code-group">
        <label for="code">验证码</label>
        <div class="code-input-wrapper">
          <input id="code" v-model="code" type="text" required maxlength="6" class="code-input" />
          <button type="button" class="send-code-btn" @click="onSendCode" :disabled="isCooldown">
            {{ isCooldown ? `${cooldown}s` : '发送' }}
          </button>
          <span class="code-decor-dots"></span>
        </div>
      </div>
      <div class="switch-login-link" @click="onSwitchToUserLogin">
        使用用户名与密码登录
      </div>
      <button class="btn" type="submit">登录</button>
    </form>
  </div>
</template>

<script setup>
import {inject, ref, onUnmounted} from 'vue'
import { useRouter } from 'vue-router'
import {emailLoginCodeCheck, requestEmailLoginCode} from "@/viewmodels/EmailLoginViewModel.js";
const showGlobalBubble = inject('showGlobalBubble')

const router = useRouter()
const email = ref('')
const code = ref('')

const cooldown = ref(0)
const isCooldown = ref(false)
let timer = null

const onEmailLogin = async () => {
  const status = await emailLoginCodeCheck(email.value, code.value, showGlobalBubble)
  if (status) {
    email.value = ''
    code.value = ''
    await router.push('/console')
  } else {
    code.value = ''
  }
}

const onSendCode = async () => {
  if (isCooldown.value) return
  const status = await requestEmailLoginCode(email.value, showGlobalBubble)
  if(!status)
    email.value = ''
  isCooldown.value = true
  cooldown.value = 60
  timer = setInterval(() => {
    cooldown.value--
    if (cooldown.value <= 0) {
      isCooldown.value = false
      clearInterval(timer)
    }
  }, 1000)
}

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

const onSwitchToUserLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.auth-container {
  width: 420px;
  max-width: 90vw;
  padding: 12px 32px 60px 32px;
  background: #fff;
  box-shadow: 0 4px 24px 0 rgba(79, 55, 138, 0.10), 0 1px 6px 0 rgba(0,0,0,0.08);
  border-radius: 20px;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}
.title {
  font-size: 32px;
  color: #4F378A;
  text-align: center;
  margin-bottom: 24px;
}
.form-group {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
}
.form-group label {
  margin-bottom: 8px;
  color: #333;
}

.form-group input:not(.code-input) {
  width: calc(100% - 30px);
  display: block;
  margin: 0 auto;
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 16px;
}
.code-input {
  width: 80px !important;
  margin: 0 8px 0 0;
  display: inline-block;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 16px;
  padding: 8px 12px;
}
.send-code-btn {
  width: 60px;
  height: 38px;
  margin-left: 0;
  display: inline-block;
  /* 38px 与输入框高度一致，若需更精确可与 .form-group input 的 padding、border 计算一致 */
  padding: 0;
  background-color: #4F378A;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}
.send-code-btn:hover {
  background-color: #3a296f;
}
.btn {
  width: 100%;
  padding: 12px;
  background-color: #4F378A;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 18px;
  cursor: pointer;
  margin-top: 12px;
}
.btn:hover {
  background-color: #3a296f;
}
.switch-login-link {
  color: #4F378A;
  cursor: pointer;
  text-decoration: underline;
  font-size: 15px;
  transition: color 0.2s;
  display: inline;
  margin: 0;
}
.switch-login-link:hover {
  color: #3a296f;
}
.code-group .code-input-wrapper {
  display: flex;
  align-items: center;
}
.code-decor-dots {
  flex: 1;
  display: flex;
  align-items: center;
  margin-left: 14px;
  min-width: 30px;
  height: 32px;
  position: relative;
  overflow: hidden;
}
.code-decor-dots::before {
  content: '';
  display: block;
  width: 100%;
  height: 6px;
  background-image: repeating-linear-gradient(
    to right,
    #a18cd1 0 6px,
    transparent 6px 16px
  );
  border-radius: 3px;
  opacity: 0.5;
  position: absolute;
  top: 50%;
  left: 0;
  transform: translateY(-50%);
}
@media (max-width: 600px) {
  .auth-container { margin: calc(100vh - 72px)  10px; padding: 20px; }
  .title { font-size: 24px; }
  .btn { font-size: 16px; }
  .code-input { width: 80px; }
}
</style> 