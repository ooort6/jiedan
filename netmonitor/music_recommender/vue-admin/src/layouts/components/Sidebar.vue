<template>
  <div class="sidebar">
    <el-menu
      :default-active="activeMenu"
      :collapse="isCollapse"
      class="sidebar-menu"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409EFF"
      router
    >
      <template v-for="route in menuRoutes" :key="route.path">
        <el-menu-item :index="'/' + route.path">
          <el-icon><component :is="route.meta.icon" /></el-icon>
          <span>{{ route.meta.title }}</span>
        </el-menu-item>
      </template>
    </el-menu>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import * as ElementPlusIconsVue from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();
const activeMenu = computed(() => route.path);

// 从父组件接收折叠状态
const props = defineProps<{
  isCollapse: boolean;
}>();

// 获取菜单路由
const menuRoutes = computed(() => {
  const mainRoute = router.options.routes.find((route) => route.path === "/");
  return mainRoute?.children?.filter((route) => route.meta?.requiresAuth) || [];
});
</script>

<style scoped>
.sidebar {
  height: 100%;
  background-color: #304156;
}

.sidebar-menu {
  height: 100%;
  border-right: none;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 200px;
}

:deep(.el-menu-item) {
  &:hover {
    background-color: #263445 !important;
  }

  &.is-active {
    background-color: #263445 !important;
  }
}
</style>
