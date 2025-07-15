<template>
  <div class="console-layout">
    <aside class="side-tabs">
      <div :class="['tab-item', activeTab === 'jinan' ? 'active' : '']" @click="activeTab = 'jinan'">济南市</div>
      <div :class="['tab-item', activeTab === 'shandong' ? 'active' : '']" @click="activeTab = 'shandong'">山东省</div>
    </aside>
    <main class="console-main">
      <div class="tab-title">
        <h2 v-if="activeTab === 'jinan'">济南市地图</h2>
        <h2 v-else>山东省地图</h2>
        <div class="tab-title-underline"></div>
      </div>
      <div class="content-wrapper">
        <transition name="fade" mode="out-in">
          <div v-if="activeTab === 'jinan'" key="jinan" class="map-container">
            <JinanMap />
          </div>
          <div v-else key="shandong" class="map-container">
            <ShandongMap />
          </div>
        </transition>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import JinanMap from './../components/JinanMap.vue'
import ShandongMap from './../components/ShandongMap.vue'

const activeTab = ref('jinan')
</script>

<style scoped>
.console-layout {
  display: flex;
  height: calc(100vh - 92px);
  min-height: 400px;
  margin-top: 0;
  margin-bottom: 20px;
}
.side-tabs {
  width: 140px;
  background: #f7f7fa;
  border-right: 2px solid #ede7f6;
  box-shadow: 2px 0 8px rgba(79, 55, 138, 0.04);
  display: flex;
  flex-direction: column;
  padding-top: 0;
  min-height: 100%;
}
.tab-item {
  padding: 16px 0;
  text-align: center;
  font-size: 16px;
  color: #666;
  cursor: pointer;
  border-left: 4px solid transparent;
  transition: background 0.2s, color 0.2s, border-color 0.2s;
  margin: 4px 0;
}
.tab-item.active {
  background: #ede7f6;
  color: #4F378A;
  border-left: 4px solid #4F378A;
  font-weight: 600;
}
.tab-item:hover {
  background: #e0e0e0;
  color: #4F378A;
}
.console-main {
  flex: 1;
  height: 100%;
  min-height: 100%;
  margin-top: 0;
  padding: 40px 56px 32px 56px;
  background: #f8f9fa;
  box-sizing: border-box;
  border-radius: 0;
  box-shadow: 0 4px 24px rgba(79, 55, 138, 0.10), 0 1.5px 6px rgba(0, 0, 0, 0.08);
  border-top: 4px solid #ede7f6;
  font-size: 18px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  overflow: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.console-main::-webkit-scrollbar {
  display: none;
}
.tab-title {
  width: 100%;
  margin-bottom: 32px;
}
.tab-title h2 {
  font-size: 1.5em;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #4F378A;
}
.tab-title-underline {
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, #4F378A 0%, #ede7f6 60%, #f8f9fa 100%);
  border-radius: 2px;
  margin-bottom: 8px;
}
.content-wrapper {
  flex: 1;
  overflow: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.map-container {
  width: 100%;
  max-width: 1200px;
  height: 600px;
  max-height: 70vh;
  min-height: 400px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(79, 55, 138, 0.06);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
