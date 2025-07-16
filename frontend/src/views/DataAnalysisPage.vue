<template>
  <div class="analysis-layout">
    <!-- 左侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2>济南出租车数据分析</h2>
      </div>
      
      <!-- 导航标签页 -->
      <div class="nav-tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.key"
          :class="['nav-tab', { active: activeTab === tab.key }]"
          @click="switchTab(tab.key)"
        >
          <i :class="tab.icon"></i>
          {{ tab.label }}
        </button>
      </div>
      
      <!-- 动态内容区域 -->
      <div class="tab-content">
        <!-- 热力图分析页面 -->
        <div v-if="activeTab === 'heatmap'" class="tab-panel">
          <div class="sidebar-panel">
            <div class="panel-title">热力图控制</div>
            <div class="control-item">
              <button @click="toggleHeatmap" class="control-btn">{{ showHeatmap ? '隐藏热力图' : '显示热力图' }}</button>
            </div>
            <div class="control-item">
              <button @click="loadDefaultHeatmap" class="control-btn">重新加载热力图</button>
            </div>
          </div>
          
          <div class="sidebar-panel">
            <div class="panel-title">密集上客区域</div>
            <div class="control-item">
              <button @click="fetchPickupClusters" class="control-btn">显示密集上客区域</button>
            </div>
            <div class="control-item">
              <button @click="clearPickupClusterMarkers" class="control-btn">清除上客区域标记</button>
            </div>
          </div>
          
          <div class="sidebar-panel">
            <div class="panel-title">地图控制</div>
            <div class="control-item">
              <button @click="fitToData" class="control-btn">适应数据范围</button>
            </div>
            <div class="control-item">
              <button @click="resetMap" class="control-btn">重置地图</button>
            </div>
          </div>
          
          <!-- 数据状态面板 -->
          <div class="sidebar-panel">
            <div class="panel-title">数据状态</div>
            <div class="stat-item">
              <span>状态：{{ dataStatus }}</span>
            </div>
            <div class="stat-item">
              <span>数据点总数：{{ totalDataPoints }}</span>
            </div>
            <div class="stat-item">
              <span>最大密度：{{ maxDensity }}</span>
            </div>
            <div class="stat-item">
              <span>坐标范围：{{ coordinateRange }}</span>
            </div>
          </div>
        </div>
        
        <!-- 时间范围分析页面 -->
        <div v-if="activeTab === 'timerange'" class="tab-panel">
          <div class="sidebar-panel">
            <div class="panel-title">北京时间范围查询 (2013/09/12)</div>
            <div class="time-inputs">
              <div class="time-input-group">
                <label>起始时间:</label>
                <input 
                  type="datetime-local" 
                  v-model="beijingTimeStart" 
                  class="time-input"
                />
              </div>
              <div class="time-input-group">
                <label>结束时间:</label>
                <input 
                  type="datetime-local" 
                  v-model="beijingTimeEnd" 
                  class="time-input"
                />
              </div>
            </div>
            <div class="time-controls">
              <button @click="fetchBeijingTimeHeatmap" :disabled="isBeijingTimeLoading" class="apply-btn">
                {{ isBeijingTimeLoading ? '加载中...' : '查询热力图' }}
              </button>
              <button @click="clearBeijingTimeHeatmap" class="clear-btn">清除热力图</button>
            </div>
            <div class="preset-buttons">
              <button @click="setPresetBeijingTime('morning_rush')" class="preset-btn">早高峰(7-9点)</button>
              <button @click="setPresetBeijingTime('noon')" class="preset-btn">中午(11-13点)</button>
              <button @click="setPresetBeijingTime('evening_rush')" class="preset-btn">晚高峰(17-19点)</button>
              <button @click="setPresetBeijingTime('night')" class="preset-btn">夜间(20-22点)</button>
              <button @click="setPresetBeijingTime('all_day')" class="preset-btn">全天</button>
            </div>
          </div>
          
          <!-- 时间统计面板 -->
          <div class="sidebar-panel" v-if="beijingTimeStats">
            <div class="panel-title">时间统计</div>
            <div class="beijing-stats">
              <div class="stat-item">
                <span>北京时间范围: {{ beijingTimeStats.time_range }}</span>
              </div>
              <div class="stat-item">
                <span>总行程数: {{ beijingTimeStats.total_trips }}</span>
              </div>
              <div class="stat-item">
                <span>车辆数: {{ beijingTimeStats.unique_vehicles }}</span>
              </div>
              <div class="stat-item">
                <span>平均距离: {{ beijingTimeStats.avg_distance }}km</span>
              </div>
              
            </div>
          </div>
          
          <!-- 数据状态面板 -->
          <div class="sidebar-panel">
            <div class="panel-title">数据状态</div>
            <div class="stat-item">
              <span>状态：{{ dataStatus }}</span>
            </div>
            <div class="stat-item">
              <span>当前显示：{{ beijingTimeStats ? '北京时间过滤数据' : '默认热力图' }}</span>
            </div>
          </div>
        </div>
        
        <!-- 车辆轨迹分析页面 -->
        <div v-if="activeTab === 'trajectory'" class="tab-panel">
          <div class="sidebar-panel">
            <div class="panel-title">车辆轨迹查询</div>
            <div class="track-inputs">
              <div class="input-group">
                <label>车牌号:</label>
                <input 
                  type="text" 
                  v-model="vehicleId" 
                  placeholder="请输入车牌号"
                  class="vehicle-input"
                />
              </div>
              <div class="time-input-group">
                <label>起始时间:</label>
                <input 
                  type="datetime-local" 
                  v-model="trackStartTime" 
                  class="time-input"
                />
              </div>
              <div class="time-input-group">
                <label>结束时间:</label>
                <input 
                  type="datetime-local" 
                  v-model="trackEndTime" 
                  class="time-input"
                />
              </div>
            </div>
            <div class="track-controls">
              <button @click="queryVehicleTrack" :disabled="isTrackLoading" class="apply-btn">
                {{ isTrackLoading ? '查询中...' : '查询轨迹' }}
              </button>
              <button @click="clearVehicleTrack" class="clear-btn">清除轨迹</button>
            </div>
          </div>
          
          <!-- 轨迹统计面板 -->
          <div class="sidebar-panel" v-if="trackStats">
            <div class="panel-title">轨迹统计</div>
            <div class="track-stats">
              <div class="stat-item">
                <span>轨迹点数: {{ trackStats.point_count }}</span>
              </div>
              <div class="stat-item">
                <span>总距离: {{ trackStats.total_distance }}km</span>
              </div>
              <div class="stat-item">
                <span>总时长: {{ trackStats.total_duration }}分钟</span>
              </div>
            </div>
          </div>
          
          <!-- 数据状态面板 -->
          <div class="sidebar-panel">
            <div class="panel-title">数据状态</div>
            <div class="stat-item">
              <span>查询状态：{{ isTrackLoading ? '查询中...' : '就绪' }}</span>
            </div>
            <div class="stat-item">
              <span>当前车辆：{{ vehicleId || '未选择' }}</span>
            </div>
            <div class="stat-item">
              <span>轨迹显示：{{ trackStats ? '已显示' : '无轨迹' }}</span>
            </div>
          </div>
        </div>
        
        <!-- 数据统计页面 -->
        <div v-if="activeTab === 'statistics'" class="tab-panel">
          <div class="sidebar-panel">
            <div class="panel-title">数据概览</div>
            <div class="stat-item">
              <span>聚类数量：{{ clusterCount }}</span>
            </div>
            <div class="stat-item">
              <span>数据点总数：{{ totalDataPoints }}</span>
            </div>
            <div class="stat-item">
              <span>最大密度：{{ maxDensity }}</span>
            </div>
            <div class="stat-item">
              <span>坐标范围：{{ coordinateRange }}</span>
            </div>
          </div>
          
          <div class="sidebar-panel">
            <div class="panel-title">数据操作</div>
            <div class="control-item">
              <button @click="checkDataDistribution" class="control-btn">检查数据分布</button>
            </div>
            <div class="control-item">
              <button @click="loadDefaultHeatmap" class="control-btn">重新加载数据</button>
            </div>
          </div>
          
          <!-- 系统状态面板 -->
          <div class="sidebar-panel">
            <div class="panel-title">系统状态</div>
            <div class="stat-item">
              <span>数据状态：{{ dataStatus }}</span>
            </div>
            <div class="stat-item">
              <span>加载状态：{{ isLoading ? '加载中' : '就绪' }}</span>
            </div>
            <div class="stat-item">
              <span>热力图：{{ showHeatmap ? '显示中' : '已隐藏' }}</span>
            </div>
          </div>
        </div>
      </div>
    </aside>
    
    <!-- 右侧地图主区域 -->
    <main class="map-main">
      <div id="analysis-map-container" class="map"></div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';

