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
          <th
            v-for="(col, idx) in columns"
            :key="col.key"
            :style="{ width: colWidths[idx] + 'px' }"
            class="resizable-th"
          >
            <span v-if="col.key === 'type'" class="clickable-type-th" @click="toggleTypeDropdown">
              类型
              <span class="dropdown-arrow">▼</span>
              <div v-if="showTypeDropdown" class="type-dropdown">
                <div class="type-option" v-for="(icon, type) in typeIconMap" :key="type" @click.stop="selectType(type)">
                  {{ icon }} {{ LogType[type] }}
                </div>
              </div>
            </span>
            <template v-else>{{ col.title }}</template>
            <span
              v-if="idx < columns.length - 1"
              class="resize-handle"
              @mousedown="startResize($event, idx)"
            ></span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="log in pagedLogs" :key="log.id">
          <td>{{ typeIconMap[log.event_type] + LogType[log.event_type] }}</td>
          <td class="log-content-cell">{{ log.description }}</td>
          <td>{{ formatTimestamp(log.timestamp) }}</td>
          <td><button @click="viewDetail(log)">查看</button></td>
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
        <template v-if="detailLog && detailLog.log">
          <!-- 非法用户弹窗 -->
          <template v-if="detailLog.log.event_type === 0">
            <p><strong>事件类型：</strong>{{ typeIconMap[detailLog.log.event_type] }} 非法用户</p>
            <p><strong>日志ID：</strong>{{ detailLog.log.id }}</p>
            <p><strong>时间戳：</strong>{{ detailLog.log.timestamp }}</p>
            <p><strong>描述：</strong>{{ detailLog.log.description }}</p>
            <div v-if="detailLog.detail">
              <p v-if="detailLog.detail.face_data"><strong>人脸数据：</strong>{{ detailLog.detail.face_data }}</p>
              <p v-if="detailLog.detail.liveness_score !== undefined"><strong>活体检测分数：</strong>{{ detailLog.detail.liveness_score }}</p>
              <p v-if="detailLog.detail.spoofing_score !== undefined"><strong>欺诈检测分数：</strong>{{ detailLog.detail.spoofing_score }}</p>
            </div>
          </template>
          <!-- 人脸欺诈弹窗 -->
          <template v-else-if="detailLog.log.event_type === 1">
            <p><strong>事件类型：</strong>{{ typeIconMap[detailLog.log.event_type] }} 人脸欺诈</p>
            <p><strong>日志ID：</strong>{{ detailLog.log.id }}</p>
            <p><strong>时间戳：</strong>{{ detailLog.log.timestamp }}</p>
            <p><strong>描述：</strong>{{ detailLog.log.description }}</p>
            <div v-if="detailLog.detail">
              <p v-if="detailLog.detail.face_data"><strong>人脸数据：</strong>{{ detailLog.detail.face_data }}</p>
              <p v-if="detailLog.detail.liveness_score !== undefined"><strong>活体检测分数：</strong>{{ detailLog.detail.liveness_score }}</p>
              <p v-if="detailLog.detail.spoofing_score !== undefined"><strong>欺诈检测分数：</strong>{{ detailLog.detail.spoofing_score }}</p>
            </div>
          </template>
          <!-- 道路安全弹窗 -->
          <template v-else-if="detailLog.log.event_type === 2">
            <p><strong>事件类型：</strong>{{ typeIconMap[detailLog.log.event_type] }} 道路安全</p>
            <p><strong>日志ID：</strong>{{ detailLog.log.id }}</p>
            <p><strong>时间戳：</strong>{{ detailLog.log.timestamp }}</p>
            <p><strong>描述：</strong>{{ detailLog.log.description }}</p>
            <div v-if="detailLog.detail">
              <p v-if="detailLog.detail.danger_nums !== undefined"><strong>危险物品数量：</strong>{{ detailLog.detail.danger_nums }}</p>
              <p v-if="detailLog.detail.predicted_image"><strong>模型预测图片：</strong><img :src="detailLog.detail.predicted_image" alt="预测图片" style="max-width: 120px;" /></p>
            </div>
            <div v-if="detailLog.dangers && detailLog.dangers.length">
              <h4>危险详情：</h4>
              <ul>
                <li v-for="danger in detailLog.dangers" :key="danger.danger_id">
                  <span>类型：{{ danger.type }}，置信度：{{ danger.confidence }}</span>
                </li>
              </ul>
            </div>
          </template>
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

async function viewDetail(log) {
  // 可加loading状态
  const detail = await queryLogDetail(log.id)
  if (detail) {
    detailLog.value = detail
    showDetailModal.value = true
  } else {
    alert('获取日志详情失败')
  }
}
function closeDetailModal() {
  showDetailModal.value = false
}

// 时间格式化到秒
function formatTimestamp(ts) {
  if (!ts) return ''
  // 支持2025-07-09 10:10:00.123或2025-07-09T10:10:00.123Z等
  const match = ts.match(/^(.{19})/)
  return match ? match[1] : ts
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

// 监听类型切换，重新查询日志
watch(selectedType, () => {
  loadLogs()
})

// 监听日期变化，重新查询日志
watch([startTime, endTime], () => {
  loadLogs()
})

// 拖拽列宽相关
const columns = [
  { key: 'type', title: '类型' },
  { key: 'description', title: '日志内容' },
  { key: 'timestamp', title: '创建时间' },
  { key: 'detail', title: '详情' }
]
const defaultWidths = [120, 400, 180, 80]
const colWidths = ref([...defaultWidths])
let resizing = false
let startX = 0
let startWidth = 0
let colIdx = 0
function startResize(e, idx) {
  resizing = true
  startX = e.clientX
  startWidth = colWidths.value[idx]
  colIdx = idx
  document.addEventListener('mousemove', onResize)
  document.addEventListener('mouseup', stopResize)
}
function onResize(e) {
  if (!resizing) return
  const delta = e.clientX - startX
  colWidths.value[colIdx] = Math.max(60, startWidth + delta)
}
function stopResize() {
  resizing = false
  document.removeEventListener('mousemove', onResize)
  document.removeEventListener('mouseup', stopResize)
}

onMounted(() => {
  loadLogs()
})
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
  table-layout: fixed;
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
.log-table th,
.log-table td,
.log-content-cell {
  min-width: 60px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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
.resizable-th {
  position: relative;
  user-select: none;
  padding-right: 0;
}
.resize-handle {
  position: absolute;
  right: 0;
  top: 0;
  width: 6px;
  height: 100%;
  cursor: col-resize;
  z-index: 2;
  background: transparent;
}
</style>

