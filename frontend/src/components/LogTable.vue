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
    <table class="log-table" :style="{ tableLayout: 'fixed' }">
      <thead>
      <tr>
        <th :style="{ width: columnWidths[0] + 'px' }" class="clickable-type-th" @click="toggleTypeDropdown" ref="typeTh">
          类型
          <span class="dropdown-arrow">▼</span>
          <div v-if="showTypeDropdown" class="type-dropdown">
            <div class="type-option" v-for="(icon, type) in typeIconMap" :key="type" @click.stop="selectType(type)">
              {{ icon }} {{ LogType[type] }}
            </div>
          </div>
          <div class="resize-handle" @mousedown.prevent="initResize($event, 0)"></div>
        </th>
        <th :style="{ width: columnWidths[1] + 'px' }">日志内容
          <div class="resize-handle" @mousedown.prevent="initResize($event, 1)"></div>
        </th>
        <th :style="{ width: columnWidths[2] + 'px' }">创建时间
          <div class="resize-handle" @mousedown.prevent="initResize($event, 2)"></div>
        </th>
        <th :style="{ width: columnWidths[3] + 'px' }">详情
        </th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="log in pagedLogs" :key="log.id">
        <td :style="{ width: columnWidths[0] + 'px' }">{{ typeIconMap[log.event_type] + LogType[log.event_type] }}</td>
        <td :style="{ width: columnWidths[1] + 'px' }">{{ log.description }}</td>
        <td :style="{ width: columnWidths[2] + 'px' }">{{ formatTimestamp(log.timestamp) }}</td>
        <td :style="{ width: columnWidths[3] + 'px' }"><button @click="viewDetail(log)">查看</button></td>
      </tr>
      </tbody>
    </table>
    <!-- 翻页栏 -->
    <div class="pagination-bar" v-if="totalPages > 1">
      <button :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">上一页</button>
      <span>第 {{ currentPage }} / {{ totalPages }} 页</span>
      <button :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)">下一页</button>
    </div>
    <!-- 日志详情弹窗 -->
    <div v-if="showDetailModal && detailLog" class="modal-overlay" @click.self="closeDetailModal">
      <div class="modal-content">
        <h3>日志详情</h3>
        <template v-if="detailLog.log">
          <p><strong>类型：</strong>{{ typeIconMap[detailLog.log.event_type] }} {{ LogType[detailLog.log.event_type] }}</p>
          <p><strong>日志ID：</strong>{{ detailLog.log.id }}</p>
          <p><strong>时间：</strong>{{ formatTimestamp(detailLog.log.timestamp) }}</p>
          <p><strong>描述：</strong>{{ detailLog.log.description }}</p>
          <div v-if="detailLog.detail">
            <p v-if="detailLog.detail.face_data"><strong>人脸数据：</strong>{{ detailLog.detail.face_data }}</p>
            <p v-if="detailLog.detail.liveness_score !== undefined"><strong>活体检测分数：</strong>{{ detailLog.detail.liveness_score }}</p>
            <p v-if="detailLog.detail.spoofing_score !== undefined"><strong>欺诈检测分数：</strong>{{ detailLog.detail.spoofing_score }}</p>
            <p v-if="detailLog.detail.danger_nums !== undefined"><strong>危险物品数量：</strong>{{ detailLog.detail.danger_nums }}</p>
          </div>
          <div v-if="detailLog.dangers && detailLog.dangers.length">
            <h4>危险详情：</h4>
            <ul>
              <li v-for="d in detailLog.dangers" :key="d.danger_id">
                类型：{{ d.type }}，置信度：{{ d.confidence }}
              </li>
            </ul>
          </div>
        </template>
        <button class="close-btn" @click="closeDetailModal">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { queryLogs, queryLogDetail } from '../viewmodels/LogViewModel'

const LogType = {
  0: '非法用户',
  1: '人脸欺诈',
  2: '道路安全',
}

const typeIconMap = {
  0: '🔒',
  1: '😡',
  2: '🚧',
}

const logRecords = ref([])

function setLogs(list) {
  logRecords.value = Array.isArray(list) ? list : []
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

// 分页相关
const pageSize = 10
const currentPage = ref(1)
const totalPages = computed(() => Math.ceil(logRecords.value.length / pageSize))
const pagedLogs = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return logRecords.value.slice(start, start + pageSize)
})

function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const showDetailModal = ref(false)
const detailLog = ref(null)