// 地图和热力图实例
let map = null;
let mapvglView = null;
let heatmapLayer = null;
let vehicleMarkers = [];
let vehiclePolyline = null;

// 控制参数
// 控制参数 - 调整为区域级别显示
const heatmapIntensity = ref(60);  // 降低强度
const heatmapRadius = ref(25);     // 增大半径：从10改为25
const showHeatmap = ref(true);
const isLoading = ref(false);
const isTrackLoading = ref(false);

// 北京时间过滤参数
const beijingTimeStart = ref('');
const beijingTimeEnd = ref('');
const isBeijingTimeLoading = ref(false);
const beijingTimeHeatmapPoints = ref([]);
const showBeijingTimeHeatmap = ref(false);
const beijingTimeStats = ref(null);
const beijingTimeHeatmapLayer = ref(null);

// 密集上客区域参数
const showPickupClusters = ref(false);
const pickupClusterMarkers = ref([]);

// 车辆轨迹查询参数
const vehicleId = ref('');
const trackStartTime = ref('');
const trackEndTime = ref('');
const trackStats = ref(null);

// 数据状态
const dataStatus = ref('准备就绪');
const clusterCount = ref(0);
const totalDataPoints = ref(0);
const maxDensity = ref(0);
const coordinateRange = ref('');

// 真实数据点
const realDataPoints = ref([]);

// API基础URL
const API_BASE_URL = 'http://localhost:8000';

// 新增：标签页管理
const activeTab = ref('heatmap');
const tabs = ref([
  { key: 'heatmap', label: '热力图分析', icon: 'fas fa-fire' },
  { key: 'timerange', label: '时间分析', icon: 'fas fa-clock' },
  { key: 'trajectory', label: '轨迹分析', icon: 'fas fa-route' },
  { key: 'statistics', label: '数据统计', icon: 'fas fa-chart-bar' }
]);

// 切换标签页
const switchTab = (tabKey) => {
  activeTab.value = tabKey;
  
  // 根据不同标签页执行相应的初始化操作
  switch(tabKey) {
    case 'heatmap':
      if (!showHeatmap.value) {
        loadDefaultHeatmap();
      }
      // 清除北京时间热力图
      clearBeijingTimeHeatmap();
      break;
    case 'timerange':
      // 可以在这里初始化时间相关的数据
      break;
    case 'trajectory':
      // 清除之前的轨迹显示
      clearVehicleTrack();
      // 清除密集上客区域标记
      clearPickupClusterMarkers();
      // 清除北京时间热力图
      clearBeijingTimeHeatmap();
      // 隐藏热力图以提供更清晰的轨迹查看体验
      if (showHeatmap.value && heatmapLayer && mapvglView) {
        mapvglView.removeLayer(heatmapLayer);
        showHeatmap.value = false;
      }
      break;
    case 'statistics':
      // 可以在这里刷新统计数据
      break;
  }
};

// 初始化地图
const initMap = async () => {
  // 创建地图实例
  map = new BMapGL.Map('analysis-map-container');
  
  // 设置济南市中心坐标
  const jinanCenter = new BMapGL.Point(117.000923, 36.675807);
  map.centerAndZoom(jinanCenter, 11);
  
  // 启用滚轮缩放
  map.enableScrollWheelZoom(true);
  
  // 添加控件
  map.addControl(new BMapGL.NavigationControl());
  map.addControl(new BMapGL.ScaleControl());
  
  // 自定义地图样式 - 已注释以使用默认样式
  /*
  try {
    const response = await fetch('/custom_map_config.json');
    const mapStyle = await response.json();
    map.setMapStyleV2({ styleJson: mapStyle });
    console.log('自定义地图样式加载成功');
  } catch (error) {
    console.error('加载自定义地图样式失败:', error);
    dataStatus.value = '地图样式加载失败，使用默认样式';
  }
  */
  
  initHeatmap();
  
  loadDefaultHeatmap();
};

