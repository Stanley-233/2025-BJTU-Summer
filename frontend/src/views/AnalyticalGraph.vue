<template>
  <div class="analysis-container">
    <div class="header">
      <h2>数据分析图表</h2>
      <button @click="back" class="back-btn">返回</button>
    </div>

    <!-- 添加数据状态提示 -->
    <div v-if="loading" class="loading-message">加载中...</div>
    <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

    <!-- 添加数据类型选择器 -->
    <div class="data-type-selector">
      <label>数据类型: </label>
      <select v-model="selectedDataType" @change="fetchData">
        <option value="speed">速度分析</option>
        <option value="taxi-weather">出租车与天气数据关系分析</option>
      </select>
    </div>

    <!-- 添加日期选择器 -->
    <div>
      <label for="start-date">开始日期: </label>
      <input type="date" id="start-date" v-model="startDate" @change="fetchData">
      <label for="end-date">结束日期: </label>
      <input type="date" id="end-date" v-model="endDate" @change="fetchData">
    </div>

    <!-- 时间点选择器 -->
    <div v-if="selectedDataType === 'taxi-weather' && data['taxi-weather'] && data['taxi-weather'].length > 0" class="time-selector">
      <label>当前时间: </label>
      <select v-model="selectedTime" @change="updateDashboards">
        <option v-for="item in data['taxi-weather']" :key="item.hour" :value="item.hour">{{ item.hour }}</option>
      </select>
      
      <div class="play-controls">
        <button @click="togglePlay" class="play-btn">
          {{ isPlaying ? '暂停' : '播放' }}
        </button>
        <span v-if="isPlaying" class="playing-indicator">
          <i class="fa fa-circle" style="color: #4CAF50;"></i> 正在播放
        </span>
      </div>
      
      <div class="time-info">
        <input 
          type="range" 
          v-model.number="timeIndex" 
          :min="0" 
          :max="maxTimeIndex" 
          @input="updateTimeFromSlider"
          class="time-slider"
        >
        <div class="time-display">
          <span>{{ currentTimeDisplay }}</span>
          <span class="playback-speed" v-if="isPlaying">
            ({{ playbackSpeed }}秒 = 1小时)
          </span>
        </div>
      </div>
    </div>

    <!-- 添加仪表盘容器 -->
    <div v-if="selectedDataType === 'taxi-weather'" class="dashboards-container">
      <div id="dashboard-wind-speed" class="dashboard-item"></div>
      <div id="dashboard-temperature" class="dashboard-item"></div>
      <div id="dashboard-humidity" class="dashboard-item"></div>
      <div id="dashboard-taxi-count" class="dashboard-item"></div>
    </div>

    <!-- 添加图表容器 -->
    <div id="main-chart" style="width: 100%; height: 400px;"></div>
    <div id="secondary-chart" style="width: 100%; height: 400px;"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick, computed } from 'vue';
import { useRouter } from 'vue-router';
import * as echarts from 'echarts';

const router = useRouter();

// 数据状态
const selectedDataType = ref('speed');  // 默认显示速度数据
const data = ref({ speed: [], trip: [], 'taxi-weather': [] });
const startDate = ref('2013-09-12');
const endDate = ref('2013-09-18');
const loading = ref(true);
const errorMessage = ref('');

// 时间控制
const selectedTime = ref('');
const timeIndex = ref(0);
const isPlaying = ref(false);
let playInterval = null;

// 播放速度控制 (秒/小时)
const playbackSpeed = ref(2); // 默认2秒代表1小时

// 计算属性：最大时间索引
const maxTimeIndex = computed(() => {
  return data.value['taxi-weather'] ? data.value['taxi-weather'].length - 1 : 0;
});

// 当前时间显示
const currentTimeDisplay = ref('');

// 返回上一页
const back = () => {
  router.go(-1);
};

