<template>
  <div class="console-layout">
    <aside class="side-tabs">
      <div :class="['tab-item', activeTab === 'user' ? 'active' : '']" @click="activeTab = 'user'">用户信息</div>
      <div :class="['tab-item', activeTab === 'log' ? 'active' : '']" @click="activeTab = 'log'">日志记录</div>
      <div :class="['tab-item', activeTab === 'upload' ? 'active' : '']" @click="activeTab = 'upload'">人脸上传</div>
    </aside>
    <main class="console-main">
      <div class="tab-title">
        <h2 v-if="activeTab === 'user'">用户信息</h2>
        <h2 v-else-if="activeTab === 'log'">日志记录</h2>
        <h2 v-else-if="activeTab === 'upload'">人脸上传</h2>
        <div class="tab-title-underline"></div>
      </div>
      <template v-if="activeTab === 'user'">
        <div class="user-info-section">
          <div class="user-info-row">
            <span class="user-info-label">用户名：</span>
            <span class="user-info-value">{{ userInfo.username || 'unknown' }}</span>
          </div>
          <div class="user-info-row">
            <span class="user-info-label">身份：</span>
            <span class="user-info-value">{{ userInfo.user_type || 'unknown'}}</span>
          </div>
          <div class="user-info-row">
            <span class="user-info-label">最近登录IP：</span>
            <span class="user-info-value">{{ userInfo.last_ip || 'unknown' }}</span>
          </div>
        </div>
        <div class="user-info-row user-info-row-editable">
          <span class="user-info-label">注册邮箱: </span>
          <span class="user-info-value">
            <span>{{ email }}</span>
          </span>
          <button class="user-info-btn" @click="onVerifyEmail" :disabled="isVerified || cooldown > 0"
                  :class="{ 'disabled-btn': isVerified || cooldown > 0 }">
            {{ isVerified ? '已验证' : (cooldown > 0 ? `请稍候(${cooldown})` : '验证邮箱') }}
          </button>
        </div>
        <div v-if="showVerificationInput" class="verification-section">
          <input v-model="verificationCode" class="verification-input" placeholder="请输入验证码" />
          <button class="verification-btn" @click="onConfirmVerification">确认</button>
        </div>
      </template>
      <template v-else-if="activeTab === 'log'">
        <LogTable/>
      </template>
      <template v-else>
        <FaceUpload/>
      </template>
    </main>
    <BubbleMessage ref="bubbleRef"/>
  </div>
</template>

<script setup>
import {ref, onMounted, inject} from 'vue'
import BubbleMessage from '../components/BubbleMessage.vue'
import {codeCheck, getUserEmail, getUserInfo, verifyEmail} from '../viewmodels/VerifyInfoViewModel'
import LogTable from '../components/LogTable.vue'
import FaceUpload from '../components/FaceUpload.vue'

const activeTab = ref('user')

const email = ref("")
const isVerified = ref(false)
const showVerificationInput = ref(false);
const verificationCode = ref("");

// 冷却相关变量
const cooldown = ref(0); // 剩余冷却秒数
let cooldownTimer = null;

const bubbleRef = ref(null)
const showGlobalBubble = inject('showGlobalBubble')

const userInfo = ref({
  username: '',
  last_ip: '',
  user_type: ''
})

async function fetchUserInfo() {
  try {
    const userEmail = await getUserEmail()
    if (userEmail == null) {
      email.value = '邮箱获取失败，请检查登录状态'
      isVerified.value = true
    } else {
      email.value = userEmail.email_address;
      isVerified.value = userEmail.email_verified;
    }
    const data = await getUserInfo()
    if(data == null){
      showGlobalBubble('获取用户信息失败，请检查登录状态')
    } else {
      userInfo.value = {
        username: data.username,
        last_ip: data.last_ip,
      }
      switch (data.user_type){
        case 'sysadmin':
          userInfo.value.user_type = '系统管理员'
          break;
        case 'driver':
          userInfo.value.user_type = '司机'
          break;
        case 'gov_admin':
          userInfo.value.user_type = '政府管理员'
          break;
        default:
          userInfo.value.user_type = 'error'
      }
    }
  } catch (e) {
    showGlobalBubble('获取用户信息失败')
  }
}

onMounted(() => {
  fetchUserInfo()
})

async function onVerifyEmail() {
  if (cooldown.value > 0) {
    showGlobalBubble && showGlobalBubble(`请勿频繁发送验证码，请在${cooldown.value}秒后重试`)
    return;
  }
  await verifyEmail((msg) => {
    showGlobalBubble(msg)
    if (!isVerified.value) {
      showVerificationInput.value = true;
      // 启动冷却
      cooldown.value = 60;
      if (cooldownTimer) clearInterval(cooldownTimer);
      cooldownTimer = setInterval(() => {
        if (cooldown.value > 0) {
          cooldown.value--;
        } else {
          clearInterval(cooldownTimer);
          cooldownTimer = null;
        }
      }, 1000);
    }
  })
}

