<template>
  <div class="log-table-wrapper" :style="{ '--row-count': logRecords.length }">
    <div class="log-table-controls">
      <label class="date-label">开始时间：
        <input type="datetime-local" v-model="startTime" class="date-input" @change="onStartTimeChange" />
      </label>
      <label class="date-label">结束时间：
        <input type="datetime-local" v-model="endTime" class="date-input" @change="onEndTimeChange" />
      </label>
      <div class="pagination-bar-inline">
        <button :disabled="currentPage <= 1" @click="goPrevPage">上一页</button>
        <span>第 {{ currentPage }} / {{ totalPages }} 页</span>
        <button :disabled="currentPage >= totalPages" @click="goNextPage">下一页</button>
      </div>
    </div>
    <table class="log-table" :style="{ tableLayout: 'fixed' }">
      <thead>
      <tr>
        <th :style="{ width: columnWidths[0] + 'px' }" class="clickable-type-th" @click="toggleTypeDropdown" ref="typeTh">
          类型
          <span class="dropdown-arrow">▼</span>
          <div v-if="showTypeDropdown" class="type-dropdown">
            <div class="type-option" @click.stop="selectType(null)">全部</div>
            <div class="type-option" v-for="(icon, type) in typeIconMap" :key="type" @click.stop="selectType(type)">
              {{ icon }} {{ LogType[type] }}
            </div>
          </div>
          <div class="resize-handle" @mousedown.prevent="initResize($event, 0)"></div>
        </th>
        <th :style="{ width: columnWidths[1] + 'px' }">操作用户
          <div class="resize-handle" @mousedown.prevent="initResize($event, 1)"></div>
        </th>
        <th :style="{ width: columnWidths[2] + 'px' }">日志内容
          <div class="resize-handle" @mousedown.prevent="initResize($event, 2)"></div>
        </th>
        <th :style="{ width: columnWidths[3] + 'px' }" class="clickable-level-th" @click="toggleLevelDropdown" ref="levelTh">
          事件等级
          <span class="dropdown-arrow">▼</span>
          <div v-if="showLevelDropdown" class="type-dropdown">
            <div class="type-option" @click.stop="selectLevel(null)">全部</div>
            <div class="type-option" v-for="(label, level) in LogLevel" :key="level" @click.stop="selectLevel(level)">
              {{ label }}
            </div>
          </div>
          <div class="resize-handle" @mousedown.prevent="initResize($event, 3)"></div>
        </th>
        <th :style="{ width: columnWidths[4] + 'px' }">创建时间
          <div class="resize-handle" @mousedown.prevent="initResize($event, 4)"></div>
        </th>
        <th :style="{ width: columnWidths[5] + 'px' }">详情
        </th>
      </tr>
      </thead>
      <transition :name="slideTransitionName" mode="out-in">
        <tbody :key="currentPage">
          <tr v-for="log in logRecords" :key="log.id">
            <td :style="{ width: columnWidths[0] + 'px' }">{{ typeIconMap[log.event_type] + LogType[log.event_type] }}</td>
            <td :style="{ width: columnWidths[1] + 'px' }">{{ log.event_type === 3 ? log.link_username : '' }}</td>
            <td :style="{ width: columnWidths[2] + 'px' }">{{ log.description }}</td>
            <td :style="{ width: columnWidths[3] + 'px' }" :class="['log-level-cell', 'log-level-' + log.log_level]">
              {{ LogLevel[log.log_level] ?? '-' }}
            </td>
            <td :style="{ width: columnWidths[4] + 'px' }">{{ formatTimestamp(log.timestamp) }}</td>
            <td :style="{ width: columnWidths[5] + 'px' }">
              <button v-if="log.event_type !== 3" class="action-btn" @click="viewDetail(log)">查看</button>
              <button v-else style="opacity:0;pointer-events:none;">占位</button>
            </td>
          </tr>
        </tbody>
      </transition>
    </table>
    <!-- 日志详情弹窗 -->
    <div v-if="showDetailModal" class="modal-overlay modal-overlay-block" @click.self="isLoadingDetail ? null : closeDetailModal">
      <div v-if="isLoadingDetail" class="modal-loading-spinner">
        <div class="spinner"></div>
        <div class="loading-text">加载中…</div>
      </div>
      <div v-else class="modal-content">
        <h3>日志详情</h3>
        <template v-if="detailLog && detailLog.log">
          <p v-if="detailLog.log.event_type !== undefined"><strong>类型：</strong>{{ typeIconMap[detailLog.log.event_type] }} {{ LogType[detailLog.log.event_type] }}</p>
          <p v-if="detailLog.log.id"><strong>日志ID：</strong>{{ detailLog.log.id }}</p>
          <p v-if="detailLog.log.timestamp"><strong>时间：</strong>{{ formatTimestamp(detailLog.log.timestamp) }}</p>
          <p v-if="detailLog.log.description"><strong>描述：</strong>{{ detailLog.log.description }}</p>
          <div v-if="detailLog.detail">
            <!-- 删除原有face_data字符串显示 -->
            <button v-if="detailLog.detail.face_data" class="action-btn" @click="showFaceVideo = true">显示人脸视频</button>
            <p v-if="detailLog.detail.liveness_score !== undefined && detailLog.detail.liveness_score !== null && detailLog.detail.liveness_score !== ''"><strong>活体检测分数：</strong>{{ detailLog.detail.liveness_score }}</p>
            <p v-if="detailLog.detail.spoofing_score !== undefined && detailLog.detail.spoofing_score !== null && detailLog.detail.spoofing_score !== ''"><strong>欺诈检测分数：</strong>{{ detailLog.detail.spoofing_score }}</p>
            <p v-if="detailLog.detail.danger_nums !== undefined && detailLog.detail.danger_nums !== null && detailLog.detail.danger_nums !== ''"><strong>危险物品数量：</strong>{{ detailLog.detail.danger_nums }}</p>
            <button v-if="detailLog.detail.predicted_image" class="action-btn" @click="showDangerImage = true">显示危险视频</button>
          </div>
          <div v-if="detailLog.dangers && detailLog.dangers.length" class="danger-detail-card">
            <h4 class="danger-detail-title">危险详情</h4>
            <table class="danger-detail-table">
              <thead>
                <tr>
                  <th>类型</th>
                  <th>置信度</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="d in detailLog.dangers" :key="d.danger_id">
                  <td>
                    <span v-if="d.type !== undefined && d.type !== null" class="danger-type">
                      {{ dangerTypeMap[d.type] ?? d.type }}
                    </span>
                  </td>
                  <td>
                    <span v-if="d.confidence !== undefined && d.confidence !== null && d.confidence !== ''" class="danger-confidence">
                      {{ formatConfidence(d.confidence) }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>
        <button class="close-btn" @click="closeDetailModal">关闭</button>
      </div>
    </div>
    <!-- 危险视频弹窗（原危险图片弹窗） -->
    <div v-if="showDangerImage && detailLog && detailLog.detail && detailLog.detail.predicted_image" class="danger-image-modal" @click.self="showDangerImage = false">
      <div class="danger-image-content">
        <video controls :src="'data:video/mp4;base64,' + detailLog.detail.predicted_image" style="max-width:60vw;max-height:60vh;border-radius:6px;margin-bottom:12px;box-shadow:0 2px 8px rgba(79,55,138,0.08);"></video>
        <button class="close-btn" @click="showDangerImage = false">关闭视频</button>
      </div>
    </div>
    <!-- 人脸视频弹窗 -->
    <div v-if="showFaceVideo && detailLog && detailLog.detail && detailLog.detail.face_data" class="danger-image-modal" @click.self="showFaceVideo = false">
      <div class="danger-image-content">
        <template v-if="decryptedFaceVideo">
          <video controls :src="'data:video/mp4;base64,' + decryptedFaceVideo" style="max-width:60vw;max-height:60vh;border-radius:6px;margin-bottom:12px;box-shadow:0 2px 8px rgba(79,55,138,0.08);"></video>
        </template>
        <template v-else>
          <div style="color:#e61714;font-weight:500;">人脸视频解密失败</div>
        </template>
        <button class="close-btn" @click="showFaceVideo = false">关闭视频</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, computed, onMounted, watch, inject} from 'vue'
