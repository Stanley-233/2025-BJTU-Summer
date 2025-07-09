<template>
  <div class="auth-container">
    <h1 class="title">注册</h1>
    <form @submit.prevent="onRegister" class="form">
      <div class="form-group">
        <label for="username">用户名</label>
        <input id="username" v-model="username" type="text" required />
      </div>
      <div class="form-group">
        <label for="email">邮箱</label>
        <input id="email" v-model="email" type="email" required />
      </div>
      <div class="form-group">
        <label for="password">密码</label>
        <input id="password" v-model="password" type="password" required />
      </div>
      <div class="form-group">
        <label for="confirm">确认密码</label>
        <input id="confirm" v-model="confirm" type="password" required />
      </div>
      <button class="btn" type="submit">注册</button>
    </form>
  </div>
</template>

<script setup>
import useRegisterPageViewModel from '@/viewmodels/RegisterPageViewModel'
const { username, email, password, confirm, onRegister } = useRegisterPageViewModel()
</script>

<style scoped>
.auth-container {
  width: 420px;
  max-width: 90vw;
  padding: 40px 32px;
  background: #fff;
  box-shadow: 0px 4px 24px 0px rgba(79, 55, 138, 0.10), 0px 1.5px 6px 0px rgba(0,0,0,0.08);
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
}
.btn:hover {
  background-color: #3a296f;
}
@media (max-width: 600px) {
  .auth-container { margin: calc(100vh - 72px) 10px; padding: 20px; }
  .title { font-size: 24px; }
  .btn { font-size: 16px; }
}
</style>
