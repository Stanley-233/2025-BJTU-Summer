<template>
  <div class="page-container">
    <h2>城市时空可视化</h2>
    <div class="intro-section">
      <p class="intro-text">欢迎使用济南市出租车时空可视化系统</p>
      <p class="intro-desc">本系统提供济南市出租车运行数据的可视化分析，包括热力图展示和车辆轨迹追踪功能。</p>
    </div>
    
    <div class="map-container">
      <div id="main-map-container" class="map"></div>
    </div>
    
    <div class="action-panel">
      <div class="panel-title">功能入口</div>
      <div class="action-buttons">
        <button @click="openDataAnalysis" class="analysis-btn">
          <span class="btn-icon">📊</span>
          <span class="btn-text">进入数据分析</span>
          <span class="btn-desc">查看热力图和车辆轨迹</span>
        </button>
        <button @click="showMapInfo" class="info-btn">
          <span class="btn-icon">ℹ️</span>
          <span class="btn-text">地图信息</span>
          <span class="btn-desc">查看地图基本信息</span>
        </button>
        <button @click="openPopulation" class="population-btn">
          <span class="btn-icon">👥</span>
          <span class="btn-text">人口可视化</span>
          <span class="btn-desc">查看人口分布</span>
        </button>
      </div>
    </div>
    
    <div class="info-panel" v-if="showInfo">
      <div class="panel-title">济南市基本信息</div>
      <div class="info-content">
        <div class="info-item">
          <span class="info-label">城市：</span>
          <span class="info-value">济南市</span>
        </div>
        <div class="info-item">
          <span class="info-label">坐标中心：</span>
          <span class="info-value">117.000923°E, 36.675807°N</span>
        </div>
        <div class="info-item">
          <span class="info-label">数据日期：</span>
          <span class="info-value">2023年9月12日</span>
        </div>
        <div class="info-item">
          <span class="info-label">数据类型：</span>
          <span class="info-value">出租车GPS轨迹数据</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import router from "@/router/index.js";

// 地图实例
let map = null;

// 控制状态
const showInfo = ref(false);

// 初始化地图
const initMap = () => {
  // 创建地图实例
  map = new BMapGL.Map('main-map-container');
  
  // 设置济南市中心坐标
  const jinanCenter = new BMapGL.Point(117.000923, 36.675807);
  map.centerAndZoom(jinanCenter, 11);
  
  // 启用滚轮缩放
  map.enableScrollWheelZoom(true);
  
  // 添加控件
  map.addControl(new BMapGL.NavigationControl());
  map.addControl(new BMapGL.ScaleControl());
  
  // 添加济南市标记
  const marker = new BMapGL.Marker(jinanCenter);
  map.addOverlay(marker);
  
  // 添加信息窗口
  const infoWindow = new BMapGL.InfoWindow('济南市 - 出租车数据可视化中心', {
    width: 200,
    height: 50
  });
  
  marker.addEventListener('click', () => {
    map.openInfoWindow(infoWindow, jinanCenter);
  });
};

// 打开数据分析页面
const openDataAnalysis = () => {
  // 在新标签页中打开数据分析页面
  router.push('/data-analysis');
};

const openPopulation = () => {
  // 在新标签页中打开人口可视化页面
  router.push('/population-visualize');
};

// 显示地图信息
const showMapInfo = () => {
  showInfo.value = !showInfo.value;
};

// 组件挂载
onMounted(() => {
  // 确保百度地图API已加载
  if (typeof BMapGL !== 'undefined') {
    initMap();
  } else {
    console.error('百度地图API未加载');
  }
});

// 组件卸载
onUnmounted(() => {
  if (map) {
    map.destroy();
    map = null;
  }
});
</script>

<style scoped>
.page-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.intro-section {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
}

.intro-text {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 10px;
}

.intro-desc {
  font-size: 16px;
  opacity: 0.9;
}

.map-container {
  margin-bottom: 30px;
}

.map {
  width: 100%;
  height: 500px;
  border: 1px solid #ddd;
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.action-panel, .info-panel {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin: 20px 0;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.panel-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #333;
}

.action-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
}

.analysis-btn, .info-btn, .population-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 200px;
}

.analysis-btn {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.info-btn {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.population-btn {
  background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
  color: white;
}

.analysis-btn:hover, .info-btn:hover, .population-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.2);
}

.btn-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.btn-text {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 4px;
}

.btn-desc {
  font-size: 12px;
  opacity: 0.9;
}

.info-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.info-item {
  display: flex;
  align-items: center;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 8px;
}

.info-label {
  font-weight: bold;
  color: #666;
  margin-right: 10px;
}

.info-value {
  color: #333;
}
</style>
