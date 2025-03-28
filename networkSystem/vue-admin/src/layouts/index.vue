<template>
  <el-container class="container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="aside">
      <div class="logo">
        <h2 v-if="!isCollapse">Vue Admin</h2>
        <h2 v-else>VA</h2>
      </div>
      <Sidebar :is-collapse="isCollapse" />
    </el-aside>

    <el-container :class="['main-container', isCollapse ? 'is-collapse' : '']">
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <el-icon class="toggle-icon" @click="toggleSidebar">
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
          <breadcrumb />
        </div>
        <div class="header-right">
          <el-dropdown trigger="click" @command="handleCommand">
            <span class="user-profile">
              <el-avatar
                :size="32"
                :src="
                  userStore.avatar ||
                  'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
                "
              />
              <span class="username">{{ userStore.nickname }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item divided command="logout"
                  >退出登录</el-dropdown-item
                >
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主要内容区域 -->
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <keep-alive>
            <component :is="Component" />
          </keep-alive>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { Fold, Expand } from "@element-plus/icons-vue";
import { useUserStore } from "@/stores/user";
import Sidebar from "./components/Sidebar.vue";
import Breadcrumb from "./components/Breadcrumb.vue";

// 侧边栏收起状态
const isCollapse = ref(false);
const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value;
};

// 用户信息
const userStore = useUserStore();
const router = useRouter();

// 下拉菜单指令处理
const handleCommand = (command: string) => {
  if (command === "logout") {
    userStore.logoutAction();
  } else if (command === "profile") {
    router.push("/profile");
  }
};

// 组件挂载后获取用户信息
onMounted(async () => {
  if (userStore.isLoggedIn && !userStore.username) {
    await userStore.getUserInfoAction();
  }
});
</script>

<style scoped>
.container {
  height: 100vh;
  width: 100vw;
  display: flex;
  overflow: hidden;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  margin: 0;
  padding: 0;
}

.aside {
  background-color: #304156;
  transition: width 0.3s;
  overflow-x: hidden;
  height: 100vh;
  flex-shrink: 0;
  z-index: 10;
}

.aside .logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  overflow: hidden;
  background-color: #2b2f3a;
}

.aside .logo h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100vh;
  transition: all 0.3s;
}

.main-container.is-collapse {
  width: calc(100vw - 64px);
}

.header {
  background-color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  height: 60px;
  padding: 0 15px;
  width: 100%;
  flex-shrink: 0;
  z-index: 9;
}

.header-left {
  display: flex;
  align-items: center;
}

.toggle-icon {
  font-size: 20px;
  cursor: pointer;
  margin-right: 15px;
  color: #5a5e66;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-profile {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin-left: 8px;
  font-size: 14px;
  color: #5a5e66;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #f0f2f5;
}
</style>
