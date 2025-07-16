<template>
  <div class="map-container">
    <div id="jinan-map" class="map"></div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import 'echarts/extension/bmap/bmap'
import regionGeoJson from '@/assets/济南市.json'

let chart
// track drawn boundary polygons
let boundaryPolygons = []
const center = new BMap.Point(117.000923, 36.675807)

const populationData = [
  { name: '历下区', value: 754136 },
  { name: '市中区', value: 713581 },
  { name: '槐荫区', value: 476811 },
  { name: '天桥区', value: 688415 },
  { name: '历城区', value: 1124306 },
  { name: '长清区', value: 578740 },
  { name: '章丘区', value: 1064210 },
  { name: '济阳区', value: 517948 },
  { name: '莱芜区', value: 989535 },
  { name: '钢城区', value: 308994 },
  { name: '平阴县', value: 331712 },
  { name: '商河县', value: 564125 }
]
const geoCoordMap = {
  '历下区': [117.0970, 36.6697],
  '市中区': [117.0080, 36.6512],
  '槐荫区': [116.9882, 36.6547],
  '天桥区': [116.9982, 36.7102],
  '历城区': [117.1366, 36.7032],
  '长清区': [116.7456, 36.5298],
  '章丘区': [117.5380, 36.7186],
  '济阳区': [116.9644, 36.9846],
  '莱芜区': [117.6755, 36.2162],
  '钢城区': [117.8184, 36.0745],
  '平阴县': [116.4450, 36.2591],
  '商河县': [117.1599, 37.3142]
}
function convertData(data) {
  return data.map(item => {
    const coord = geoCoordMap[item.name]
    if (coord) {
      return { name: item.name, value: [...coord, item.value] }
    }
    return null
  }).filter(item => item !== null)
}

// Add helper functions for color interpolation
function hexToRgb(hex) {
  const m = hex.match(/^#?([a-fA-F0-9]{6})$/);
  const i = parseInt(m[1], 16);
  return { r: (i >> 16) & 255, g: (i >> 8) & 255, b: i & 255 };
}
function rgbToHex({ r, g, b }) {
  const h = (n) => (n < 16 ? '0' : '') + n.toString(16);
  return `#${h(r)}${h(g)}${h(b)}`;
}
function interpolateColor(c1, c2, factor) {
  const rgb1 = hexToRgb(c1), rgb2 = hexToRgb(c2);
  return rgbToHex({ r: Math.round(rgb1.r + (rgb2.r - rgb1.r) * factor), g: Math.round(rgb1.g + (rgb2.g - rgb1.g) * factor), b: Math.round(rgb1.b + (rgb2.b - rgb1.b) * factor) });
}

// Add helper to convert GCJ-02 to BD-09
function gcj02ToBd09(lon, lat) {
  const x = lon, y = lat;
  const z = Math.sqrt(x * x + y * y) + 0.00002 * Math.sin(y * Math.PI);
  const theta = Math.atan2(y, x) + 0.000003 * Math.cos(x * Math.PI);
  return [z * Math.cos(theta) + 0.0065, z * Math.sin(theta) + 0.006];
}

onMounted(() => {
  const dom = document.getElementById('jinan-map')
  chart = echarts.init(dom)
  const vals = populationData.map(i => i.value);
  const minVal = Math.min(...vals), maxVal = Math.max(...vals);
  const vmColors = ['#50a3ba', '#eac763', '#d94e5d'];
  // compute color for a given value
  function getColor(value) {
    const ratio = (value - minVal) / (maxVal - minVal);
    if (ratio <= 0.5) {
      return interpolateColor(vmColors[0], vmColors[1], ratio * 2);
    }
    return interpolateColor(vmColors[1], vmColors[2], (ratio - 0.5) * 2);
  }
  chart.setOption({
    bmap: { center: [117.000923,36.675807], zoom:11, roam:true, mapStyle:{} },
    tooltip:{
      trigger: 'item',
      formatter: p => `${p.name}: ${p.value[2]} 人`,
      textStyle: { fontSize: 16 },
      padding: [12, 18]
    },
    visualMap:{ min:minVal,max:maxVal,calculable:true,inRange:{color:['#50a3ba','#eac763','#d94e5d']},text:['高','低'] },
    series:[{
      name:'人口分布',
      type:'scatter',
      coordinateSystem:'bmap',
      data:convertData(populationData),
      // @ts-ignore: symbolSize is a valid series property
      symbolSize: val => Math.max(val[2] / 80000, 20),
      encode:{ value:2 },
      // remove fixed color to allow visualMap coloring
    }]
  });
  // draw initial boundaries matching population data colors using GeoJSON
  const bmap = chart.getModel().getComponent('bmap').getBMap();
  regionGeoJson.features.forEach(feature => {
    const name = feature.properties.name;
    const item = populationData.find(d => d.name === name);
    const color = item ? getColor(item.value) : '#000';
    const polys = feature.geometry.type === 'Polygon' ? [feature.geometry.coordinates] : feature.geometry.coordinates;
    polys.forEach(polygon => {
      const ring = polygon[0];
      const points = ring.map(coord => {
        const [lon, lat] = coord;
        const [bdLon, bdLat] = gcj02ToBd09(lon, lat);
        return new BMap.Point(bdLon, bdLat);
      });
      const ply = new BMap.Polygon(points, { strokeWeight: 2, strokeColor: color, fillColor: color, fillOpacity: 0.3 });
      bmap.addOverlay(ply);
      boundaryPolygons.push(ply);
    });
  });
  // 点击散点事件已移除
})

onUnmounted(() => { chart && chart.dispose() })
</script>

<style scoped>
.map-container {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
}
.map {
  width: 100%;
  height: 100%;
  border-radius: 12px;
}
</style>
