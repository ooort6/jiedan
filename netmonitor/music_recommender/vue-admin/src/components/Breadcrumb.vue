<template>
  <el-breadcrumb separator="/">
    <el-breadcrumb-item
      v-for="(item, index) in breadcrumbs"
      :key="index"
      :to="item.path"
    >
      {{ item.title }}
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { useRoute, RouteRecordNormalized } from "vue-router";

interface BreadcrumbItem {
  path: string;
  title: string;
}

const route = useRoute();
const breadcrumbs = ref<BreadcrumbItem[]>([]);

// 根据当前路由生成面包屑导航
const getBreadcrumbs = () => {
  const matched = route.matched.filter((item) => item.meta && item.meta.title);

  const result: BreadcrumbItem[] = [
    {
      path: "/dashboard",
      title: "首页",
    },
  ];

  matched.forEach((item) => {
    if (item.path !== "/dashboard") {
      result.push({
        path: item.path,
        title: item.meta.title as string,
      });
    }
  });

  breadcrumbs.value = result;
};

// 监听路由变化
watch(
  () => route.path,
  () => {
    getBreadcrumbs();
  },
  { immediate: true }
);
</script>

<style scoped>
.el-breadcrumb {
  line-height: 60px;
}
</style>
