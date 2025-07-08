<template>
  <div class="app-bg">
    <StartPage />
  </div>
</template>

<script setup>
import StartPage from './components/StartPage.vue'
</script>

<style scoped>
.app-bg {
  min-height: 100vh;
  width: 100vw;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