// 初始化热力图
const initHeatmap = () => {
  if (!window.mapvgl) {
    console.error('MapVGL库未加载');
    dataStatus.value = 'MapVGL库未加载，请检查引入';
    return;
  }
  
  try {
    mapvglView = new mapvgl.View({ map: map });
    
    // 创建热力图图层 - 移除固定的max参数，将在updateHeatmapData中动态设置
    heatmapLayer = new mapvgl.HeatmapLayer({
      size: heatmapRadius.value * 80,
      // max: 500, // 移除固定值，改为动态设置
      height: 0,
      unit: 'm',
      gradient: {
        // 蓝色区域 (0.0 - 0.4) - 低密度区域，增加透明度
        0.0: 'rgba(0, 80, 255, 0.5)',      // 从0.2增加到0.5
        0.1: 'rgba(0, 120, 255, 0.6)',     // 从0.3增加到0.6
        0.2: 'rgba(0, 160, 255, 0.7)',     // 从0.4增加到0.7
        0.3: 'rgba(0, 200, 255, 0.75)',    // 从0.5增加到0.75
        0.4: 'rgba(0, 240, 255, 0.8)',     // 从0.6增加到0.8
        
        // 黄色区域 (0.4 - 0.92) - 中密度区域，增加透明度
        0.45: 'rgba(0, 255, 220, 0.82)',   // 从0.65增加到0.82
        0.5: 'rgba(0, 255, 180, 0.85)',    // 从0.7增加到0.85
        0.55: 'rgba(40, 255, 140, 0.87)',  // 从0.72增加到0.87
        0.6: 'rgba(80, 255, 100, 0.88)',   // 从0.75增加到0.88
        0.65: 'rgba(120, 255, 60, 0.9)',   // 从0.78增加到0.9
        0.7: 'rgba(160, 255, 20, 0.92)',   // 从0.8增加到0.92
        0.75: 'rgba(200, 255, 0, 0.93)',   // 从0.82增加到0.93
        0.8: 'rgba(240, 255, 0, 0.94)',    // 从0.85增加到0.94
        0.85: 'rgba(255, 240, 0, 0.95)',   // 从0.87增加到0.95
        0.88: 'rgba(255, 220, 0, 0.96)',   // 从0.89增加到0.96
        0.9: 'rgba(255, 200, 0, 0.97)',    // 从0.91增加到0.97
        0.92: 'rgba(255, 180, 0, 0.98)',   // 从0.93增加到0.98
        
        // 橙色过渡区域 (0.92 - 0.98) - 高密度区域，保持原有透明度
        0.94: 'rgba(255, 140, 0, 0.95)',   // 橙色
        0.96: 'rgba(255, 100, 0, 0.97)',   
        0.98: 'rgba(255, 60, 0, 0.985)',   // 橙红色
        
        // 红色区域 (0.98 - 1.0) - 极少数最高密度区域，保持原有透明度
        0.99: 'rgba(255, 30, 0, 0.995)',   // 深红色
        1.0: 'rgba(255, 0, 0, 1.0)'        // 纯红色（最高密度）
      },
      opacity: heatmapIntensity.value / 100
    });
    
    mapvglView.addLayer(heatmapLayer);
    console.log('MapVGL热力图初始化成功');
  } catch (error) {
    console.error('MapVGL热力图初始化失败:', error);
    dataStatus.value = 'MapVGL热力图初始化失败';
  }
};

// 更新热力图数据
const updateHeatmapData = () => {
  if (!heatmapLayer || realDataPoints.value.length === 0) return;
  
  // 计算实际数据的最大count值
  const maxCount = Math.max(...realDataPoints.value.map(point => point.count));
  const dynamicMax = Math.max(maxCount * 1.2, 10); // 设置为最大值的1.2倍，最小为10
  
  console.log(`动态设置热力图max值: ${dynamicMax} (实际最大count: ${maxCount})`);
  
  // 更新热力图的max参数
  heatmapLayer.setOptions({
    max: dynamicMax
  });
  
  const data = realDataPoints.value.map(point => ({
    geometry: {
      type: 'Point',
      coordinates: [point.lng, point.lat]
    },
    properties: {
      count: point.count
    }
  }));
  
  heatmapLayer.setData(data);
};

// 通用热力图数据获取函数
const fetchHeatmapData = async (url, params, successCallback, errorCallback) => {
  try {
    isLoading.value = true;
    dataStatus.value = '正在加载热力图数据...';
    
    const response = await axios.get(`${API_BASE_URL}${url}`, { params });
    
    if (response.data && response.data.length > 0) {
      const processedData = processHeatmapData(response.data);
      updateStats(response.data);
      
      if (successCallback) {
        successCallback(processedData);
      }
      
      dataStatus.value = `热力图数据加载完成 (${response.data.length}个点)`;
    } else {
      dataStatus.value = '无可用的热力图数据';
    }
  } catch (error) {
    console.error('获取热力图数据失败:', error);
    dataStatus.value = `热力图数据加载失败: ${error.message}`;
    
    if (errorCallback) {
      errorCallback(error);
    }
  } finally {
    isLoading.value = false;
  }
};

// 通用热力图图层创建函数
const createHeatmapLayer = (data, options = {}) => {
  if (!mapvglView || data.length === 0) return null;
  
  // 计算实际数据的最大count值
  const maxCount = Math.max(...data.map(point => point.count));
  const dynamicMax = Math.max(maxCount * 1.2, 10); // 设置为最大值的1.2倍，最小为10
  
  // 创建热力图数据
  const mapData = data.map(point => ({
    geometry: {
      type: 'Point',
      coordinates: [point.lng, point.lat]
    },
    properties: {
      count: point.count
    }
  }));
  
  // 默认配置
  const defaultOptions = {
    size: heatmapRadius.value * 80,
    max: dynamicMax,
    unit: 'm',
    gradient: {
      0.0: 'rgba(50, 50, 255, 0.0)',
      0.1: 'rgba(50, 50, 255, 0.5)',
      0.2: 'rgba(0, 100, 255, 0.6)',
      0.3: 'rgba(0, 150, 255, 0.7)',
      0.4: 'rgba(0, 200, 255, 0.8)',
      0.5: 'rgba(0, 255, 255, 0.9)',
      0.6: 'rgba(0, 255, 200, 0.9)',
      0.7: 'rgba(0, 255, 100, 0.9)',
      0.8: 'rgba(0, 255, 0, 0.9)',
      0.9: 'rgba(255, 255, 0, 0.9)',
      1.0: 'rgba(255, 0, 0, 1.0)'
    },
    opacity: heatmapIntensity.value / 100
  };
  
  // 合并选项
  const mergedOptions = { ...defaultOptions, ...options };
  
  // 创建热力图图层
  const layer = new mapvgl.HeatmapLayer(mergedOptions);
  layer.setData(mapData);
  
  return layer;
};

