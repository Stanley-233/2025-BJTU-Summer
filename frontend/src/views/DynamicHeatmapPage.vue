<template>
  <div class="dynamic-heatmap-layout">
    <!-- 顶部控制栏 -->
    <header class="control-header">
      <div class="header-left">
        <button @click="goBack" class="back-btn">
          <i class="fas fa-arrow-left"></i> 返回
        </button>
        <h1>动态热力图 - 2013/09/12</h1>
      </div>
      
      <div class="header-center">
        <div class="time-display">
          <span class="current-time">{{ currentTimeDisplay }}</span>
        </div>
      </div>
      
      <div class="header-right">
        <div class="control-buttons">
          <button @click="togglePlay" :class="['play-btn', { playing: isPlaying }]">
            <i :class="isPlaying ? 'fas fa-pause' : 'fas fa-play'"></i>
            {{ isPlaying ? '暂停' : '播放' }}
          </button>
          <button @click="resetAnimation" class="reset-btn">
            <i class="fas fa-redo"></i> 重置
          </button>
          <button @click="clearCache" class="cache-btn">
            <i class="fas fa-trash"></i> 清除缓存
          </button>
        </div>
        
        <div class="speed-control">
          <label>播放速度:</label>
          <select v-model="playSpeed" @change="updateSpeed">
            <option value="0.5">0.5x</option>
            <option value="1">1x</option>
            <option value="2">2x</option>
            <option value="4">4x</option>
            <option value="8">8x</option>
          </select>
        </div>
      </div>
    </header>
    
    <!-- 时间轴控制 -->
    <div class="timeline-control">
      <div class="timeline-wrapper">
        <div class="timeline-labels">
          <span v-for="hour in 24" :key="hour" class="hour-label">
            {{ String(hour - 1).padStart(2, '0') }}:00
          </span>
        </div>
        <div class="timeline-slider">
          <input 
            type="range" 
            min="0" 
            max="23.5" 
            step="0.5" 
            v-model="currentHour" 
            @input="onTimelineChange"
            class="slider"
          />
          <div class="timeline-progress" :style="{ width: progressWidth }"></div>
        </div>
      </div>
    </div>
    
    <!-- 地图区域 -->
    <main class="map-container">
      <div id="dynamic-map" class="map"></div>
      
      <!-- 数据统计面板 -->
      <div class="stats-panel">
        <div class="stat-item">
          <span class="stat-label">当前时间:</span>
          <span class="stat-value">{{ currentTimeDisplay }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">数据点数:</span>
          <span class="stat-value">{{ currentDataPoints }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">最大密度:</span>
          <span class="stat-value">{{ maxDensity }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">缓存大小:</span>
          <span class="stat-value">{{ dataCache.size }}/{{ cacheSize }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">状态:</span>
          <span class="stat-value">{{ loadingStatus }}</span>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();

// 地图实例
let map = null;
let mapvglView = null;
let heatmapLayer = null;

// 控制状态
const isPlaying = ref(false);
const currentHour = ref(0);
const playSpeed = ref(2); // 默认播放速度提高到2x
const currentDataPoints = ref(0);
const maxDensity = ref(0);
const loadingStatus = ref('准备就绪');

// 动画控制 - 优化时间跨度和播放速度
let animationTimer = null;
const animationStep = 0.5; // 增大时间跨度：每次增加0.5小时（30分钟）
const maxHours = 24; // 全天24小时

// 数据缓存机制
const dataCache = new Map(); // 缓存热力图数据
const cacheSize = 48; // 缓存48个时间段（每30分钟一个）
const preloadBuffer = 3; // 预加载缓冲区大小

// API配置
const API_BASE_URL = 'http://localhost:8000';

// 计算属性
const currentTimeDisplay = computed(() => {
  const hour = Math.floor(currentHour.value);
  const minute = Math.floor((currentHour.value % 1) * 60);
  return `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;
});

const progressWidth = computed(() => {
  return `${(currentHour.value / 23) * 100}%`;
});

// 返回上一页
const goBack = () => {
  router.go(-1);
};

// 初始化地图
const initMap = () => {
  map = new BMapGL.Map('dynamic-map');
  const jinanCenter = new BMapGL.Point(117.000923, 36.675807);
  map.centerAndZoom(jinanCenter, 11);
  map.enableScrollWheelZoom(true);
  
  // 添加控件
  map.addControl(new BMapGL.NavigationControl());
  map.addControl(new BMapGL.ScaleControl());
  
  // 初始化MapVGL
  if (window.mapvgl) {
    mapvglView = new mapvgl.View({ map: map });
    initHeatmapLayer();
  }
};

// 初始化热力图层 - 参考DataAnalysisPage.vue的实现
const initHeatmapLayer = () => {
  heatmapLayer = new mapvgl.HeatmapLayer({
    size: 2000, // 热力图点的大小
    max: 100,   // 最大值，将在updateHeatmapData中动态设置
    height: 0,
    unit: 'm',
    gradient: {
      // 参考DataAnalysisPage.vue的渐变色配置
      0.0: 'rgba(0, 80, 255, 0.5)',
      0.1: 'rgba(0, 120, 255, 0.6)',
      0.2: 'rgba(0, 160, 255, 0.7)',
      0.3: 'rgba(0, 200, 255, 0.75)',
      0.4: 'rgba(0, 240, 255, 0.8)',
      0.45: 'rgba(0, 255, 220, 0.82)',
      0.5: 'rgba(0, 255, 180, 0.85)',
      0.55: 'rgba(40, 255, 140, 0.87)',
      0.6: 'rgba(80, 255, 100, 0.88)',
      0.65: 'rgba(120, 255, 60, 0.9)',
      0.7: 'rgba(160, 255, 20, 0.92)',
      0.75: 'rgba(200, 255, 0, 0.93)',
      0.8: 'rgba(240, 255, 0, 0.94)',
      0.85: 'rgba(255, 240, 0, 0.95)',
      0.88: 'rgba(255, 220, 0, 0.96)',
      0.9: 'rgba(255, 200, 0, 0.97)',
      0.92: 'rgba(255, 180, 0, 0.98)',
      0.94: 'rgba(255, 140, 0, 0.95)',
      0.96: 'rgba(255, 100, 0, 0.97)',
      0.98: 'rgba(255, 60, 0, 0.985)',
      0.99: 'rgba(255, 30, 0, 0.995)',
      1.0: 'rgba(255, 0, 0, 1.0)'
    },
    opacity: 0.8
  });
  
  mapvglView.addLayer(heatmapLayer);
};

// 获取指定时间的热力图数据 - 使用新的API接口
const fetchHeatmapDataForTime = async (hour) => {
  try {
    // 生成缓存键
    const cacheKey = Math.floor(hour * 2) / 2; // 按30分钟间隔缓存
    
    // 检查缓存
    if (dataCache.has(cacheKey)) {
      const cachedData = dataCache.get(cacheKey);
      updateHeatmapData(cachedData.data);
      currentDataPoints.value = cachedData.dataPoints;
      maxDensity.value = cachedData.maxDensity;
      loadingStatus.value = '缓存数据';
      return;
    }
    
    loadingStatus.value = '加载中...';
    
    // 构建北京时间范围 - 扩大时间窗口到30分钟
    const startHour = Math.floor(hour);
    const startMinute = Math.floor((hour % 1) * 60);
    const endMinute = Math.min(startMinute + 29, 59);
    
    const startTime = `2013-09-12 ${String(startHour).padStart(2, '0')}:${String(startMinute).padStart(2, '0')}:00`;
    const endTime = `2013-09-12 ${String(startHour).padStart(2, '0')}:${String(endMinute).padStart(2, '0')}:59`;
    
    const response = await axios.get(`${API_BASE_URL}/taxi/dynamic-heatmap-data`, {
      params: {
        start_time: startTime,
        end_time: endTime,
        max_points: 8000, // 增加数据点数量
        grid_size: 0.003  // 减小网格大小，提高精度
      }
    });
    
    if (response.data && response.data.length > 0) {
      const dataPoints = response.data.length;
      const maxDens = Math.max(...response.data.map(p => p.count));
      
      // 缓存数据
      if (dataCache.size >= cacheSize) {
        // 删除最旧的缓存项
        const firstKey = dataCache.keys().next().value;
        dataCache.delete(firstKey);
      }
      
      dataCache.set(cacheKey, {
        data: response.data,
        dataPoints: dataPoints,
        maxDensity: maxDens
      });
      
      updateHeatmapData(response.data);
      currentDataPoints.value = dataPoints;
      maxDensity.value = maxDens;
      loadingStatus.value = '数据已加载';
      
      // 预加载相邻时间段的数据
      preloadAdjacentData(cacheKey);
    } else {
      clearHeatmapData();
      currentDataPoints.value = 0;
      maxDensity.value = 0;
      loadingStatus.value = '无数据';
    }
  } catch (error) {
    console.error('获取热力图数据失败:', error);
    loadingStatus.value = '加载失败';
  }
};

// 预加载相邻时间段数据
const preloadAdjacentData = async (currentCacheKey) => {
  const preloadTasks = [];
  
  for (let i = 1; i <= preloadBuffer; i++) {
    const nextKey = currentCacheKey + 0.5 * i;
    const prevKey = currentCacheKey - 0.5 * i;
    
    if (nextKey < maxHours && !dataCache.has(nextKey)) {
      preloadTasks.push(preloadDataForKey(nextKey));
    }
    
    if (prevKey >= 0 && !dataCache.has(prevKey)) {
      preloadTasks.push(preloadDataForKey(prevKey));
    }
  }
  
  // 异步预加载，不阻塞当前播放
  Promise.all(preloadTasks).catch(error => {
    console.warn('预加载数据失败:', error);
  });
};

// 预加载指定时间段的数据
const preloadDataForKey = async (cacheKey) => {
  try {
    const hour = cacheKey;
    const startHour = Math.floor(hour);
    const startMinute = Math.floor((hour % 1) * 60);
    const endMinute = Math.min(startMinute + 29, 59);
    
    const startTime = `2013-09-12 ${String(startHour).padStart(2, '0')}:${String(startMinute).padStart(2, '0')}:00`;
    const endTime = `2013-09-12 ${String(startHour).padStart(2, '0')}:${String(endMinute).padStart(2, '0')}:59`;
    
    const response = await axios.get(`${API_BASE_URL}/taxi/dynamic-heatmap-data`, {
      params: {
        start_time: startTime,
        end_time: endTime,
        max_points: 8000,
        grid_size: 0.003
      }
    });
    
    if (response.data && response.data.length > 0) {
      const dataPoints = response.data.length;
      const maxDens = Math.max(...response.data.map(p => p.count));
      
      if (dataCache.size < cacheSize) {
        dataCache.set(cacheKey, {
          data: response.data,
          dataPoints: dataPoints,
          maxDensity: maxDens
        });
      }
    }
  } catch (error) {
    // 静默处理预加载错误
  }
};

// 更新热力图数据 - 参考DataAnalysisPage.vue的实现
const updateHeatmapData = (data) => {
  if (!heatmapLayer) return;
  
  // 计算实际数据的最大count值，动态设置max参数
  const maxCount = Math.max(...data.map(point => point.count));
  const dynamicMax = Math.max(maxCount * 1.2, 10);
  
  // 更新热力图的max参数
  heatmapLayer.setOptions({ max: dynamicMax });
  
  // 转换数据格式
  const mapData = data.map(point => ({
    geometry: {
      type: 'Point',
      coordinates: [point.lng, point.lat]
    },
    properties: {
      count: point.count
    }
  }));
  
  heatmapLayer.setData(mapData);
};

// 清除热力图数据
const clearHeatmapData = () => {
  if (heatmapLayer) {
    heatmapLayer.setData([]);
  }
};

// 播放/暂停控制
const togglePlay = () => {
  isPlaying.value = !isPlaying.value;
  
  if (isPlaying.value) {
    startAnimation();
  } else {
    stopAnimation();
  }
};

// 开始动画 - 优化播放速度
const startAnimation = () => {
  if (animationTimer) clearInterval(animationTimer);
  
  // 根据播放速度调整间隔，基础间隔为500ms（对应30分钟时间跨度）
  const baseInterval = 500;
  const interval = baseInterval / playSpeed.value;
  
  animationTimer = setInterval(() => {
    currentHour.value += animationStep;
    
    if (currentHour.value >= maxHours) {
      currentHour.value = 0; // 循环播放
    }
    
    fetchHeatmapDataForTime(currentHour.value);
  }, interval);
};

// 停止动画
const stopAnimation = () => {
  if (animationTimer) {
    clearInterval(animationTimer);
    animationTimer = null;
  }
};

// 重置动画 - 清除缓存选项
const resetAnimation = () => {
  stopAnimation();
  isPlaying.value = false;
  currentHour.value = 0;
  fetchHeatmapDataForTime(0);
};

// 清除缓存
const clearCache = () => {
  dataCache.clear();
  loadingStatus.value = '缓存已清除';
  fetchHeatmapDataForTime(currentHour.value);
};

// 更新播放速度
const updateSpeed = () => {
  if (isPlaying.value) {
    stopAnimation();
    startAnimation();
  }
};

// 时间轴变化
const onTimelineChange = () => {
  fetchHeatmapDataForTime(currentHour.value);
};

// 监听当前小时变化
watch(currentHour, (newHour) => {
  if (!isPlaying.value) {
    fetchHeatmapDataForTime(newHour);
  }
});

// 组件挂载 - 预加载初始数据
onMounted(() => {
  initMap();
  // 加载初始数据并预加载相邻数据
  setTimeout(() => {
    fetchHeatmapDataForTime(0);
  }, 1000);
});

// 组件卸载 - 清理缓存
onUnmounted(() => {
  stopAnimation();
  dataCache.clear();
  if (mapvglView) {
    mapvglView.destroy();
  }
});
</script>

<style scoped>
.dynamic-heatmap-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.control-header {
  background: white;
  padding: 15px 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 1000;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.back-btn {
  padding: 8px 15px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.back-btn:hover {
  background: #5a6268;
}

.header-left h1 {
  margin: 0;
  color: #333;
  font-size: 1.5rem;
}

.header-center {
  flex: 1;
  text-align: center;
}

.time-display {
  background: #007bff;
  color: white;
  padding: 10px 20px;
  border-radius: 20px;
  font-size: 1.2rem;
  font-weight: bold;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.control-buttons {
  display: flex;
  gap: 10px;
}

.play-btn, .reset-btn {
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: bold;
}

.play-btn {
  background: #28a745;
  color: white;
}

.play-btn.playing {
  background: #ffc107;
  color: #333;
}

.reset-btn {
  background: #dc3545;
  color: white;
}

.play-btn:hover, .reset-btn:hover {
  transform: translateY(-1px);
}

.speed-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.speed-control select {
  padding: 5px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.timeline-control {
  background: white;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.timeline-wrapper {
  position: relative;
}

.timeline-labels {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 0.9rem;
  color: #666;
}

.timeline-slider {
  position: relative;
  height: 40px;
}

.slider {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  background: #ddd;
  outline: none;
  -webkit-appearance: none;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #007bff;
  cursor: pointer;
}

.timeline-progress {
  position: absolute;
  top: 6px;
  left: 0;
  height: 8px;
  background: linear-gradient(90deg, #007bff, #28a745);
  border-radius: 4px;
  transition: width 0.3s;
  pointer-events: none;
}

.map-container {
  flex: 1;
  position: relative;
}

.map {
  width: 100%;
  height: 100%;
}

.stats-panel {
  position: absolute;
  top: 20px;
  right: 20px;
  background: rgba(255, 255, 255, 0.95);
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  min-width: 200px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.stat-label {
  color: #666;
}

.stat-value {
  font-weight: bold;
  color: #333;
}

.cache-btn {
  background: #6f42c1;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: bold;
}

.cache-btn:hover {
  background: #5a32a3;
  transform: translateY(-1px);
}

.dynamic-btn {
  background: linear-gradient(45deg, #ff6b6b, #ee5a24);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s;
  margin-left: 10px;
}

.dynamic-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.4);
}

.dynamic-btn i {
  margin-right: 5px;
}
</style>