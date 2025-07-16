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
  const center = new BMapGL.Point(119.000923, 36.275807)
  map.centerAndZoom(center, 7.5)
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