import { queryLogs, queryLogDetail, queryLogCount } from '../viewmodels/LogViewModel'
import CryptoJS from "crypto-js";

const showGlobalBubble = inject('showGlobalBubble')
const LogType = {
  0: '非法用户',
  1: '人脸欺诈',
  2: '道路安全',
  3: '操作事件', // 新增
}

const typeIconMap = {
  0: '🔒',
  1: '😡',
  2: '🚧',
  3: '📝', // 新增
}

const LogLevel = {
  0: '信息',
  1: '警告',
  2: '错误',
}

const dangerTypeMap = {
  0: '🚧水平',
  1: '🚧垂直',
  2: '🚧裂隙',
  3: '🚧坑洼',
  4: '🚧补丁'
}

const logRecords = ref([])

function setLogs(list) {
  logRecords.value = Array.isArray(list) ? list : []
}

// 下拉筛选相关
const showTypeDropdown = ref(false)
const showLevelDropdown = ref(false)
const selectedType = ref(null)
const selectedLevel = ref(null)
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
  // 立即刷新并重定向到第一页
  slideTransitionName.value = 'slide-left';
  currentPage.value = 1;
  loadLogs();
}


const showDetailModal = ref(false)
const detailLog = ref(null)
const isLoadingDetail = ref(false)
const showDangerImage = ref(false)
const showFaceVideo = ref(false)

