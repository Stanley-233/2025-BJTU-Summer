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
            <div class="panel-title">时间范围查询</div>
            <div class="time-inputs">
              <div class="time-input-group">
                <label>起始时间:</label>
                <input 
                  type="datetime-local" 
                  v-model="startUtcTime" 
                  @change="onUtcTimeChange"
                  class="time-input"
                />
              </div>
              <div class="time-input-group">
                <label>结束时间:</label>
                <input 
                  type="datetime-local" 
                  v-model="endUtcTime" 
                  @change="onUtcTimeChange"
                  class="time-input"
                />
              </div>
            </div>
            <div class="time-controls">
              <button @click="applyUtcTimeFilter" :disabled="isLoading" class="apply-btn">
                {{ isLoading ? '加载中...' : '查询热力图' }}
              </button>
              <button @click="clearUtcTimeFilter" class="clear-btn">清除过滤</button>
            </div>
            <div class="preset-buttons">
              <button @click="setPresetUtcTime('today')" class="preset-btn">0912全天</button>
              <button @click="setPresetUtcTime('morning')" class="preset-btn">早高峰(7-9点)</button>
              <button @click="setPresetUtcTime('evening')" class="preset-btn">晚高峰(17-19点)</button>
              <button @click="setPresetUtcTime('last_hour')" class="preset-btn">22-23点</button>
            </div>
          </div>
          
          <!-- 时间统计面板 -->
          <div class="sidebar-panel" v-if="utcTimeStats">
            <div class="panel-title">时间统计</div>
            <div class="utc-stats">
              <div class="stat-item">
                <span>时间范围: {{ utcTimeStats.time_range }}</span>
              </div>
              <div class="stat-item">
                <span>总行程数: {{ utcTimeStats.total_trips }}</span>
              </div>
              <div class="stat-item">
                <span>车辆数: {{ utcTimeStats.unique_vehicles }}</span>
              </div>
              <div class="stat-item">
                <span>平均距离: {{ utcTimeStats.avg_distance }}km</span>
              </div>
              <div class="stat-item">
                <span>平均时长: {{ utcTimeStats.avg_duration }}分钟</span>
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
              <span>当前显示：{{ utcTimeStats ? '时间过滤数据' : '默认热力图' }}</span>
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
// 控制参数 - 调整为适合道路级别的数值
const heatmapIntensity = ref(70);
const heatmapRadius = ref(10); // 默认10，对应200米半径
const showHeatmap = ref(true);
const isLoading = ref(false);
const isTrackLoading = ref(false);