// 点击查看详情时获取详细数据
async function viewDetail(log) {
  try {
    const detail = await queryLogDetail(log.id)
    if (detail) {
      detailLog.value = detail
      showDetailModal.value = true
    }
  } catch (e) {
    console.error(e)
    alert('获取日志详情失败')
  }
}
function closeDetailModal() {
  showDetailModal.value = false
}

// 格式化时间到秒
function formatTimestamp(ts) {
  if (!ts) return ''
  const m = ts.match(/^(.{19})/)
  const str = m ? m[1] : ts
  return str.replace('T', ' ')
}

// 监听筛选条件变化，自动加载日志
async function loadLogs() {
  // 格式化时间范围
  let logRange = null
  if (startTime.value && endTime.value) {
    logRange = `${startTime.value.replace('T', ' ').slice(0, 16)}~${endTime.value.replace('T', ' ').slice(0, 16)}`
  }
  // 调用前弹窗显示参数
  alert(`查询参数：\ntype: ${selectedType.value}\nlogRange: ${logRange}\nlimit: ${pageSize}\noffset: ${(currentPage.value - 1) * pageSize}`)
  const logs = await queryLogs(selectedType.value, logRange, pageSize, (currentPage.value - 1) * pageSize)
  setLogs(logs || [])
}

onMounted(() => {
  loadLogs()
})

watch([selectedType, startTime, endTime, currentPage], () => {
  loadLogs()
})

// column resize state
const columnWidths = ref([80, 200, 160, 100])
let resizingIndex = null
let startX = 0
let startWidth = 0
let startNextWidth = 0

function initResize(event, index) {
  resizingIndex = index
  startX = event.clientX
  startWidth = columnWidths.value[index]
  startNextWidth = columnWidths.value[index + 1] || 0
  window.addEventListener('mousemove', onResize)
  window.addEventListener('mouseup', stopResize)
}

function onResize(event) {
  if (resizingIndex !== null) {
    const i = resizingIndex
    const delta = event.clientX - startX
    let newWidth = startWidth + delta
    let newNextWidth = startNextWidth - delta
    const min = 60
    const max = 300
    // constrain both new widths
    if (newWidth < min) {
      newWidth = min
      newNextWidth = startWidth + startNextWidth - min
    }
    if (newNextWidth < min) {
      newNextWidth = min
      newWidth = startWidth + startNextWidth - min
    }
    if (newWidth > max) {
      newWidth = max
      newNextWidth = startWidth + startNextWidth - max
    }
    columnWidths.value[i] = newWidth
    if (columnWidths.value.length > i + 1) {
      columnWidths.value[i + 1] = newNextWidth
    }
  }
}

function stopResize() {
  window.removeEventListener('mousemove', onResize)
  window.removeEventListener('mouseup', stopResize)
  resizingIndex = null
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
  font-size: 0.9em; /* reduced font size */
  margin-bottom: 24px;
}
.log-table th, .log-table td {
  padding: 8px 10px; /* reduced row height */
  border-bottom: 1px solid #ede7f6;
  text-align: left;
  color: #333;
  position: relative;
}
.log-table td {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
.log-table th {
  color: #4F378A;
  font-weight: 600;
}
.log-table tr:last-child td {
  border-bottom: none;
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
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0,0,0,0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-content {
  background: #fff;
  border-radius: 8px;
  padding: 32px 24px 20px 24px;
  min-width: 320px;
  box-shadow: 0 4px 24px rgba(79,55,138,0.12);
  position: relative;
  text-align: left;
}
.close-btn {
  margin-top: 18px;
  padding: 6px 18px;
  background: #4F378A;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1em;
  transition: background 0.2s;
}
.close-btn:hover {
  background: #6c4bb6;
}
.pagination-bar {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 18px;
  margin: 18px 0 0 0;
}
.pagination-bar button {
  padding: 4px 16px;
  border: 1.5px solid #ede7f6;
  border-radius: 6px;
  background: #f7f7fa;
  color: #4F378A;
  font-size: 1em;
  cursor: pointer;
  transition: background 0.2s;
}
.pagination-bar button:disabled {
  background: #ede7f6;
  color: #aaa;
  cursor: not-allowed;
}
.pagination-bar span {
  color: #4F378A;
  font-size: 1em;
}
.resize-handle {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 8px;
  height: 60%;
  cursor: col-resize;
  background: #e0e0e0;
  border-radius: 4px;
  transition: background 0.2s;
}
.resize-handle:hover {
  background: rgba(0,0,0,0.1);
}
</style>
