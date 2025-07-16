<template>
  <div class="map-container">
    <div id="shandong-map" class="map"></div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import 'echarts/extension/bmap/bmap'
import regionGeoJson from '@/assets/山东省.json'

let chart
let boundaryPolygons = []

const populationData = [
  { name: '济南市', value: 6949600 },
  { name: '青岛市', value: 8868500 },
  { name: '淄博市', value: 4579300 },
  { name: '枣庄市', value: 3772000 },
  { name: '东营市', value: 2072600 },
  { name: '烟台市', value: 6982900 },
  { name: '潍坊市', value: 9216100 },
  { name: '济宁市', value: 8158100 },
  { name: '泰安市', value: 5528900 },
  { name: '威海市', value: 2797500 },
  { name: '日照市', value: 2834300 },
  { name: '莱芜市', value: 1313500 },
  { name: '临沂市', value: 10124400 },
  { name: '德州市', value: 5631000 },
  { name: '聊城市', value: 5893300 },
  { name: '滨州市', value: 3788700 },
  { name: '菏泽市', value: 8338100 }
]

// color interpolation
function hexToRgb(hex) {
  const m = hex.match(/^#?([a-fA-F0-9]{6})$/)
  const i = parseInt(m[1], 16)
  return { r: (i >> 16) & 255, g: (i >> 8) & 255, b: i & 255 }
}
function rgbToHex({ r, g, b }) {
  const h = n => (n < 16 ? '0' : '') + n.toString(16)
  return `#${h(r)}${h(g)}${h(b)}`
}
function interpolateColor(c1, c2, factor) {
  const rgb1 = hexToRgb(c1), rgb2 = hexToRgb(c2)
  return rgbToHex({
    r: Math.round(rgb1.r + (rgb2.r - rgb1.r) * factor),
    g: Math.round(rgb1.g + (rgb2.g - rgb1.g) * factor),
    b: Math.round(rgb1.b + (rgb2.b - rgb1.b) * factor)
  })
}

// GCJ-02 to BD-09
function gcj02ToBd09(lon, lat) {
  const x = lon, y = lat
  const z = Math.sqrt(x * x + y * y) + 0.00002 * Math.sin(y * Math.PI)
  const theta = Math.atan2(y, x) + 0.000003 * Math.cos(x * Math.PI)
  return [z * Math.cos(theta) + 0.0065, z * Math.sin(theta) + 0.006]
}

onMounted(() => {
  const dom = document.getElementById('shandong-map')
  chart = echarts.init(dom)
  const vals = populationData.map(i => i.value)
  const minVal = Math.min(...vals), maxVal = Math.max(...vals)
  const vmColors = ['#50a3ba','#eac763','#d94e5d']
  function getColor(value) {
    const ratio = (value - minVal) / (maxVal - minVal)
    return ratio <= 0.5
      ? interpolateColor(vmColors[0], vmColors[1], ratio * 2)
      : interpolateColor(vmColors[1], vmColors[2], (ratio - 0.5) * 2)
  }
  // compute centroids for scatter
  const geoCoordMap = {}
  regionGeoJson.features.forEach(f => {
    const name = f.properties.name
    const coordsList = f.geometry.type==='Polygon'? [f.geometry.coordinates]: f.geometry.coordinates
    const ring = coordsList[0][0]
    const [sumX,sumY] = ring.reduce((a,c)=>[a[0]+c[0],a[1]+c[1]],[0,0])
    const avgX = sumX/ring.length, avgY = sumY/ring.length
    geoCoordMap[name] = gcj02ToBd09(avgX, avgY)
  })
  function convertData(data) {
    return data.map(item=>{const c=geoCoordMap[item.name];return c?{name:item.name,value:[...c,item.value]}:null}).filter(i=>i)
  }
  chart.setOption({
    bmap:{center:[117.000923,36.675807],zoom:7.5,roam:true,mapStyle:{}},
    tooltip:{trigger:'item',formatter:p=>`${p.name}: ${p.value[2]} 人`},
    visualMap:{min:minVal,max:maxVal,calculable:true,inRange:{color:vmColors},text:['高','低']},
    series:[{
      name:'人口分布',type:'scatter',coordinateSystem:'bmap',data:convertData(populationData),
      symbolSize:val=>Math.max(val[2]/(maxVal/20),20),encode:{value:2}
    }]
  })
  // @ts-ignore: access private member getBMap
  const bmap = chart.getModel().getComponent('bmap').getBMap()
  regionGeoJson.features.forEach(f=>{
    const name = f.properties.name
    const item = populationData.find(d=>d.name===name)
    const color = item?getColor(item.value):'#000'
    const polys = f.geometry.type==='Polygon'? [f.geometry.coordinates]:f.geometry.coordinates
    polys.forEach(poly=>{
      const ring = poly[0]
      const pts = ring.map(c=>{const [x,y]=c;const [lon,lat]=gcj02ToBd09(x,y);return new BMap.Point(lon,lat)})
      const ply = new BMap.Polygon(pts,{strokeWeight:2,strokeColor:color,fillColor:color,fillOpacity:0.3})
      bmap.addOverlay(ply)
      boundaryPolygons.push(ply)
    })
  })
})

onUnmounted(()=>{chart&&chart.dispose()})
</script>

<style scoped>
.map-container {
  width: 100%;
  height: 100%;
}
.map {
  width: 100%;
  height: 100%;
  border-radius: 12px;
}
</style>
