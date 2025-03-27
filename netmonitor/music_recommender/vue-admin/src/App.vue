<script setup lang="ts">
// 不需要导入 HelloWorld 组件
</script>

<template>
  <router-view />
</template>

<style>
html,
body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow: hidden;
}

#app {
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 0;
  display: flex;
}

.el-menu {
  border-right: none !important;
}

.el-container {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
}

.el-row {
  width: 100%;
  margin-left: 0 !important;
  margin-right: 0 !important;
}

.el-col {
  padding-left: 10px !important;
  padding-right: 10px !important;
}

.el-card {
  width: 100%;
}

/* 修复控制台Dashboard内容 */
.dashboard-container {
  width: 100%;
  max-width: 100%;
  padding: 0;
  margin: 0;
}
</style>
