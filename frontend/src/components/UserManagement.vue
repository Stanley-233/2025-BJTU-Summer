<template>
  <div class="user-management">
    <h3>用户管理</h3>
    <div v-if="loading">加载中...</div>
    <div v-else>
      <table class="user-table">
        <thead>
          <tr>
            <th>用户名</th>
            <th>邮箱</th>
            <th>邮箱验证状态</th>
            <th>角色</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.user.username">
            <td>{{ item.user.username }}</td>
            <td>{{ item.user.email_address }}</td>
            <td>{{ item.user.email_verified ? '是' : '否' }}</td>
            <td>
              <select v-model="item.newType">
                <option v-for="opt in options" :key="opt" :value="opt">
                  {{ roleLabel(opt) }}
                </option>
              </select>
            </td>
            <td>
              <button @click="change(item)" :disabled="item.newType === item.user.user_type">提交</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import {ref, onMounted} from 'vue'
import {fetchAllUsers, updateUserPermission} from '@/viewmodels/UserManagementViewModel'
import {UserType} from '@/api/generated'
import type {UserWithEmail} from '@/api/generated'

const items = ref<Array<{user: UserWithEmail, newType: UserType}>>([])
const loading = ref(true)
const options: UserType[] = Object.values(UserType)
// Helper to map type to Chinese
function roleLabel(t: UserType | undefined) {
  switch(t) {
    case UserType.Sysadmin: return '系统管理员'
    case UserType.Driver: return '司机'
    case UserType.GovAdmin: return '政府管理员'
    case UserType.RoadMaintainer: return '道路维护人员'
    default: return '未知'
  }
}

async function load() {
  loading.value = true
  const users = await fetchAllUsers(msg => alert(msg))
  if (users) {
    items.value = users.map(u => ({ user: u, newType: u.user_type || options[0] }))
  }
  loading.value = false
}

async function change(item: {user: UserWithEmail, newType: UserType}) {
  const ok = await updateUserPermission(
    item.user.username,
    item.newType,
    msg => alert(msg),
    msg => alert(msg)
  )
  if (ok) {
    item.user.user_type = item.newType
  }
}

onMounted(load)
</script>

<style scoped>
.user-management {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(79, 55, 138, 0.06);
}
.user-table {
  width: 100%;
  border-collapse: collapse;
}
.user-table th, .user-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}
.user-table th {
  background: #f7f7fa;
  color: #4F378A;
}
.user-table select {
  width: 100%;
  height: 40px;
  padding: 0 12px;
  font-size: 14px;
  line-height: 20px;
  color: rgba(0, 0, 0, 0.87);
  background-color: #fff;
  border: 1px solid rgba(0, 0, 0, 0.38);
  border-radius: 4px;
  appearance: none;
  -webkit-appearance: none;
  /* Add custom arrow if desired */
}
button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