// 更新热力图参数
const updateHeatmap = () => {
  if (!heatmapLayer) return;
  
  // 更新热力图配置 - 使用更大的半径倍数
  heatmapLayer.setOptions({
    size: heatmapRadius.value * 80,  // 从*50改为*80
    opacity: heatmapIntensity.value / 100
  });
};

// 切换热力图显示
const toggleHeatmap = () => {
  if (!heatmapLayer || !mapvglView) return;
  
  if (showHeatmap.value) {
    mapvglView.removeLayer(heatmapLayer);
    showHeatmap.value = false;
  } else {
    mapvglView.addLayer(heatmapLayer);
    showHeatmap.value = true;
  }
};

// 统一的数据处理函数
const processHeatmapData = (rawData) => {
  return rawData.map(point => ({
    lng: parseFloat(point.lng),
    lat: parseFloat(point.lat),
    count: Math.max(0.1, point.count)  // 移除Math.min(500, ...)的限制
  }));
};

// 新增：平衡高低密度区域的数据处理函数
const processHeatmapDataWithFiltering = (rawData) => {
  // 首先进行基本处理
  const basicProcessed = rawData.map(point => ({
    lng: parseFloat(point.lng),
    lat: parseFloat(point.lat),
    count: Math.max(0.1, point.count)  // 移除Math.min(500, ...)的限制
  }));
  
  // 计算密度统计信息
  const counts = basicProcessed.map(p => p.count);
  const avgCount = counts.reduce((sum, c) => sum + c, 0) / counts.length;
  const sortedCounts = [...counts].sort((a, b) => a - b);
  const medianCount = sortedCounts[Math.floor(sortedCounts.length / 2)];
  const q25Count = sortedCounts[Math.floor(sortedCounts.length * 0.25)];
  const q75Count = sortedCounts[Math.floor(sortedCounts.length * 0.75)];
  const q90Count = sortedCounts[Math.floor(sortedCounts.length * 0.9)];
  const q95Count = sortedCounts[Math.floor(sortedCounts.length * 0.95)];
  const q98Count = sortedCounts[Math.floor(sortedCounts.length * 0.98)];
  
  console.log(`密度统计: 平均=${avgCount.toFixed(2)}, Q25=${q25Count.toFixed(2)}, 中位数=${medianCount.toFixed(2)}, Q75=${q75Count.toFixed(2)}, Q90=${q90Count.toFixed(2)}, Q95=${q95Count.toFixed(2)}, Q98=${q98Count.toFixed(2)}`);
  
  // 使用更宽松的基础筛选条件
  const lowDensityThreshold = Math.max(avgCount * 0.03, q25Count * 0.2);  // 进一步降低阈值
  const allFiltered = basicProcessed.filter(point => point.count >= lowDensityThreshold);
  
  // 按密度排序
  allFiltered.sort((a, b) => b.count - a.count);
  
  // 分层选择
  const ultraHighDensity = allFiltered.filter(p => p.count >= q98Count);
  const veryHighDensity = allFiltered.filter(p => p.count >= q95Count && p.count < q98Count);
  const highDensity = allFiltered.filter(p => p.count >= q90Count && p.count < q95Count);
  const mediumHighDensity = allFiltered.filter(p => p.count >= q75Count && p.count < q90Count);
  const mediumDensity = allFiltered.filter(p => p.count >= medianCount && p.count < q75Count);
  const lowMediumDensity = allFiltered.filter(p => p.count >= q25Count && p.count < medianCount);
  const lowDensity = allFiltered.filter(p => p.count >= lowDensityThreshold && p.count < q25Count);
  
  // 调整点数分配
  const selectedUltraHigh = ultraHighDensity.slice(0, 25);      
  const selectedVeryHigh = veryHighDensity.slice(0, 35);        
  const selectedHigh = highDensity.slice(0, 45);                
  const selectedMediumHigh = mediumHighDensity.slice(0, 70);    
  const selectedMedium = mediumDensity.slice(0, 140);           
  const selectedLowMedium = lowMediumDensity.slice(0, 280);     
  const selectedLow = lowDensity.slice(0, 600);                 
  
  // 优化人工低密度点生成，减少网格化效应
  const artificialLowDensityPoints = [];
  if (basicProcessed.length > 0) {
    const lngs = basicProcessed.map(p => p.lng);
    const lats = basicProcessed.map(p => p.lat);
    const minLng = Math.min(...lngs);
    const maxLng = Math.max(...lngs);
    const minLat = Math.min(...lats);
    const maxLat = Math.max(...lats);
    
    // 使用更小的网格步长和更多随机性
    const gridStep = 0.006; // 减小网格步长
    const baseCount = Math.min(q25Count * 0.25, 0.6);
    
    for (let lng = minLng; lng <= maxLng; lng += gridStep) {
      for (let lat = minLat; lat <= maxLat; lat += gridStep) {
        // 增加随机偏移，减少网格化效应
        const randomOffsetLng = (Math.random() - 0.5) * gridStep * 0.8;
        const randomOffsetLat = (Math.random() - 0.5) * gridStep * 0.8;
        
        // 随机跳过一些点，创建更自然的分布
        if (Math.random() > 0.7) {
          artificialLowDensityPoints.push({
            lng: lng + randomOffsetLng,
            lat: lat + randomOffsetLat,
            count: baseCount * (0.2 + Math.random() * 0.6)
          });
        }
      }
    }
    
    // 限制人工点数量
    artificialLowDensityPoints.splice(500);
  }
  
  const result = [
    ...selectedUltraHigh, 
    ...selectedVeryHigh, 
    ...selectedHigh, 
    ...selectedMediumHigh,
    ...selectedMedium,
    ...selectedLowMedium,
    ...selectedLow,
    ...artificialLowDensityPoints
  ];
  
  console.log(`优化连续性热力图结果:`);
  console.log(`超超高密度(红色)=${selectedUltraHigh.length}, 超高密度=${selectedVeryHigh.length}, 高密度=${selectedHigh.length}`);
  console.log(`中高密度=${selectedMediumHigh.length}, 中等密度=${selectedMedium.length}, 中低密度=${selectedLowMedium.length}`);
  console.log(`低密度=${selectedLow.length}, 人工低密度=${artificialLowDensityPoints.length}`);
  console.log(`总计=${result.length}个点`);
  
  return result;
};

