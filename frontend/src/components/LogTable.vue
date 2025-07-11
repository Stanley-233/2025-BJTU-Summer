<template>
  <div class="log-table-wrapper">
    <div class="log-table-controls">
      <label class="date-label">开始时间：
        <input type="datetime-local" v-model="startTime" class="date-input" @change="onStartTimeChange" />
      </label>
      <label class="date-label">结束时间：
        <input type="datetime-local" v-model="endTime" class="date-input" @change="onEndTimeChange" />
      </label>
    </div>
    <table class="log-table">
      <thead>
        <tr>
          <th class="clickable-type-th" @click="toggleTypeDropdown">
            类型
            <span class="dropdown-arrow">▼</span>
            <div v-if="showTypeDropdown" class="type-dropdown">
              <div class="type-option" v-for="(icon, type) in typeIconMap" :key="type" @click.stop="selectType(type)">
                {{ icon }} {{ type }}
              </div>
            </div>
          </th>
          <th>ID</th>
          <th>日志内容</th>
          <th>创建时间</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="log in logRecords" :key="log.id">
          <td>{{ typeIconMap[log.type] }}</td>
          <td>{{ log.id }}</td>
          <td>{{ log.content }}</td>
          <td>{{ log.createdAt }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const LogType = {
  UNVERIFIED: '非法用户',
  SPOOFING: '人脸欺诈',
  ROAD_SAFETY: '道路安全',
}

const typeIconMap = {
  [LogType.UNVERIFIED]: '🔒',
  [LogType.SPOOFING]: '😡',
  [LogType.ROAD_SAFETY]: '🚧',
}

const logRecords = ref([
  {
    type: LogType.UNVERIFIED,
    id: 1,
    content: '修改了用户权限',
    createdAt: '2025-07-09 10:00:00',
  },
  {
    type: LogType.SPOOFING,
    id: 2,
    content: '登录失败',
    createdAt: '2025-07-09 10:05:00',
  },
  {
    type: LogType.ROAD_SAFETY,
    id: 3,
    content: '检测到道路异常',
    createdAt: '2025-07-09 10:10:00',
  },
])

function addLogRecord({ type, content }) {
  logRecords.value.push({
    type,
    id: logRecords.value.length + 1,
    content,
    createdAt: new Date().toLocaleString(),
  })
}

// 下拉筛选相关
const showTypeDropdown = ref(false)
const selectedType = ref(null)
const startTime = ref("")
const endTime = ref("")

function onStartTimeChange() {
  if (startTime.value && endTime.value && startTime.value > endTime.value) {
    endTime.value = startTime.value
  }
}
function onEndTimeChange() {
  if (startTime.value && endTime.value && startTime.value > endTime.value) {
    startTime.value = endTime.value
  }
}
function toggleTypeDropdown() {
  showTypeDropdown.value = !showTypeDropdown.value
}
function selectType(type) {
  selectedType.value = type
  showTypeDropdown.value = false
  // 这里只关闭下拉，不做筛选
}
function handleClickOutside(event) {
  if (!event.target.closest('.clickable-type-th')) {
    showTypeDropdown.value = false
  }
}
if (typeof window !== 'undefined') {
  window.addEventListener('click', handleClickOutside)
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
.log-table th:nth-child(1), .log-table td:nth-child(1) {
  width: 80px;
  min-width: 60px;
  max-width: 100px;
}
.log-table th:nth-child(2), .log-table td:nth-child(2) {
  width: 80px;
  min-width: 60px;
  max-width: 100px;
}
.log-table th:nth-child(3), .log-table td:nth-child(3) {
  width: auto;
  min-width: 200px;
}
.log-table th:nth-child(4), .log-table td:nth-child(4) {
  width: 160px;
  min-width: 120px;
  max-width: 200px;
}
.clickable-type-th {
  cursor: pointer;
  position: relative;
  user-select: none;
}
.dropdown-arrow {
  font-size: 0.8em;
  margin-left: 6px;
}
.type-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  background: #fff;
  border: 1.5px solid #ede7f6;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(79,55,138,0.08);
  z-index: 10;
  min-width: 90px;
  margin-top: 2px;
  padding: 4px 0;
}
.type-option {
  padding: 4px 12px;
  cursor: pointer;
  color: #4F378A;
  font-size: 0.85em;
  transition: background 0.2s;
  line-height: 1.5;
  white-space: nowrap;
  text-align: center;
  display: block;
}
.type-option:hover {
  background: #ede7f6;
}
.selected-type-info {
  margin-bottom: 8px;
  color: #4F378A;
  font-size: 1em;
  font-weight: 500;
}
.log-table-controls {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 10px;
}
.date-label {
  color: #4F378A;
  font-size: 1em;
  font-weight: 500;
}
.date-input {
  margin-left: 8px;
  padding: 4px 10px;
  border: 1.5px solid #ede7f6;
  border-radius: 6px;
  background: #f7f7fa;
  font-size: 1em;
  color: #4F378A;
  outline: none;
  transition: border 0.2s;
}
.date-input:focus {
  border: 1.5px solid #4F378A;
  background: #fff;
}
</style>