// UTC时间过滤参数
const startUtcTime = ref('');
const endUtcTime = ref('');
const utcTimeStats = ref(null);

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
      break;
    case 'timerange':
      // 可以在这里初始化时间相关的数据
      break;
    case 'trajectory':
      // 清除之前的轨迹显示
      clearVehicleTrack();
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
  
  // 自定义地图样式
  try {
    const response = await fetch('/custom_map_config.json');
    const mapStyle = await response.json();
    map.setMapStyleV2({ styleJson: mapStyle });
    console.log('自定义地图样式加载成功');
  } catch (error) {
    console.error('加载自定义地图样式失败:', error);
    dataStatus.value = '地图样式加载失败，使用默认样式';
  }
  
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
    
    // 创建热力图图层 - 调整为道路级别的精细度
    heatmapLayer = new mapvgl.HeatmapLayer({
      size: heatmapRadius.value * 20,  // 大幅减小半径倍数：从*10改为*2
      max: 200,  // 提高最大值以增强对比度
      height: 0,
      unit: 'm',
      gradient: {
        0.1: 'rgba(0, 0, 255, 0.1)',    // 低密度：淡蓝色
        0.3: 'rgba(0, 255, 255, 0.4)',  // 中低密度：青色
        0.5: 'rgba(0, 255, 0, 0.6)',    // 中密度：绿色
        0.7: 'rgba(255, 255, 0, 0.8)',  // 中高密度：黄色
        0.9: 'rgba(255, 165, 0, 0.9)',  // 高密度：橙色
        1: 'rgba(255, 0, 0, 1)'         // 最高密度：红色
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

// 更新热力图参数
const updateHeatmap = () => {
  if (!heatmapLayer) return;
  
  // 更新热力图配置 - 使用更小的半径倍数
  heatmapLayer.setOptions({
    size: heatmapRadius.value * 2,  // 从*10改为*2
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

// 加载默认热力图（基于完整轨迹数据）
const loadDefaultHeatmap = async () => {
  try {
    isLoading.value = true;
    dataStatus.value = '正在加载完整轨迹热力图数据...';
    
    // 使用新的完整轨迹数据API
    const response = await axios.get(`${API_BASE_URL}/taxi/heatmap-data-full-trajectory`, {
      params: {
        max_points: 15000,
        grid_size: 0.001,  // 1km左右的网格
        sample_rate: 0.25  // 采样25%的数据以平衡性能和完整性
      }
    });
    
    if (response.data && response.data.length > 0) {
      const processedData = response.data.map(point => ({
        lng: parseFloat(point.lng),
        lat: parseFloat(point.lat),
        count: Math.max(1, Math.min(100, point.count))
      }));
      
      realDataPoints.value = processedData;
      updateHeatmapData();
      updateStats(response.data);
      
      dataStatus.value = `完整轨迹热力图加载完成 (${processedData.length}个点)`;
      console.log(`完整轨迹热力图加载完成，共 ${processedData.length} 个数据点`);
    } else {
      dataStatus.value = '未获取到轨迹热力图数据';
    }
  } catch (error) {
    console.error('轨迹热力图数据加载失败:', error);
    dataStatus.value = `数据加载失败: ${error.message}`;
    
    // 降级到原有的快速API
    try {
      console.log('尝试降级到聚类数据API...');
      const fallbackResponse = await axios.get(`${API_BASE_URL}/taxi/heatmap-data-fast`, {
        params: { max_points: 8000 }
      });
      
      if (fallbackResponse.data && fallbackResponse.data.length > 0) {
        const processedData = fallbackResponse.data.map(point => ({
          lng: parseFloat(point.lng),
          lat: parseFloat(point.lat),
          count: Math.max(1, Math.min(100, point.count))
        }));
        
        realDataPoints.value = processedData;
        updateHeatmapData();
        updateStats(fallbackResponse.data);
        
        dataStatus.value = `热力图数据加载完成 (降级模式: ${processedData.length}个点)`;
      }
    } catch (fallbackError) {
      console.error('降级API也失败:', fallbackError);
      dataStatus.value = '所有热力图数据源都无法加载';
      
      if (error.code === 'ERR_NETWORK') {
        alert('网络连接失败，请检查后端服务是否启动在 http://localhost:8000');
      } else if (error.response) {
        alert(`服务器错误: ${error.response.status} - ${error.response.data?.detail || error.response.statusText}`);
      } else {
        alert(`请求失败: ${error.message}`);
      }
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
    
    realDataPoints.value = data.map(point => ({
      lng: parseFloat(point.lng),
      lat: parseFloat(point.lat),
      count: Math.max(1, Math.min(100, point.count))
    }));
    
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
      
      realDataPoints.value = data.map(point => ({
        lng: parseFloat(point.lng),
        lat: parseFloat(point.lat),
        count: Math.max(1, Math.min(100, point.count))
      }));
      
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
    alert('请输入车牌号和时间范围');
    return;
  }
  
  try {
    isTrackLoading.value = true;
    
    const startUtc = new Date(trackStartTime.value).toISOString().slice(0, 19).replace('T', ' ');
    const endUtc = new Date(trackEndTime.value).toISOString().slice(0, 19).replace('T', ' ');
    
    const response = await axios.get(`${API_BASE_URL}/taxi/vehicle-track?vehicle_id=${vehicleId.value}&start_utc=${startUtc}&end_utc=${endUtc}`);
    const trackData = response.data;
    
    if (trackData.length === 0) {
      alert('未找到该车辆在指定时间范围内的轨迹数据');
      return;
    }
    
    // 清除之前的轨迹
    clearVehicleTrack();
    
    // 创建轨迹点和线
    const points = [];
    trackData.forEach((point, index) => {
      const bPoint = new BMapGL.Point(point.lng, point.lat);
      points.push(bPoint);
      
      // 添加标记点
      const marker = new BMapGL.Marker(bPoint);
      const label = new BMapGL.Label(`${index + 1}`, {
        offset: new BMapGL.Size(10, -10)
      });
      marker.setLabel(label);
      map.addOverlay(marker);
      vehicleMarkers.push(marker);
    });
    
    // 创建轨迹线
    vehiclePolyline = new BMapGL.Polyline(points, {
      strokeColor: 'red',
      strokeWeight: 3,
      strokeOpacity: 0.8
    });
    map.addOverlay(vehiclePolyline);
    
    // 调整地图视野
    map.setViewport(points);
    
    // 计算轨迹统计
    let totalDistance = 0;
    for (let i = 1; i < points.length; i++) {
      totalDistance += map.getDistance(points[i-1], points[i]);
    }
    
    const startTime = new Date(trackData[0].timestamp);
    const endTime = new Date(trackData[trackData.length - 1].timestamp);
    const totalDuration = (endTime - startTime) / (1000 * 60); // 分钟
    
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
  
  await fetchHeatmapDataUtc(startUtc, endUtc);
  await fetchUtcTimeStats(startUtc, endUtc);
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
  background: #4F378A;
  color: white;
}

.sidebar-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

/* 新增：标签页导航样式 */
.nav-tabs {
  display: flex;
  flex-wrap: wrap;
  background: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
}

.nav-tab {
  flex: 1;
  min-width: 0;
  padding: 12px 8px;
  border: none;
  background: transparent;
  color: #333; /* 改为深灰色，增加对比度 */
  font-size: 13px; /* 稍微增大字体 */
  font-weight: 500; /* 增加字体粗细 */
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 3px solid transparent;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.nav-tab:hover {
  background: #e9ecef;
  color: #2c3e50; /* 悬停时使用更深的颜色 */
}

.nav-tab.active {
  background: white;
  color: #2c3e50; /* 激活状态使用深色 */
  border-bottom-color: #4F378A;
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
  color: #333;
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