// 加载默认热力图（只使用降级模式的OD数据API）
const loadDefaultHeatmap = async () => {
  if (!mapvglView) {
    dataStatus.value = 'MapVGL库未加载，请检查引入';
    return;
  }
  
  isLoading.value = true;
  dataStatus.value = '正在加载热力图数据...';
  
  try {
    console.log('使用聚类数据API...');
    const response = await axios.get(`${API_BASE_URL}/taxi/heatmap-data-clusters`, {
      params: {
        max_points: 1200,     // 增加点数以获得更自然分布
        grid_size: 0.005      // 减小网格以获得更自然分布
      }
    });
    
    if (response.data && response.data.length > 0) {
      const processedData = processHeatmapDataWithFiltering(response.data);
      realDataPoints.value = processedData;
      updateHeatmapData();
      updateStats(response.data);
      
      dataStatus.value = `热力图数据加载完成 (聚类模式: ${processedData.length}个点)`;
      console.log(`聚类模式热力图加载完成，共 ${processedData.length} 个数据点`);
    } else {
      dataStatus.value = '无可用的热力图数据';
    }
  } catch (error) {
    console.error('聚类数据API失败:', error);
    dataStatus.value = `热力图API不可用: ${error.message}`;
    
    if (error.code === 'ERR_NETWORK') {
      alert('网络连接失败，请检查后端服务是否启动在 http://localhost:8000');
    } else if (error.response) {
      alert(`服务器错误: ${error.response.status} - ${error.response.data?.detail || error.response.statusText}`);
    } else {
      alert(`请求失败: ${error.message}`);
    }
  } finally {
    isLoading.value = false;
  }
};

// 添加数据分布检查函数
const checkDataDistribution = async (data) => {
  if (data && data.length === 0) return;
  
  if (data) {
    const lats = data.map(p => p.lat);
    const latMin = Math.min(...lats);
    const latMax = Math.max(...lats);
    const latMid = (latMin + latMax) / 2;
    
    const northCount = data.filter(p => p.lat > latMid).length;
    const southCount = data.filter(p => p.lat <= latMid).length;
    
    console.log('数据分布检查:');
    console.log(`纬度范围: ${latMin.toFixed(4)} - ${latMax.toFixed(4)}`);
    console.log(`北部数据点: ${northCount} (${(northCount/data.length*100).toFixed(1)}%)`);
    console.log(`南部数据点: ${southCount} (${(southCount/data.length*100).toFixed(1)}%)`);
    
    if (northCount < southCount * 0.3) {
      console.warn('警告：北部数据点明显少于南部，可能存在数据分布不均问题');
    }
    return;
  }
  
  try {
    const response = await axios.get(`${API_BASE_URL}/taxi/data-distribution`);
    console.log('数据分布:', response.data);
    alert(`数据分布检查完成，详情请查看控制台`);
  } catch (error) {
    console.error('检查数据分布失败:', error);
    alert('检查数据分布失败');
  }
};

// UTC时间过滤相关函数（使用自适应聚合保留稀疏区域）
const fetchHeatmapDataUtc = async (startUtc, endUtc) => {
  try {
    isLoading.value = true;
    dataStatus.value = '正在加载时间范围数据...';
    
    // 优先使用自适应聚合API
    const response = await axios.get(`${API_BASE_URL}/taxi/heatmap-data-adaptive`, {
      params: {
        start_utc: startUtc,
        end_utc: endUtc,
        max_points: 15000,
        preserve_sparse: true  // 确保保留稀疏区域数据
      }
    });
    
    const data = response.data;
    
    realDataPoints.value = processHeatmapData(data);
    
    updateHeatmapData();
    updateStats(data);
    
    dataStatus.value = `时间范围数据加载完成 (${data.length}个点，已保留稀疏区域)`;
    
  } catch (error) {
    console.error('自适应API时间过滤失败，尝试原始API:', error);
    
    // 降级到原始UTC API
    try {
      let url = `${API_BASE_URL}/taxi/heatmap-data-utc`;
      const params = new URLSearchParams();
      
      if (startUtc && endUtc) {
        params.append('start_utc', startUtc);
        params.append('end_utc', endUtc);
      }
      
      if (params.toString()) {
        url += `?${params.toString()}`;
      }
      
      const response = await axios.get(url);
      const data = response.data;
      
      realDataPoints.value = processHeatmapData(data);
      
      updateHeatmapData();
      updateStats(data);
      
      dataStatus.value = `时间范围数据加载完成 (${data.length}个点，降级模式)`;
    } catch (fallbackError) {
      console.error('所有时间过滤API都失败:', fallbackError);
      dataStatus.value = '时间范围数据加载失败';
    }
  } finally {
    isLoading.value = false;
  }
};

