<template>
  <div class="map-container">
    <div id="jinan-map" class="map"></div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'

let map
const center = new BMapGL.Point(117.000923, 36.675807)

onMounted(() => {
  map = new BMapGL.Map('jinan-map')
  map.centerAndZoom(center, 11)
  map.enableScrollWheelZoom(true)
  map.addControl(new BMapGL.NavigationControl())
  map.addControl(new BMapGL.ScaleControl())
})

onUnmounted(() => {
  map && map.destroy()
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
