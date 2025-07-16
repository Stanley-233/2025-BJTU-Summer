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
        <option value="density">密度分布</option>
        <option value="flow">流量趋势</option>
      </select>
    </div>

    <!-- 添加日期选择器 -->
    <div>
      <label for="start-date">开始日期: </label>
      <input type="date" id="start-date" v-model="startDate" @change="fetchData">
      <label for="end-date">结束日期: </label>
      <input type="date" id="end-date" v-model="endDate" @change="fetchData">
    </div>

    <!-- 添加图表容器 -->
    <div id="main-chart" style="width: 100%; height: 400px;"></div>
    <div id="secondary-chart" style="width: 100%; height: 400px;"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import * as echarts from 'echarts';

const router = useRouter();

// 数据状态
const selectedDataType = ref('speed');  // 默认显示速度数据
const data = ref([]);
const startDate = ref('2013-09-12');
const endDate = ref('2013-09-18');
const loading = ref(true);
const errorMessage = ref('');

// 返回上一页
const back = () => {
  router.go(-1);
};

// 获取数据
const fetchData = async () => {
  loading.value = true;
  errorMessage.value = '';
  
  try {
    // 根据选择的数据类型调用不同的API
    let url = `http://localhost:8000/${selectedDataType.value}-data`;
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
    
    data.value = result;
    renderCharts();
  } catch (error) {
    errorMessage.value = `数据加载失败: ${error.message}`;
    console.error('API请求失败:', error);
  } finally {
    loading.value = false;
  }
};

// 渲染图表
const renderCharts = () => {
  if (data.value.length === 0) {
    return;
  }

  // 根据数据类型渲染不同的图表
  if (selectedDataType.value === 'speed') {
    renderSpeedCharts();
  } else if (selectedDataType.value === 'density') {
    renderDensityCharts();
  } else if (selectedDataType.value === 'flow') {
    renderFlowCharts();
  }
};

// 渲染速度图表
const renderSpeedCharts = () => {
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
      data: data.value.map(item => item.timestamp)
    },
    yAxis: {
      type: 'value',
      name: '速度 (km/h)'
    },
    series: [{
      name: '平均速度',
      data: data.value.map(item => item.average_speed),
      type: 'line',
      smooth: true
    }],
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

  // 次要图表：速度区间分布饼图
  const secondaryChartDom = document.getElementById('secondary-chart');
  const secondaryChart = echarts.init(secondaryChartDom);
  
  const speedRanges = [
    { name: '低速 (<10km/h)', min: 0, max: 10 },
    { name: '中低速 (10-30km/h)', min: 10, max: 30 },
    { name: '中速 (30-60km/h)', min: 30, max: 60 },
    { name: '高速 (60-90km/h)', min: 60, max: 90 },
    { name: '超高速 (≥90km/h)', min: 90, max: Infinity }
  ];
  
  const rangeCounts = speedRanges.map(range => ({
    name: range.name,
    value: 0
  }));
  
  data.value.forEach(item => {
    const speed = item.average_speed;
    for (let i = 0; i < speedRanges.length; i++) {
      const range = speedRanges[i];
      if (speed >= range.min && speed < range.max) {
        rangeCounts[i].value++;
        break;
      }
    }
  });
  
  const total = rangeCounts.reduce((sum, item) => sum + item.value, 0);
  const pieData = rangeCounts.map(item => ({
    name: item.name,
    value: item.value,
    percent: ((item.value / total) * 100).toFixed(1) + '%'
  }));
  
  const secondaryOption = {
    title: {
      text: '速度区间分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 次 ({d}%)'
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

// 渲染密度图表（示例）
const renderDensityCharts = () => {
  // 主图表：密度热力图
  const mainChartDom = document.getElementById('main-chart');
  const mainChart = echarts.init(mainChartDom);
  const mainOption = {
    title: {
      text: '区域密度分布'
    },
    tooltip: {
      trigger: 'item'
    },
    xAxis: {
      type: 'category',
      data: ['区域A', '区域B', '区域C', '区域D', '区域E']
    },
    yAxis: {
      type: 'value',
      name: '车辆密度 (辆/平方公里)'
    },
    series: [{
      name: '密度',
      data: data.value.map(item => item.density),
      type: 'bar'
    }]
  };
  mainChart.setOption(mainOption);

  // 次要图表：密度趋势图
  const secondaryChartDom = document.getElementById('secondary-chart');
  const secondaryChart = echarts.init(secondaryChartDom);
  const secondaryOption = {
    title: {
      text: '密度随时间变化'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: data.value.map(item => item.timestamp)
    },
    yAxis: {
      type: 'value',
      name: '平均密度 (辆/平方公里)'
    },
    series: [{
      name: '密度',
      data: data.value.map(item => item.avg_density),
      type: 'line',
      smooth: true
    }]
  };
  secondaryChart.setOption(secondaryOption);
};

// 渲染流量图表（示例）
const renderFlowCharts = () => {
  // 主图表：流量趋势图
  const mainChartDom = document.getElementById('main-chart');
  const mainChart = echarts.init(mainChartDom);
  const mainOption = {
    title: {
      text: '交通流量趋势'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: data.value.map(item => item.timestamp)
    },
    yAxis: {
      type: 'value',
      name: '流量 (辆/小时)'
    },
    series: [{
      name: '流量',
      data: data.value.map(item => item.flow),
      type: 'line',
      smooth: true
    }]
  };
  mainChart.setOption(mainOption);

  // 次要图表：流量分布饼图
  const secondaryChartDom = document.getElementById('secondary-chart');
  const secondaryChart = echarts.init(secondaryChartDom);
  const secondaryOption = {
    title: {
      text: '时段流量分布'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 辆 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [{
      type: 'pie',
      radius: '50%',
      data: [
        { name: '早高峰 (7-9点)', value: data.value[0].morning_peak },
        { name: '平峰期 (9-17点)', value: data.value[0].off_peak },
        { name: '晚高峰 (17-19点)', value: data.value[0].evening_peak },
        { name: '夜间 (19-7点)', value: data.value[0].night }
      ]
    }]
  };
  secondaryChart.setOption(secondaryOption);
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
</style>