// 获取UTC时间范围统计
const fetchUtcTimeStats = async (startUtc, endUtc) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/taxi/utc-time-stats?start_utc=${startUtc}&end_utc=${endUtc}`);
    utcTimeStats.value = response.data;
  } catch (error) {
    console.error('获取UTC时间统计失败:', error);
    utcTimeStats.value = null;
  }
};

// 查询车辆轨迹
const queryVehicleTrack = async () => {
  if (!vehicleId.value || !trackStartTime.value || !trackEndTime.value) {
    alert('请填写完整的查询条件');
    return;
  }
  
  isTrackLoading.value = true;
  
  try {
    const startTime = trackStartTime.value.replace('T', ' ') + ':00';
    const endTime = trackEndTime.value.replace('T', ' ') + ':00';
    
    const encodedStartTime = encodeURIComponent(startTime);
    const encodedEndTime = encodeURIComponent(endTime);
    
    const response = await axios.get(`${API_BASE_URL}/taxi/vehicle-track?vehicle_id=${vehicleId.value}&start_time=${encodedStartTime}&end_time=${encodedEndTime}`);
    const trackData = response.data;
    
    if (trackData.length === 0) {
      alert('未找到该车辆在指定时间范围内的轨迹数据');
      return;
    }
    
    // 清除之前的轨迹
    clearVehicleTrack();
    
    // 按时间排序确保轨迹连续性
    trackData.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    
    // 创建轨迹点
    const points = trackData.map(point => new BMapGL.Point(point.lng, point.lat));
    
    // 创建优化的轨迹线
    vehiclePolyline = new BMapGL.Polyline(points, {
      strokeColor: '#FF4444',
      strokeWeight: 4,
      strokeOpacity: 0.8,
      strokeStyle: 'solid'
    });
    map.addOverlay(vehiclePolyline);
    
    // 只添加起点和终点标记（使用简单图标）
    if (points.length > 0) {
      // 起点标记（绿色圆点）
      const startMarker = new BMapGL.Marker(points[0]);
      const startLabel = new BMapGL.Label('起点', {
        offset: new BMapGL.Size(10, -10)
      });
      startLabel.setStyle({
        color: 'white',
        backgroundColor: '#00AA00',
        border: '1px solid white',
        borderRadius: '3px',
        padding: '2px 5px',
        fontSize: '12px',
        fontWeight: 'bold'
      });
      startMarker.setLabel(startLabel);
      map.addOverlay(startMarker);
      vehicleMarkers.push(startMarker);
      
      // 终点标记（红色圆点）
      if (points.length > 1) {
        const endMarker = new BMapGL.Marker(points[points.length - 1]);
        const endLabel = new BMapGL.Label('终点', {
          offset: new BMapGL.Size(10, -10)
        });
        endLabel.setStyle({
          color: 'white',
          backgroundColor: '#FF0000',
          border: '1px solid white',
          borderRadius: '3px',
          padding: '2px 5px',
          fontSize: '12px',
          fontWeight: 'bold'
        });
        endMarker.setLabel(endLabel);
        map.addOverlay(endMarker);
        vehicleMarkers.push(endMarker);
      }
    }
    
    // 调整地图视野
    if (points.length > 0) {
      map.setViewport(points);
    }
    
    // 计算轨迹统计
    let totalDistance = 0;
    for (let i = 1; i < points.length; i++) {
      totalDistance += map.getDistance(points[i-1], points[i]);
    }
    
    // 计算轨迹统计时直接使用返回的时间戳
    const startTimeCalc = new Date(trackData[0].timestamp);
    const endTimeCalc = new Date(trackData[trackData.length - 1].timestamp);
    const totalDuration = (endTimeCalc - startTimeCalc) / (1000 * 60); // 分钟
    
    trackStats.value = {
      point_count: trackData.length,
      total_distance: (totalDistance / 1000).toFixed(2),
      total_duration: totalDuration.toFixed(0)
    };
    
  } catch (error) {
    console.error('查询车辆轨迹失败:', error);
    alert('查询车辆轨迹失败');
  } finally {
    isTrackLoading.value = false;
  }
};

// 清除车辆轨迹
const clearVehicleTrack = () => {
  // 清除标记点
  vehicleMarkers.forEach(marker => {
    map.removeOverlay(marker);
  });
  vehicleMarkers = [];
  
  // 清除轨迹线
  if (vehiclePolyline) {
    map.removeOverlay(vehiclePolyline);
    vehiclePolyline = null;
  }
  
  trackStats.value = null;
};

// 应用UTC时间过滤
const applyUtcTimeFilter = async () => {
  if (!startUtcTime.value || !endUtcTime.value) {
    alert('请选择起始和结束时间');
    return;
  }
  
  const startUtc = new Date(startUtcTime.value).toISOString().slice(0, 19).replace('T', ' ');
  const endUtc = new Date(endUtcTime.value).toISOString().slice(0, 19).replace('T', ' ');
  
  await fetchHeatmapData(
    '/taxi/heatmap-data-utc',
    {
      start_utc: startUtc,
      end_utc: endUtc,
      max_points: 15000,
      grid_size: 0.005
    },
    (processedData) => {
      realDataPoints.value = processedData;
      updateHeatmapData();
      fetchUtcTimeStats(startUtc, endUtc);
    }
  );
};

// 清除UTC时间过滤
const clearUtcTimeFilter = async () => {
  startUtcTime.value = '';
  endUtcTime.value = '';
  utcTimeStats.value = null;
  // 回到默认的0912当天数据显示
  await loadDefaultHeatmap();
};

// 设置预设UTC时间
const setPresetUtcTime = async (preset) => {
  // 数据集日期：2013年9月12日
  let start, end;
  
  switch (preset) {
    case 'today':
      // 0912全天 (00:00:00 到 23:59:59)
      start = '2013-09-12T00:00';
      end = '2013-09-12T23:59';
      break;
    case 'yesterday':
      // 0911全天（如果有数据的话）
      start = '2013-09-11T00:00';
      end = '2013-09-11T23:59';
      break;
    case 'last_hour':
      // 0912当天22-23点
      start = '2013-09-12T22:00';
      end = '2013-09-12T23:00';
      break;
    case 'morning':
      // 0912早高峰 (7-9点)
      start = '2013-09-12T07:00';
      end = '2013-09-12T09:00';
      break;
    case 'evening':
      // 0912晚高峰 (17-19点)
      start = '2013-09-12T17:00';
      end = '2013-09-12T19:00';
      break;
  }
  
  startUtcTime.value = start;
  endUtcTime.value = end;
  
  await applyUtcTimeFilter();
};

// UTC时间变化处理
const onUtcTimeChange = () => {
  // 可以在这里添加实时预览逻辑
};

// 保留第265-310行之间的原始函数定义

// 适应数据范围
const fitToData = () => {
  if (!map || realDataPoints.value.length === 0) return;
  
  const points = realDataPoints.value.map(point => 
    new BMapGL.Point(point.lng, point.lat)
  );
  
  map.setViewport(points);
};

// 重置地图
const resetMap = () => {
  if (!map) return;
  
  const jinanCenter = new BMapGL.Point(117.000923, 36.675807);
  map.centerAndZoom(jinanCenter, 11);
  
  clearVehicleTrack();
};

// 更新统计信息
const updateStats = (data) => {
  clusterCount.value = data.length;
  totalDataPoints.value = data.reduce((sum, point) => sum + point.count, 0);
  maxDensity.value = Math.max(...data.map(p => p.count));
  
  if (data.length > 0) {
    const lngs = data.map(p => p.lng);
    const lats = data.map(p => p.lat);
    const minLng = Math.min(...lngs);
    const maxLng = Math.max(...lngs);
    const minLat = Math.min(...lats);
    const maxLat = Math.max(...lats);
    coordinateRange.value = `经度:${minLng.toFixed(3)}-${maxLng.toFixed(3)}, 纬度:${minLat.toFixed(3)}-${maxLat.toFixed(3)}`;
  }
};

// 组件挂载
onMounted(() => {
  // 确保百度地图API和MapVGL库已加载
  if (typeof BMapGL !== 'undefined') {
    if (typeof mapvgl !== 'undefined') {
      initMap();
    } else {
      console.error('MapVGL库未加载，请检查index.html中的引入');
      dataStatus.value = 'MapVGL库未加载';
    }
  } else {
    console.error('百度地图API未加载');
    dataStatus.value = '百度地图API未加载';
  }
});

// 获取密集上客区域数据
const fetchPickupClusters = async () => {
  await fetchHeatmapData(
    '/taxi/heatmap-data-cluster',
    { max_points: 50 },
    (processedData) => {
      // 清除之前的标记
      clearPickupClusterMarkers();
      
      // 添加新的标记
      processedData.forEach((point, index) => {
        // 创建自定义图标
        const size = Math.min(50, Math.max(20, Math.sqrt(point.count) * 0.8));
        const label = new BMapGL.Label(`上客点 #${index+1}\n${point.count}次`, {
          position: new BMapGL.Point(point.lng, point.lat),
          offset: new BMapGL.Size(size/2 + 5, 0)
        });
        
        label.setStyle({
          color: '#fff',
          backgroundColor: 'rgba(255, 0, 0, 0.8)',
          border: '1px solid #fff',
          padding: '2px 5px',
          borderRadius: '3px',
          fontSize: '12px',
          fontWeight: 'bold',
          zIndex: 3
        });
        
        // 创建圆形标记
        const circle = new BMapGL.Circle(
          new BMapGL.Point(point.lng, point.lat),
          size,
          {
            strokeColor: 'rgba(255, 0, 0, 0.8)',
            strokeWeight: 2,
            strokeOpacity: 0.8,
            fillColor: 'rgba(255, 0, 0, 0.5)',
            fillOpacity: 0.6
          }
        );
        
        map.addOverlay(circle);
        map.addOverlay(label);
        
        pickupClusterMarkers.value.push(circle);
        pickupClusterMarkers.value.push(label);
      });
      
      // 调整地图视野以包含所有标记
      const points = processedData.map(point => new BMapGL.Point(point.lng, point.lat));
      map.setViewport(points);
      
      showPickupClusters.value = true;
    }
  );
};