// 缓存解密后的人脸视频base64
const decryptedFaceVideo = computed(() => {
  if (detailLog.value && detailLog.value.detail && detailLog.value.detail.face_data) {
    return decryptFaceData(detailLog.value.detail.face_data)
  }
  return null
})
// 点击查看详情时获取详细数据
async function viewDetail(log) {
  showDetailModal.value = true;
  isLoadingDetail.value = true;
  detailLog.value = null;
  showFaceVideo.value = false;
  try {
    const detail = await queryLogDetail(log.id);
    if (detail) {
      detailLog.value = detail;
    }
  } catch (e) {
    console.error(e);
    alert('获取日志详情失败');
    showDetailModal.value = false;
  } finally {
    isLoadingDetail.value = false;
  }
}
function closeDetailModal() {
  showDetailModal.value = false
  showFaceVideo.value = false
}

// 格式化时间到秒
function formatTimestamp(ts) {
  if (!ts) return ''
  const m = ts.match(/^(.{19})/)
  const str = m ? m[1] : ts
  return str.replace('T', ' ')
}

function formatConfidence(val) {
  const num = Number(val);
  if (isNaN(num)) return val;
  return (num * 100).toFixed(2) + '%';
}

// AES解密函数
function decryptFaceData(encrypted) {
  try {
    const bytes = CryptoJS.AES.decrypt(encrypted, 'BrPz0VgQzNmhw1KmHfEyUFu1DHnq0schBijdSm0P_K0=')
    let decrypted = bytes.toString()
    if (decrypted.startsWith('"') && decrypted.endsWith('"')) {
      decrypted = decrypted.slice(1, -1);
    }
    alert(decrypted === encrypted)
    return decrypted;
  } catch (e) {
    return null;
  }
}

const pageSize = 10
const totalLogs = ref(1);
const totalPages = ref(1);
const currentPage = ref(1);

const slideTransitionName = ref('slide-left');
let lastPage = 1;

function goPrevPage() {
  if (currentPage.value > 1) {
    slideTransitionName.value = 'slide-right';
    currentPage.value--;
    loadLogs();
  }
}
function goNextPage() {
  if (currentPage.value < totalPages.value) {
    slideTransitionName.value = 'slide-left';
    currentPage.value++;
    loadLogs();
  }
}
// 监听筛选条件变化，自动加载日志
async function loadLogs() {
  try {
    // 格式化时间范围
    let logRange = null
    if (startTime.value && endTime.value) {
      logRange = `${startTime.value.replace('T', ' ').slice(0, 16)}~${endTime.value.replace('T', ' ').slice(0, 16)}`
    }
    totalLogs.value = await queryLogCount(selectedType.value, logRange, selectedLevel.value, showGlobalBubble)
    totalPages.value = Math.max(1, Math.ceil(totalLogs.value / pageSize))
    if (currentPage.value > totalPages.value) currentPage.value = totalPages.value
    if (currentPage.value < 1) currentPage.value = 1
    const logs = await queryLogs(selectedType.value, logRange, pageSize, (currentPage.value - 1) * pageSize, selectedLevel.value, showGlobalBubble)
    setLogs(logs || [])
  } catch (e) {
    console.error('加载日志失败', e)
    setLogs([])
  }
}

