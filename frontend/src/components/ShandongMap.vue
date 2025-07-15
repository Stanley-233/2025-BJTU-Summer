<template>
  <div class="map-container">
    <div id="shandong-map" class="map"></div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'

let map

onMounted(() => {
  map = new BMapGL.Map('shandong-map')
  // 山东省中心坐标，大约117.0009E, 36.6758N，缩放级别设为7
  const center = new BMapGL.Point(117.000923, 36.675807)
  map.centerAndZoom(center, 7)
  map.enableScrollWheelZoom(true)
  map.addControl(new BMapGL.NavigationControl())
  map.addControl(new BMapGL.ScaleControl())
})

onUnmounted(() => {
  if (map) {
    map.destroy()
    map = null
  }
})
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