// 清除密集上客区域标记
const clearPickupClusterMarkers = () => {
  pickupClusterMarkers.value.forEach(marker => {
    map.removeOverlay(marker);
  });
  pickupClusterMarkers.value = [];
  showPickupClusters.value = false;
};

// 按北京时间筛选热力图数据
const fetchBeijingTimeHeatmap = async () => {
  if (!beijingTimeStart.value || !beijingTimeEnd.value) {
    alert('请选择起始和结束时间');
    return;
  }
  
  try {
    isBeijingTimeLoading.value = true;
    dataStatus.value = '正在加载北京时间热力图数据...';
    
    // 清除之前的热力图
    clearBeijingTimeHeatmap();
    
    // 解析北京时间字符串
    const startBJ = new Date(beijingTimeStart.value);
    const endBJ = new Date(beijingTimeEnd.value);
    
    // 直接格式化为数据库使用的格式 YYYY-MM-DD HH:MM:SS，保持北京时间
    const startBJStr = `${startBJ.getFullYear()}-${String(startBJ.getMonth() + 1).padStart(2, '0')}-${String(startBJ.getDate()).padStart(2, '0')} ${String(startBJ.getHours()).padStart(2, '0')}:${String(startBJ.getMinutes()).padStart(2, '0')}:00`;
    const endBJStr = `${endBJ.getFullYear()}-${String(endBJ.getMonth() + 1).padStart(2, '0')}-${String(endBJ.getDate()).padStart(2, '0')} ${String(endBJ.getHours()).padStart(2, '0')}:${String(endBJ.getMinutes()).padStart(2, '0')}:00`;
    
    // 获取热力图数据，使用新的API端点
    const response = await axios.get(`${API_BASE_URL}/taxi/heatmap-data-beijing`, {
      params: {
        start_time: startBJStr,
        end_time: endBJStr,
        max_points: 15000,
        grid_size: 0.005
      }
    });
    
    if (response.data && response.data.length > 0) {
      beijingTimeHeatmapPoints.value = processHeatmapData(response.data);
      
      // 创建新的热力图图层
      createBeijingTimeHeatmap();
      
      // 获取统计信息
      await fetchBeijingTimeStats(startBJStr, endBJStr);
      
      dataStatus.value = `北京时间热力图加载完成 (${response.data.length}个点)`;
    } else {
      dataStatus.value = '无可用的北京时间热力图数据';
    }
  } catch (error) {
    console.error('获取北京时间热力图数据失败:', error);
    dataStatus.value = `北京时间热力图数据加载失败: ${error.message}`;
  } finally {
    isBeijingTimeLoading.value = false;
  }
};

// 创建北京时间热力图图层
const createBeijingTimeHeatmap = () => {
  if (!mapvglView || beijingTimeHeatmapPoints.value.length === 0) return;
  
  // 计算实际数据的最大count值
  const maxCount = Math.max(...beijingTimeHeatmapPoints.value.map(point => point.count));
  const dynamicMax = Math.max(maxCount * 1.2, 10); // 设置为最大值的1.2倍，最小为10
  
  // 创建热力图数据
  const data = beijingTimeHeatmapPoints.value.map(point => ({
    geometry: {
      type: 'Point',
      coordinates: [point.lng, point.lat]
    },
    properties: {
      count: point.count
    }
  }));
  
  // 创建热力图图层
  beijingTimeHeatmapLayer.value = new mapvgl.HeatmapLayer({
    size: heatmapRadius.value * 80,
    max: dynamicMax,
    unit: 'm',
    gradient: {
      0.0: 'rgba(50, 50, 255, 0.0)',
      0.1: 'rgba(50, 50, 255, 0.5)',
      0.2: 'rgba(0, 100, 255, 0.6)',
      0.3: 'rgba(0, 150, 255, 0.7)',
      0.4: 'rgba(0, 200, 255, 0.8)',
      0.5: 'rgba(0, 255, 255, 0.9)',
      0.6: 'rgba(0, 255, 200, 0.9)',
      0.7: 'rgba(0, 255, 100, 0.9)',
      0.8: 'rgba(0, 255, 0, 0.9)',
      0.9: 'rgba(255, 255, 0, 0.9)',
      1.0: 'rgba(255, 0, 0, 1.0)'
    },
    opacity: heatmapIntensity.value / 100
  });
  
  beijingTimeHeatmapLayer.value.setData(data);
  mapvglView.addLayer(beijingTimeHeatmapLayer.value);
  showBeijingTimeHeatmap.value = true;
};

// 清除北京时间热力图
const clearBeijingTimeHeatmap = () => {
  if (beijingTimeHeatmapLayer.value && mapvglView) {
    mapvglView.removeLayer(beijingTimeHeatmapLayer.value);
    beijingTimeHeatmapLayer.value = null;
  }
  beijingTimeHeatmapPoints.value = [];
  beijingTimeStats.value = null;
  showBeijingTimeHeatmap.value = false;
};

