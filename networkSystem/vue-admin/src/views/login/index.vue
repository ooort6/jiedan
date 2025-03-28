<template>
  <div class="login-container">
    <!-- 背景动画 -->
    <div class="login-background">
      <div class="circle-1"></div>
      <div class="circle-2"></div>
    </div>

    <div class="login-content">
      <!-- 左侧区域 -->
      <div class="login-left">
        <div class="left-content">
          <h1>Vue Admin</h1>
          <p>基于 Vue3 + TypeScript + Element Plus 的后台管理系统</p>
          <div class="feature-list">
            <div class="feature-item">
              <i class="el-icon"><Monitor /></i>
              <div class="feature-info">
                <h3>现代化的界面设计</h3>
                <p>清晰的视觉层次，舒适的界面交互</p>
              </div>
            </div>
            <div class="feature-item">
              <i class="el-icon"><Setting /></i>
              <div class="feature-info">
                <h3>丰富的功能组件</h3>
                <p>内置多种常用组件，快速搭建功能</p>
              </div>
            </div>
            <div class="feature-item">
              <i class="el-icon"><Promotion /></i>
              <div class="feature-info">
                <h3>完善的权限管理</h3>
                <p>多级权限控制，安全可靠</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧登录表单 -->
      <div class="login-right">
        <div class="login-form-container">
          <!-- Logo -->
          <div class="login-header">
            <div class="login-logo">
              <span>VA</span>
            </div>
            <h2>欢迎回来</h2>
            <p>请登录您的账号</p>
          </div>

          <!-- 登录表单 -->
          <div class="login-form">
            <form @submit.prevent="handleLogin">
              <div class="form-item">
                <label>用户名</label>
                <el-input
                  v-model="loginForm.username"
                  placeholder="请输入用户名"
                  :prefix-icon="User"
                />
              </div>

              <div class="form-item">
                <label>密码</label>
                <el-input
                  v-model="loginForm.password"
                  type="password"
                  placeholder="请输入密码"
                  :prefix-icon="Lock"
                  show-password
                />
              </div>

              <div class="form-extra">
                <el-checkbox v-model="rememberMe">记住我</el-checkbox>
                <a href="#" class="forget-link">忘记密码？</a>
              </div>

              <el-button
                type="primary"
                native-type="submit"
                :loading="loading"
                class="submit-button"
              >
                {{ loading ? "登录中..." : "登 录" }}
              </el-button>

              <div class="form-switch">
                还没有账号？
                <router-link to="/register" class="register-link"
                  >立即注册</router-link
                >
              </div>

              <div class="login-tips">
                <p>默认账号：admin</p>
                <p>默认密码：123456</p>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import {
  User,
  Lock,
  Monitor,
  Setting,
  Promotion,
} from "@element-plus/icons-vue";
import { useUserStore } from "@/stores/user";
import { ElMessage } from "element-plus";

const userStore = useUserStore();
const loading = ref(false);
const rememberMe = ref(false);

const loginForm = reactive({
  username: "",
  password: "",
});

const handleLogin = async () => {
  if (!loginForm.username || !loginForm.password) {
    ElMessage.warning("请输入用户名和密码");
    return;
  }

  loading.value = true;
  try {
    const success = await userStore.loginAction(
      loginForm.username,
      loginForm.password
    );
    if (!success) {
      ElMessage.error("登录失败，请检查用户名和密码");
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  width: 100%;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7eb 100%);
  position: relative;
  overflow: hidden;
  padding: 20px;
}

.login-background {
  position: fixed;
  inset: 0;
  z-index: 0;
}

.circle-1,
.circle-2 {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
}

.circle-1 {
  width: 600px;
  height: 600px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  top: -200px;
  right: -100px;
  animation: float 15s infinite ease-in-out;
}

.circle-2 {
  width: 450px;
  height: 450px;
  background: linear-gradient(135deg, #6b8dd6 0%, #8e37d7 100%);
  bottom: -150px;
  left: -50px;
  animation: float 20s infinite ease-in-out reverse;
}

.login-content {
  display: flex;
  width: 100%;
  max-width: 1000px;
  height: 600px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
  z-index: 1;
  overflow: hidden;
}

.login-left {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 60px;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.left-content {
  max-width: 480px;
  animation: fadeIn 0.6s ease-out;
}

.left-content h1 {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 16px;
}

.left-content > p {
  font-size: 16px;
  opacity: 0.9;
  margin-bottom: 48px;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.feature-item .el-icon {
  font-size: 24px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.feature-info h3 {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 8px;
}

.feature-info p {
  font-size: 14px;
  opacity: 0.8;
}

.login-right {
  width: 420px;
  padding: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
}

.login-form-container {
  width: 100%;
  max-width: 360px;
  animation: fadeIn 0.6s ease-out;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-logo {
  width: 64px;
  height: 64px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  font-weight: bold;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.25);
}

.login-header h2 {
  font-size: 24px;
  color: #1a1a1a;
  margin: 0 0 8px;
}

.login-header p {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.form-item {
  margin-bottom: 24px;
}

.form-item label {
  display: block;
  font-size: 14px;
  color: #333;
  margin-bottom: 8px;
}

.form-item :deep(.el-input__wrapper) {
  background-color: #fff;
  border: 1px solid #dcdfe6;
  box-shadow: none !important;
  height: 44px;
  transition: all 0.3s ease;
}

.form-item :deep(.el-input__wrapper:hover) {
  border-color: #667eea;
}

.form-item :deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1) !important;
}

.form-extra {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #667eea;
  border-color: #667eea;
}

:deep(.el-checkbox__label) {
  color: #666;
}

.forget-link {
  color: #667eea;
  font-size: 14px;
  text-decoration: none;
  transition: color 0.3s ease;
}

.forget-link:hover {
  color: #764ba2;
}

.submit-button {
  width: 100%;
  height: 44px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border: none;
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 16px;
}

.submit-button:hover {
  opacity: 0.9;
}

.form-switch {
  text-align: center;
  font-size: 14px;
  color: #666;
  margin-bottom: 16px;
}

.form-switch a {
  color: #667eea;
  text-decoration: none;
  margin-left: 4px;
  transition: color 0.3s ease;
}

.form-switch a:hover {
  color: #764ba2;
}

.login-tips {
  text-align: center;
  font-size: 13px;
  color: #999;
}

.login-tips p {
  margin: 4px 0;
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式处理 */
@media (max-width: 1024px) {
  .login-left {
    display: none;
  }

  .login-right {
    width: 100%;
    max-width: 420px;
  }
}

.register-link {
  color: #667eea;
  text-decoration: none;
  margin-left: 4px;
  transition: color 0.3s ease;
}

.register-link:hover {
  color: #764ba2;
}
</style>
