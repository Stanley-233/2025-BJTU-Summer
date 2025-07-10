<template>
  <div class="log-table-wrapper">
    <table class="log-table">
      <thead>
        <tr>
          <th>类型</th>
          <th>ID</th>
          <th>账户名</th>
          <th>日志内容</th>
          <th>创建时间</th>
          <th>IP地址</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="log in logRecords" :key="log.id">
          <td>{{ typeIconMap[log.type] }}</td>
          <td>{{ log.id }}</td>
          <td>{{ log.username }}</td>
          <td>{{ log.content }}</td>
          <td>{{ log.createdAt }}</td>
          <td>{{ log.ip }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const LogType = {
  OPERATION: 'operation',
  SECURITY: 'security',
}

const typeIconMap = {
  [LogType.OPERATION]: '🛠️',
  [LogType.SECURITY]: '🔒',
}

const logRecords = ref([
  {
    type: LogType.OPERATION,
    id: 1,
    username: 'admin',
    content: '修改了用户权限',
    createdAt: '2025-07-09 10:00:00',
    ip: '192.168.1.1',
  },
  {
    type: LogType.SECURITY,
    id: 2,
    username: 'user1',
    content: '登录失败',
    createdAt: '2025-07-09 10:05:00',
    ip: '192.168.1.2',
  },
])

function addLogRecord({ type, username, content, ip }) {
  logRecords.value.push({
    type,
    id: logRecords.value.length + 1,
    username,
    content,
    createdAt: new Date().toLocaleString(),
    ip,
  })
}
</script>

<style scoped>
.log-table-wrapper {
  width: 100%;
  overflow-x: auto;
}
.log-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  box-shadow: 0 2px 8px rgba(79,55,138,0.04);
  border-radius: 6px;
  font-size: 1em;
  margin-bottom: 24px;
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