// 获取北京时间统计信息
const fetchBeijingTimeStats = async (startTime, endTime) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/taxi/beijing-time-stats`, {
      params: {
        start_time: startTime,
        end_time: endTime
      }
    });
    beijingTimeStats.value = response.data;
  } catch (error) {
    console.error('获取北京时间统计信息失败:', error);
    beijingTimeStats.value = null;
  }
};

// 设置预设北京时间
const setPresetBeijingTime = (preset) => {
  // 数据集日期：2013年9月12日
  switch (preset) {
    case 'morning_rush':
      // 早高峰 (7:00-9:00)
      beijingTimeStart.value = '2013-09-12T07:00';
      beijingTimeEnd.value = '2013-09-12T09:00';
      break;
    case 'noon':
      // 中午 (11:00-13:00)
      beijingTimeStart.value = '2013-09-12T11:00';
      beijingTimeEnd.value = '2013-09-12T13:00';
      break;
    case 'evening_rush':
      // 晚高峰 (17:00-19:00)
      beijingTimeStart.value = '2013-09-12T17:00';
      beijingTimeEnd.value = '2013-09-12T19:00';
      break;
    case 'night':
      // 夜间 (20:00-22:00)
      beijingTimeStart.value = '2013-09-12T20:00';
      beijingTimeEnd.value = '2013-09-12T22:00';
      break;
    case 'all_day':
      // 全天 (00:00-23:59)
      beijingTimeStart.value = '2013-09-12T00:00';
      beijingTimeEnd.value = '2013-09-12T23:59';
      break;
  }
};

// 组件卸载
onUnmounted(() => {
  // 清理MapVGL资源
  if (mapvglView) {
    try {
      mapvglView.destroy();
    } catch (error) {
      console.error('MapVGL视图销毁失败:', error);
    }
    mapvglView = null;
  }
  
  // 清理地图资源
  if (map) {
    try {
      map.destroy();
    } catch (error) {
      console.error('地图销毁失败:', error);
    }
    map = null;
  }
  
  // 重置变量
  heatmapLayer = null;
  clearPickupClusterMarkers();
  clearBeijingTimeHeatmap();
});
</script>

<style scoped>
.analysis-layout {
  display: flex;
  height: 100vh;
  background: #f5f5f5;
  margin: 0;
  padding: 0;
}

.sidebar {
  width: 350px;
  background: white;
  border-right: 1px solid #e0e0e0;
  overflow-y: auto;
  flex-shrink: 0;
  margin: 0;
  padding: 0;
  position: relative;
  left: 0;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  background: #4F378A;  /* 这里设置了背景颜色为紫色 */
  color: #FFFFFF;       /* 使用纯白色 */
}

.sidebar-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #F0F0F0;       /* 使用更亮的白色 */
}

/* 新增：标签页导航样式 */
.nav-tabs {
  display: flex;
  flex-wrap: wrap;
  background: #4F378A; /* 修改为与标题背景相同的紫色 */
  border-bottom: 1px solid #e0e0e0;
}

.nav-tab {
  flex: 1;
  min-width: 0;
  padding: 12px 8px;
  border: none;
  background: transparent;
  color: white; /* 修改为白色，在紫色背景上更清晰 */
  font-size: 13px;
  font-weight: 600; /* 增加字体粗细 */
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 3px solid transparent;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.nav-tab:hover {
  background: rgba(255, 255, 255, 0.2); /* 修改悬停背景为半透明白色 */
  color: white; /* 悬停时保持白色 */
}

.nav-tab.active {
  background: rgba(255, 255, 255, 0.3); /* 激活状态使用更明显的半透明白色 */
  color: white; /* 激活状态使用白色 */
  border-bottom-color: white; /* 底部边框也改为白色 */
  font-weight: 700; /* 激活状态字体更粗 */
}

.nav-tab i {
  font-size: 16px; /* 增大图标尺寸 */
  margin-bottom: 2px;
  color: inherit; /* 图标颜色继承文字颜色 */
}

.tab-content {
  flex: 1;
}

.tab-panel {
  display: block;
}

.sidebar-panel {
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.sidebar-panel:last-child {
  border-bottom: none;
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 15px;
  color: #333;  /* 可以保持这个颜色，它是深灰色，应该有足够对比度 */
  border-left: 4px solid #4F378A;
  padding-left: 10px;
}

.time-inputs, .track-inputs {
  margin-bottom: 15px;
}

.time-input-group, .input-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-bottom: 12px;
}

.time-input-group label, .input-group label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.time-input, .vehicle-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.time-input:focus, .vehicle-input:focus {
  outline: none;
  border-color: #4F378A;
  box-shadow: 0 0 0 2px rgba(79, 55, 138, 0.1);
}

.time-controls, .track-controls {
  display: flex;
  gap: 8px;
  margin-bottom: 15px;
}

.apply-btn {
  background: #4F378A;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
  flex: 1;
}

.apply-btn:hover:not(:disabled) {
  background: #3d2a6b;
}

.apply-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.clear-btn {
  background: #6c757d;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
  flex: 1;
}

.clear-btn:hover {
  background: #5a6268;
}

.preset-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 15px;
}

.preset-btn {
  background: #28a745;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: background 0.2s;
}

.preset-btn:hover {
  background: #218838;
}

.control-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 14px;
}

.control-item span {
  color: #666;
  min-width: 80px;
}

.control-item input[type="range"] {
  flex: 1;
  margin: 0 8px;
}

.control-btn {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
  color: #2c3e50; /* 改为深色文字 */
  cursor: pointer;
  font-size: 14px;
  font-weight: 500; /* 增加字体粗细 */
  transition: all 0.2s;
  width: 100%;
}

.control-btn:hover {
  background: #f8f9fa;
  border-color: #4F378A;
  color: #4F378A; /* 悬停时使用主题色 */
}

.control-btn:active {
  background: #4F378A;
  color: white; /* 点击时反色显示 */
  border-color: #4F378A;
}

.utc-stats, .track-stats {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 12px;
  margin-top: 10px;
}

.stat-item {
  font-size: 13px;
  color: #666;
  margin-bottom: 6px;
  padding: 4px 0;
  border-bottom: 1px solid #e9ecef;
}

.stat-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.map-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin: 0;
  padding: 0;
}

.map {
  width: 100%;
  height: 100%;
  border: none;
  margin: 0;
  padding: 0;
}

/* 滚动条样式 */
.sidebar::-webkit-scrollbar {
  width: 6px;
}

.sidebar::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.sidebar::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.sidebar::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .sidebar {
    width: 300px;
  }
}

@media (max-width: 768px) {
  .analysis-layout {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    height: auto;
    max-height: 40vh;
  }
  
  .map-main {
    height: 60vh;
  }
}
</style>