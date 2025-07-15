<template>
  <div class="map-container">
    <div id="jinan-map" class="map"></div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import 'echarts/extension/bmap/bmap'

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

onMounted(() => {
  const dom = document.getElementById('jinan-map')
  chart = echarts.init(dom)
  const vals = populationData.map(i => i.value)
  const minVal = Math.min(...vals), maxVal = Math.max(...vals)
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
      symbolSize: val => Math.max(val[2] / 80000, 20),
      encode:{ value:2 },
      itemStyle:{ color:'purple' }
    }]
  })
  // 点击散点显示行政区边界
  chart.on('click', function(params) {
    if (params.componentType === 'series' && params.seriesType === 'scatter') {
      const name = params.name;
      const bmapComp = chart.getModel().getComponent('bmap');
      const bmap = bmapComp.getBMap();
      // 移除之前绘制的行政区边界
      boundaryPolygons.forEach(poly => bmap.removeOverlay(poly));
      boundaryPolygons = [];
      // 移除之前绘制的行政区边界
      boundaryPolygons.forEach(poly => bmap.removeOverlay(poly));
      boundaryPolygons = [];
      const bdary = new BMap.Boundary();
      // 指定济南市行政区，避免同名歧义
          // 构建多边形覆盖物
      const regionName = `济南市${name}`;
      bdary.get(regionName, function(rs) {
        for (let i = 0; i < rs.boundaries.length; i++) {
          // 构建多边形覆盖物
          const ply = new BMap.Polygon(rs.boundaries[i], {
             strokeWeight: 2,
             strokeColor: '#ff0000',
             fillColor: 'rgba(255,0,0,0.3)'
           });
          bmap.addOverlay(ply);
          boundaryPolygons.push(ply);
         }
        // 不调整视野，保持点击前的中心和缩放级别
       });
     }
   });
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