onMounted(() => {
  loadLogs()
})

watch(
  () => ({
    type: selectedType.value,
    level: selectedLevel.value,
    start: startTime.value,
    end: endTime.value
  }),
  () => {
    // 筛选条件变化时，重置为第一页，动画为左滑
    slideTransitionName.value = 'slide-left';
    currentPage.value = 1;
    loadLogs();
  }
)

// 通用监听：下拉框由开变关时刷新
watch(showTypeDropdown, (val, oldVal) => {
  // 类型下拉关闭时无需手动刷新，已由 selectType 处理
})
watch(showLevelDropdown, (val, oldVal) => {
  if (oldVal && !val) {
    slideTransitionName.value = 'slide-left';
    currentPage.value = 1;
    loadLogs();
  }
})
// column resize state
const columnWidths = ref([120, 80, 240, 100, 160, 60])
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

function toggleLevelDropdown() {
  showLevelDropdown.value = !showLevelDropdown.value
}
function selectLevel(level) {
  selectedLevel.value = level === null ? null : Number(level)
  showLevelDropdown.value = false
  // 立即刷新并重定向到第一页
  slideTransitionName.value = 'slide-left';
  currentPage.value = 1;
  loadLogs();
}

function handleClickOutside(event) {
  let needRefresh = false;
  if (
    !event.target.closest('.clickable-type-th') &&
    !event.target.closest('.type-dropdown') &&
    !event.target.closest('.clickable-level-th')
  ) {
    if (showTypeDropdown.value) {
      showTypeDropdown.value = false;
      // 类型下拉关闭无需手动刷新，已由selectType处理
    }
    if (showLevelDropdown.value) {
      showLevelDropdown.value = false;
      // 危险等级下拉关闭时，重置为第一页并刷新
      slideTransitionName.value = 'slide-left';
      currentPage.value = 1;
      loadLogs();
    }
  }
}
if (typeof window !== 'undefined') {
  window.addEventListener('click', handleClickOutside)
}
</script>

