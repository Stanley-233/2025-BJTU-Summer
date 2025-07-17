<template>
  <div class="auth-layout">
    <div class="auth-container">
      <h1 class="title">登录</h1>
      <form @submit.prevent="onLogin" class="form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input id="username" v-model="username" type="text" required />
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input id="password" v-model="password" type="password" required />
        </div>
        <div class="email-login-link" @click="onEmailLoginClick">
          使用邮箱登录
        </div>
        <button class="btn" type="submit">登录</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue'
import useLoginPageViewModel from '@/viewmodels/LoginPageViewModel'
import { useRouter } from 'vue-router'

const router = useRouter()
const showGlobalBubble = inject('showGlobalBubble')

const { username, password, onLogin } = useLoginPageViewModel((msg) => {
  if (msg.includes('用户不存在')) {
    showGlobalBubble && showGlobalBubble('用户不存在')
  } else {
    showGlobalBubble && showGlobalBubble(msg)
  }
})

const onEmailLoginClick = () => {
  router.push('/email_login')
}
</script>

<style scoped>
.auth-layout {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 92px);
}
.auth-container {
  width: 420px;
  max-width: 90vw;
  padding: 12px 32px 60px 32px;
  background: rgba(255, 255, 255, 0.7);
  box-shadow: 0px 4px 24px 0px rgba(79, 55, 138, 0.10), 0px 1.5px 6px 0px rgba(0, 0, 0, 0.08);
  border-radius: 20px;
  margin: 0;
  position: relative;
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
.form-group input {
  width: calc(100% - 30px);
  display: block;
  margin: 0 auto;
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 16px;
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
.email-login-link {
  color: #4F378A;
  cursor: pointer;
  text-decoration: underline;
  font-size: 15px;
  transition: color 0.2s;
  display: inline;
  margin: 0;
}
.email-login-link:hover {
  color: #3a296f;
}
@media (max-width: 600px) {
  .auth-container { margin: calc(100vh - 72px)  10px; padding: 20px; }
  .title { font-size: 24px; }
  .btn { font-size: 16px; }
}
</style>
