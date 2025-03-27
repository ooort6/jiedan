<template>
  <el-breadcrumb separator="/">
    <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
    <el-breadcrumb-item v-if="currentRoute.meta.title">
      {{ currentRoute.meta.title }}
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import { computed } from "vue";

const route = useRoute();
const currentRoute = computed(() => route);
</script>

<style scoped>
.el-breadcrumb {
  line-height: 60px;
  font-size: 14px;
}
</style>