// 获取数据
const fetchData = async () => {
  loading.value = true;
  errorMessage.value = '';

  // 清除之前的图表
  const mainChartDom = document.getElementById('main-chart');
  const mainChart = echarts.getInstanceByDom(mainChartDom);
  if (mainChart) {
    mainChart.clear();
  }

  const secondaryChartDom = document.getElementById('secondary-chart');
  const secondaryChart = echarts.getInstanceByDom(secondaryChartDom);
  if (secondaryChart) {
    secondaryChart.clear();
  }

  // 清除仪表盘
  const dashboards = ['dashboard-wind-speed', 'dashboard-temperature', 'dashboard-humidity', 'dashboard-taxi-count'];
  dashboards.forEach(id => {
    const dom = document.getElementById(id);
    if (dom) {
      const chart = echarts.getInstanceByDom(dom);
      if (chart) {
        chart.clear();
      }
    }
  });

  try {
    if (selectedDataType.value === 'speed') {
      // 请求速度数据
      let speedUrl = `http://127.0.0.1:8000/speed-data`;
      if (startDate.value && endDate.value) {
        speedUrl += `?start_date=${startDate.value}&end_date=${endDate.value}`;
      }
      const speedResponse = await fetch(speedUrl);
      if (!speedResponse.ok) {
        throw new Error(`HTTP错误: ${speedResponse.status}`);
      }
      const speedData = await speedResponse.json();

      // 请求订单类型数据
      let tripUrl = `http://127.0.0.1:8000/trip-percentage-data`;
      if (startDate.value && endDate.value) {
        tripUrl += `?start_date=${startDate.value}&end_date=${endDate.value}`;
      }
      const tripResponse = await fetch(tripUrl);
      if (!tripResponse.ok) {
        throw new Error(`HTTP错误: ${tripResponse.status}`);
      }
      const tripData = await tripResponse.json();

      // 合并数据
      data.value = {
        speed: speedData,
        trip: tripData
      };
    } else {
      // 根据选择的数据类型调用不同的API
      let url = `http://127.0.0.1:8000/${selectedDataType.value}-data`;
      if (startDate.value && endDate.value) {
        url += `?start_date=${startDate.value}&end_date=${endDate.value}`;
      }

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP错误: ${response.status}`);
      }

      const result = await response.json();

      if (!Array.isArray(result) || result.length === 0) {
        throw new Error('没有可用的数据，请检查日期范围或后端数据');
      }

      data.value = {
        [selectedDataType.value]: result
      };
      
      // 初始化时间选择
      if (result.length > 0) {
        selectedTime.value = result[0].hour;
        timeIndex.value = 0;
        updateCurrentTimeDisplay();
        // 确保DOM更新后再渲染仪表盘
        nextTick(() => {
          renderDashboards();
        });
      }
    }

    renderCharts();
  } catch (error) {
    errorMessage.value = `数据加载失败: ${error.message}`;
    console.error('API请求失败:', error);
  } finally {
    loading.value = false;
  }
};

// 更新当前时间显示
const updateCurrentTimeDisplay = () => {
  if (data.value['taxi-weather'] && data.value['taxi-weather'].length > 0 && timeIndex.value < data.value['taxi-weather'].length) {
    currentTimeDisplay.value = data.value['taxi-weather'][timeIndex.value].hour;
  }
};

// 从滑块更新时间
const updateTimeFromSlider = () => {
  if (data.value['taxi-weather'] && data.value['taxi-weather'].length > 0) {
    // 限制timeIndex在有效范围内
    timeIndex.value = Math.max(0, Math.min(timeIndex.value, maxTimeIndex.value));
    
    // 获取对应时间点
    if (data.value['taxi-weather'][timeIndex.value]) {
      selectedTime.value = data.value['taxi-weather'][timeIndex.value].hour;
      // 使用nextTick确保DOM更新后再渲染仪表盘
      nextTick(() => {
        renderDashboards();
      });
    }
  }
};

// 从下拉选择更新仪表盘
const updateDashboards = () => {
  if (data.value['taxi-weather'] && data.value['taxi-weather'].length > 0) {
    const currentItem = data.value['taxi-weather'].find(item => item.hour === selectedTime.value);
    if (currentItem) {
      timeIndex.value = data.value['taxi-weather'].indexOf(currentItem);
      updateCurrentTimeDisplay();
      // 使用nextTick确保DOM更新后再渲染仪表盘
      nextTick(() => {
        renderDashboards();
      });
    }
  }
};

// 切换播放状态
const togglePlay = () => {
  if (isPlaying.value) {
    // 停止播放
    clearInterval(playInterval);
    playInterval = null;
  } else {
    // 开始播放
    // 计算时间间隔（毫秒）
    const interval = playbackSpeed.value * 1000;
    
    // 使用箭头函数确保正确的this上下文
    playInterval = setInterval(() => {
      if (timeIndex.value < maxTimeIndex.value) {
        timeIndex.value++;
        // 确保selectedTime与timeIndex同步
        if (data.value['taxi-weather'][timeIndex.value]) {
          selectedTime.value = data.value['taxi-weather'][timeIndex.value].hour;
          // 使用nextTick确保DOM更新后再渲染仪表盘
          nextTick(() => {
            renderDashboards();
          });
        }
      } else {
        // 播放到末尾，停止播放
        isPlaying.value = false;
        clearInterval(playInterval);
        playInterval = null;
      }
    }, interval);
  }
  isPlaying.value = !isPlaying.value;
};

// 组件卸载时清除定时器
onUnmounted(() => {
  if (playInterval) {
    clearInterval(playInterval);
    playInterval = null;
  }
});

// 监听时间索引变化
watch(timeIndex, () => {
  updateCurrentTimeDisplay();
});

// 监听selectedTime变化
watch(selectedTime, () => {
  updateDashboards();
});

// 渲染图表
const renderCharts = () => {
  if (Object.values(data.value).some(arr => arr.length === 0)) {
    return;
  }

  // 根据数据类型渲染不同的图表
  if (selectedDataType.value === 'speed') {
    renderSpeedCharts();
  } else if (selectedDataType.value === 'taxi-weather') {
    renderTaxiWeatherCharts();
    renderDashboards();
  }
};

// 渲染速度图表
const renderSpeedCharts = () => {
  const speedData = data.value.speed;
  const tripData = data.value.trip;

  // 主图表：速度折线图
  const mainChartDom = document.getElementById('main-chart');
  const mainChart = echarts.init(mainChartDom);
  const mainOption = {
    title: {
      text: '平均速度趋势'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: speedData.map(item => item.time_interval_start)
    },
    yAxis: {
      type: 'value',
      name: '速度 (km/h)'
    },
    series: [{
      name: '平均速度',
      data: speedData.map(item => item.average_speed),
      type: 'line',
      smooth: true
    }],
    dataZoom: [
      {
        type: 'slider',
        xAxisIndex: 0,
        start: 0,
        end: 30
      }
    ]
  };
  mainChart.setOption(mainOption);

  // 次要图表：订单类型百分比饼图
  const secondaryChartDom = document.getElementById('secondary-chart');
  const secondaryChart = echarts.init(secondaryChartDom);

  const pieData = [
    { name: '中程订单', value: tripData.reduce((sum, item) => sum + item.medium_trip, 0) },
    { name: '短程订单', value: tripData.reduce((sum, item) => sum + item.short_trip, 0) },
    { name: '长途订单', value: tripData.reduce((sum, item) => sum + item.long_trip, 0) }
  ];

  const secondaryOption = {
    title: {
      text: '订单类型百分比分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}% ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [{
      type: 'pie',
      radius: '50%',
      data: pieData,
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      },
      label: {
        formatter: '{b}: {d}%'
      }
    }]
  };
  secondaryChart.setOption(secondaryOption);
};

// 渲染出租车与天气数据关系图表
const renderTaxiWeatherCharts = () => {
  const taxiWeatherData = data.value['taxi-weather'];

  const mainChartDom = document.getElementById('main-chart');
  const mainChart = echarts.init(mainChartDom);
  const mainOption = {
    title: {
      text: '出租车与天气数据关系'
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        let result = params[0].name + '<br/>';
        params.forEach(item => {
          result += `<span style="display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:${item.color}"></span>`;
          result += `${item.seriesName}: ${item.value}${item.seriesName === '温度' ? '°C' : item.seriesName === '湿度' ? '%' : item.seriesName === '风速' ? ' m/s' : ' 辆'}<br/>`;
        });
        return result;
      }
    },
    xAxis: {
      type: 'category',
      data: taxiWeatherData.map(item => item.hour)
    },
    yAxis: [
      {
        type: 'value',
        name: '载客出租车数量',
        min: 0
      },
      {
        type: 'value',
        name: '天气数据',
        splitLine: {
          show: false
        }
      }
    ],
    series: [
      {
        name: '载客出租车数量',
        data: taxiWeatherData.map(item => item.active_taxis),
        type: 'line',
        smooth: true,
        yAxisIndex: 0,
        emphasis: {
          focus: 'series'
        }
      },
      {
        name: '温度',
        data: taxiWeatherData.map(item => item.temperature),
        type: 'line',
        smooth: true,
        yAxisIndex: 1,
        emphasis: {
          focus: 'series'
        }
      },
      {
        name: '湿度',
        data: taxiWeatherData.map(item => item.humidity),
        type: 'line',
        smooth: true,
        yAxisIndex: 1,
        emphasis: {
          focus: 'series'
        }
      },
      {
        name: '风速',
        data: taxiWeatherData.map(item => item.wind_speed),
        type: 'line',
        smooth: true,
        yAxisIndex: 1,
        emphasis: {
          focus: 'series'
        }
      }
    ],
    dataZoom: [
      {
        type: 'slider',
        xAxisIndex: 0,
        start: 0,
        end: 100
      }
    ]
  };
  mainChart.setOption(mainOption);
};

// 渲染仪表盘
const renderDashboards = () => {
  const taxiWeatherData = data.value['taxi-weather'];
  if (!taxiWeatherData || taxiWeatherData.length === 0) {
    return;
  }
  
  const currentItem = taxiWeatherData.find(item => item.hour === selectedTime.value);
  if (!currentItem) {
    return;
  }

  // 风速仪表盘
  const windSpeedDashboardDom = document.getElementById('dashboard-wind-speed');
  if (windSpeedDashboardDom) {
    const windSpeedDashboard = echarts.getInstanceByDom(windSpeedDashboardDom) || echarts.init(windSpeedDashboardDom);
    const windSpeedDashboardOption = {
      title: {
        text: '风速',
        left: 'center'
      },
      tooltip: {
        formatter: '{a} <br/>{b} : {c} m/s'
      },
      series: [
        {
          name: '风速',
          type: 'gauge',
          min: 0,
          max: 10,
          detail: { formatter: '{value} m/s' },
          data: [
            {
              value: currentItem.wind_speed.toFixed(1),
              name: '风速'
            }
          ]
        }
      ]
    };
    windSpeedDashboard.setOption(windSpeedDashboardOption);
  }

  // 温度仪表盘
  const temperatureDashboardDom = document.getElementById('dashboard-temperature');
  if (temperatureDashboardDom) {
    const temperatureDashboard = echarts.getInstanceByDom(temperatureDashboardDom) || echarts.init(temperatureDashboardDom);
    const temperatureDashboardOption = {
      title: {
        text: '温度',
        left: 'center'
      },
      tooltip: {
        formatter: '{a} <br/>{b} : {c} °C'
      },
      series: [
        {
          name: '温度',
          type: 'gauge',
          min: 0,
          max: 40,
          detail: { formatter: '{value} °C' },
          data: [
            {
              value: currentItem.temperature.toFixed(1),
              name: '温度'
            }
          ]
        }
      ]
    };
    temperatureDashboard.setOption(temperatureDashboardOption);
  }

  // 湿度仪表盘
  const humidityDashboardDom = document.getElementById('dashboard-humidity');
  if (humidityDashboardDom) {
    const humidityDashboard = echarts.getInstanceByDom(humidityDashboardDom) || echarts.init(humidityDashboardDom);
    const humidityDashboardOption = {
      title: {
        text: '湿度',
        left: 'center'
      },
      tooltip: {
        formatter: '{a} <br/>{b} : {c} %'
      },
      series: [
        {
          name: '湿度',
          type: 'gauge',
          min: 0,
          max: 100,
          detail: { formatter: '{value} %' },
          data: [
            {
              value: currentItem.humidity.toFixed(1),
              name: '湿度'
            }
          ]
        }
      ]
    };
    humidityDashboard.setOption(humidityDashboardOption);
  }

  // 车辆数量仪表盘
  const taxiCountDashboardDom = document.getElementById('dashboard-taxi-count');
  if (taxiCountDashboardDom) {
    const taxiCountDashboard = echarts.getInstanceByDom(taxiCountDashboardDom) || echarts.init(taxiCountDashboardDom);
    const taxiCountDashboardOption = {
      title: {
        text: '车辆数量',
        left: 'center'
      },
      tooltip: {
        formatter: '{a} <br/>{b} : {c} 辆'
      },
      series: [
        {
          name: '车辆数量',
          type: 'gauge',
          min: 0,
          max: 6000,
          detail: { formatter: '{value} 辆' },
          data: [
            {
              value: currentItem.active_taxis,
              name: '车辆数量'
            }
          ]
        }
      ]
    };
    taxiCountDashboard.setOption(taxiCountDashboardOption);
  }
};

// 组件挂载时自动获取数据并渲染图表
onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.analysis-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.back-btn {
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: #e5e5e5;
}

.loading-message {
  color: #333;
  margin: 10px 0;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
  text-align: center;
}

.error-message {
  color: red;
  margin: 10px 0;
  padding: 10px;
  background-color: #ffebee;
  border-radius: 4px;
}

/* 数据类型选择器样式 */
.data-type-selector {
  margin: 15px 0;
  display: flex;
  align-items: center;
}

.data-type-selector label {
  margin-right: 10px;
  font-weight: bold;
}

.data-type-selector select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

/* 日期选择器样式 */
input[type="date"] {
  padding: 8px;
  margin: 0 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

/* 时间选择器样式 */
.time-selector {
  margin: 15px 0;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.time-selector > div {
  display: flex;
  align-items: center;
  width: 100%;
  margin-bottom: 10px;
}

.play-controls {
  display: flex;
  align-items: center;
}

.playing-indicator {
  margin-left: 10px;
  color: #4CAF50;
  font-size: 14px;
}

.time-info {
  width: 100%;
}

.time-slider {
  flex-grow: 1;
  margin: 0 10px;
}

.time-display {
  display: flex;
  justify-content: space-between;
  margin-top: 5px;
  font-size: 14px;
}

.playback-speed {
  color: #666;
}

.play-btn {
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
  margin-right: 10px;
}

.play-btn:hover {
  background: #45a049;
}

/* 仪表盘容器样式 */
.dashboards-container {
  display: flex;
  flex-wrap: wrap;
  margin: 20px 0;
}

.dashboard-item {
  width: 25%;
  height: 300px;
  box-sizing: border-box;
  padding: 10px;
}
</style>