async function onConfirmVerification() {
  const state = await codeCheck(verificationCode.value, (msg) => {
    showGlobalBubble(msg)
  });
  if(state === 1){
    showVerificationInput.value = false;
  }else if(state === 0){
    showVerificationInput.value = false;
    isVerified.value = true;
  }else if(state === 2){
    verificationCode.value = '';
  }
}
</script>

<style scoped>
.console-layout {
  display: flex;
  height: calc(100vh - 92px); /* 72px为顶���bar高度，底部再留20px间距 */
  min-height: 400px;
  margin-top: 0;
  margin-bottom: 20px; /* 屏幕底部留出间距 */
}

.side-tabs {
  width: 140px;
  background: #f7f7fa;
  border-right: 1px solid #ececec;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 100%;
  padding-top: 0;
  /* 增加右侧分割线���投影 */
  box-shadow: 2px 0 8px rgba(79, 55, 138, 0.04);
  border-right: 2px solid #ede7f6;
}

.tab-item {
  padding: 16px 0;
  text-align: center;
  font-size: 16px;
  color: #666;
  cursor: pointer;
  border-left: 4px solid transparent;
  transition: background 0.2s, color 0.2s, border-color 0.2s;
}

.console-main {
  flex: 1;
  height: 100%;
  min-height: 100%;
  margin-top: 0;
  padding: 40px 56px 32px 56px;
  background: #f8f9fa;
  box-sizing: border-box;
  border-radius: 0;
  /* 增加更明显的阴影和顶部边框修饰 */
  box-shadow: 0 4px 24px rgba(79, 55, 138, 0.10), 0 1.5px 6px rgba(0, 0, 0, 0.08);
  border-top: 4px solid #ede7f6;
  font-size: 18px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.tab-title {
  width: 100%;
  margin-bottom: 32px;
}

.tab-title h2 {
  font-size: 1.5em;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #4F378A;
}

.tab-title-underline {
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, #4F378A 0%, #ede7f6 60%, #f8f9fa 100%);
  border-radius: 2px;
  margin-bottom: 8px;
}

.user-info-section {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(79, 55, 138, 0.06);
  padding: 24px 32px 8px 32px;
  margin-bottom: 32px;
}

.user-info-row {
  display: flex;
  align-items: center;
  font-size: 1.1em;
  margin-bottom: 16px;
  color: #333;
}

.user-info-row-editable {
  margin-bottom: 16px;
}

.user-info-label {
  min-width: 110px;
  color: #666;
  font-weight: 500;
}

.user-info-value {
  flex: 1;
  display: flex;
  align-items: center;
  min-height: 32px; /* 保证编辑和非编辑状态高度一致，避免间距抖动 */
}

.user-info-btn {
  margin-left: 12px;
  padding: 4px 16px;
  font-size: 0.95em;
  border: none;
  border-radius: 4px;
  background: #ede7f6;
  color: #4F378A;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}

.user-info-btn:hover {
  background: #d1c4e9;
}

.user-info-btn.disabled-btn {
  background: #d9d9d9;
  color: #8c8c8c;
  cursor: not-allowed;
}

.log-table th, .log-table td {
  padding: 12px 10px;
  border-bottom: 1px solid #ede7f6;
  text-align: left;
  color: #333;
}

.log-table th {
  background: #f7f7fa;
  color: #4F378A;
  font-weight: 600;
}

.log-table tr:last-child td {
  border-bottom: none;
}

.verification-section {
  margin-top: 18px;
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(79, 55, 138, 0.06);
  padding: 16px 24px;
  width: fit-content;
}

.verification-input {
  flex: 1;
  min-width: 180px;
  padding: 8px 14px;
  margin-right: 16px;
  border: 1.5px solid #ede7f6;
  border-radius: 6px;
  background: #f7f7fa;
  font-size: 1em;
  color: #4F378A;
  transition: border 0.2s, box-shadow 0.2s;
  outline: none;
}
.verification-input:focus {
  border: 1.5px solid #4F378A;
  box-shadow: 0 0 0 2px #ede7f6;
  background: #fff;
}

.verification-btn {
  padding: 8px 22px;
  background-color: #4F378A;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 1em;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(79, 55, 138, 0.08);
  transition: background 0.2s, box-shadow 0.2s;
}
.verification-btn:hover {
  background-color: #37205e;
  box-shadow: 0 4px 16px rgba(79, 55, 138, 0.13);
}
</style>
