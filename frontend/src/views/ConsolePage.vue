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
            <span class="user-info-value">{{ userInfo.username || '（无）' }}</span>
          </div>
          <div class="user-info-row">
            <span class="user-info-label">是否管理员：</span>
            <span class="user-info-value">{{ userInfo.is_admin ? '是' : '否' }}</span>
          </div>
          <div class="user-info-row">
            <span class="user-info-label">最近登录IP：</span>
            <span class="user-info-value">{{ userInfo.last_ip || '（无）' }}</span>
          </div>
          <div class="user-info-row">
            <span class="user-info-label">人脸数据：</span>
            <span class="user-info-value">{{ userInfo.face_data ? '已录入' : '未录入' }}</span>
          </div>
        </div>
        <div class="user-info-row user-info-row-editable">
          <span class="user-info-label">注册手机号：</span>
          <span class="user-info-value">
            <template v-if="editingPhone">
              <input v-model="phone" class="user-info-input" placeholder="请输入手机号" />
            </template>
            <template v-else>
              <span class="user-info-placeholder">（待接入）</span>
            </template>
          </span>
          <button class="user-info-btn" @click="onEditPhone">
            {{ editingPhone ? '保存' : '编辑' }}
          </button>
          <button class="user-info-btn" @click="onVerifyPhone">验证</button>
        </div>
        <div class="user-info-row user-info-row-editable">
          <span class="user-info-label">注册邮箱：</span>
          <span class="user-info-value">
            <template v-if="editingEmail">
              <input v-model="email" class="user-info-input" placeholder="请输入邮箱" type="email" autocomplete="email" />
            </template>
            <template v-else>
              <span>{{ email || '（未填写）' }}</span>
            </template>
          </span>
          <button class="user-info-btn" @click="onEditEmail">
            {{ editingEmail ? '保存' : '编辑' }}
          </button>
          <button class="user-info-btn" @click="onVerifyEmail">
            验证
          </button>
        </div>
      </template>
      <template v-else-if="activeTab === 'log'">
        <LogTable />
      </template>
      <template v-else>
        <FaceUpload />
      </template>
    </main>
    <BubbleMessage ref="bubbleRef" />
  </div>
</template>

<script setup>
import {ref, onMounted, inject} from 'vue'
import BubbleMessage from '../components/BubbleMessage.vue'
import verifyEmail from '../viewmodels/VerifyInfoViewModel'
import LogTable from '../components/LogTable.vue'
import FaceUpload from '../components/FaceUpload.vue'
const activeTab = ref('user')

// 编辑状态
const editingPhone = ref(false)
const editingEmail = ref(false)
// 预留数据
const phone = ref("")
const email = ref("")

const bubbleRef = ref(null)
const showGlobalBubble = inject('showGlobalBubble')

const userInfo = ref({
  username: '',
  is_admin: false,
  face_data: '',
  last_ip: ''
})

async function fetchUserInfo() {
  try {

    userInfo.value = res.data
  } catch (e) {
    showGlobalBubble('获取用户信息失败')
  }
}

onMounted(() => {
  fetchUserInfo()
})

function onEditEmail() {
  if (editingEmail.value) {
    // 校验邮箱格式
    const emailPattern = /^([A-Za-z0-9_\-.])+@([A-Za-z0-9_\-.])+\.([A-Za-z]{2,4})$/
    console.log(email.value)
    if (!emailPattern.test(email.value)) {
      showGlobalBubble('请输入合法的邮件地址')
      return
    }
    localStorage.setItem('user_email', email.value)
    editingEmail.value = false // 保存后立即切换为不可编辑
    return
  }
  editingEmail.value = true
}

function onEditPhone() {
  if (editingPhone.value) {
    // TODO: 保存手机号逻辑
  }
  editingPhone.value = !editingPhone.value
}
function onVerifyPhone() {
  // TODO: 验证手机号逻辑
}

function onVerifyEmail() {
  verifyEmail((msg) => {showGlobalBubble(msg)} )
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
  box-shadow: 2px 0 8px rgba(79,55,138,0.04);
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
.tab-item.active {
  color: #4F378A;
  /* 增加右侧小投影和背景渐变修饰 */
  background: linear-gradient(90deg, #fff 80%, #ede7f6 100%);
  box-shadow: 2px 0 8px rgba(79,55,138,0.04);
  border-left: 4px solid #4F378A;
  font-weight: 600;
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
  box-shadow: 0 4px 24px rgba(79,55,138,0.10), 0 1.5px 6px rgba(0,0,0,0.08);
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
  box-shadow: 0 2px 8px rgba(79,55,138,0.06);
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
.user-info-input {
  font-size: 1em;
  padding: 4px 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  outline: none;
  margin-right: 12px;
  min-width: 180px;
  background: #fff;
  height: 32px; /* �����编辑状态保持一��� */
  box-sizing: border-box;
}
.user-info-placeholder {
  color: #bbb;
  font-style: italic;
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
  transition: background 0.2s;
}
.user-info-btn:hover {
  background: #d1c4e9;
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
</style>