<style scoped>
.log-table-wrapper {
  width: 100%;
  box-sizing: border-box;
}
.log-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  box-shadow: 0 2px 8px rgba(79,55,138,0.04);
  border-radius: 6px;
  font-size: 0.9em; /* reduced font size */
  margin-bottom: 8px; /* 原来是24px，改小 */
  min-height: 120px; /* 新增，防止下拉被裁剪 */
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
  z-index: 100; /* 提高层级，防止被遮挡 */
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
  gap: 8px;
  margin-bottom: 4px;
  justify-content: flex-start;
  position: relative;
}
.date-label {
  color: #4F378A;
  font-size: 0.95em;
  font-weight: 500;
  white-space: nowrap;
  margin-right: 4px;
}
.date-input {
  margin-left: 4px;
  padding: 2px 6px;
  border: 1px solid #ede7f6;
  border-radius: 4px;
  background: #f7f7fa;
  font-size: 0.93em;
  color: #4F378A;
  outline: none;
  transition: border 0.2s;
  height: 28px;
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
.pagination-bar-inline {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: auto;
  font-size: 0.97em;
  white-space: nowrap;
}
.pagination-bar-inline button {
  background: #a97ef8;
  color: #fff;
  font-size: 15px;
  font-weight: 500;
  border: none;
  border-radius: 6px;
  padding: 1px 10px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
  height: 28px;
  box-shadow: 0 2px 8px rgba(58,90,215,0.08);
}
.pagination-bar-inline button:hover:not(:disabled) {
  background: #964ff1;
  color: #fff;
}
.pagination-bar-inline button:disabled {
  background: #ede7f6;
  color: #aaa;
  cursor: not-allowed;
  box-shadow: none;
}
.pagination-bar-inline span {
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
.danger-detail-card {
  background: #f7f7fa;
  border: 1.5px solid #ede7f6;
  border-radius: 4px;
  padding: 2px 8px 6px 8px;
  margin-top: 2px;
  box-shadow: 0 1px 4px rgba(79,55,138,0.03);
}
.danger-detail-title {
  color: #b71c1c;
  font-size: 1.08em;
  margin-top: 2px;
  margin-bottom: 8px;
  font-weight: 600;
  letter-spacing: 1px;
}
.danger-detail-table {
  width: 100%;
  border-collapse: collapse;
  background: transparent;
}
.danger-detail-table th, .danger-detail-table td {
  border-bottom: 1px solid #ede7f6;
  padding: 2px 6px;
  text-align: left;
  font-size: 0.92em;
  line-height: 1.3;
}
.danger-detail-table th {
  color: #4F378A;
  font-weight: 600;
  background: #ede7f6;
  padding-top: 3px;
  padding-bottom: 3px;
}
.danger-detail-table tr:last-child td {
  border-bottom: none;
}
.danger-type {
  font-weight: 500;
  color: #d84315;
}
.danger-confidence {
  color: #1565c0;
  font-weight: 500;
}
/* 日志等级颜色 */
.log-level-cell {
  font-weight: 600;
}
.log-level-cell.log-level-0 { color: #33abf6 !important; }
.log-level-cell.log-level-1 { color: #FF9800 !important; }
.log-level-cell.log-level-2 { color: #e61714 !important; }
.action-btn {
  font-family: inherit;
  font-size: 16px;
  font-weight: 500;
  border: none;
  border-radius: 6px;
  background: #4F378A;
  color: #fff;
  padding: 2px 14px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
  height: 32px;
  box-shadow: 0 2px 8px rgba(79,55,138,0.08);
}
.action-btn:hover {
  background: #6c4bb6;
  color: #fff;
}
.fade-table-enter-active, .fade-table-leave-active {
  transition: opacity 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}
.fade-table-enter-from, .fade-table-leave-to {
  opacity: 0;
}
.fade-table-enter-to, .fade-table-leave-from {
  opacity: 1;
}
.slide-left-enter-active, .slide-left-leave-active,
.slide-right-enter-active, .slide-right-leave-active {
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}
.slide-left-enter-from {
  opacity: 0;
  transform: translateX(40px);
}
.slide-left-enter-to {
  opacity: 1;
  transform: translateX(0);
}
.slide-left-leave-from {
  opacity: 1;
  transform: translateX(0);
}
.slide-left-leave-to {
  opacity: 0;
  transform: translateX(-40px);
}
.slide-right-enter-from {
  opacity: 0;
  transform: translateX(-40px);
}
.slide-right-enter-to {
  opacity: 1;
  transform: translateX(0);
}
.slide-right-leave-from {
  opacity: 1;
  transform: translateX(0);
}
.slide-right-leave-to {
  opacity: 0;
  transform: translateX(40px);
}
.modal-overlay-block {
  pointer-events: auto;
}
.modal-loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100vw;
  height: 100vh;
  z-index: 1100;
}
.spinner {
  width: 48px;
  height: 48px;
  border: 5px solid #ede7f6;
  border-top: 5px solid #4F378A;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.loading-text {
  color: #4F378A;
  font-size: 1.1em;
  font-weight: 500;
  letter-spacing: 1px;
}
.danger-image-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0,0,0,0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
.danger-image-content {
  background: #fff;
  border-radius: 8px;
  padding: 18px 18px 12px 18px;
  box-shadow: 0 4px 24px rgba(79,55,138,0.18);
  display: flex;
  flex-direction: column;
  align-items: center;
}
.danger-image-content img {
  max-width: 60vw;
  max-height: 60vh;
  border-radius: 6px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(79,55,138,0.08);
}
.log-table {
  min-height: 320px; /* 10行*32px，可根据实际调整 */
}
.log-table tbody {
  position: relative;
}
.log-table tbody::after {
  content: '';
  display: block;
  height: calc(320px - (var(--row-count, 0) * 32px));
  min-height: 0;
  background: #fff;
}
</style>
