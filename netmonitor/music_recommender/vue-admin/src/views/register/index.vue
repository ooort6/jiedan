<template>
  <div class="register-container">
    <!-- 背景动画 -->
    <div class="register-background">
      <div class="circle-1"></div>
      <div class="circle-2"></div>
    </div>

    <div class="register-content">
      <!-- 左侧区域 -->
      <div class="register-left">
        <div class="left-content">
          <h1>Vue Admin</h1>
          <p>基于 Vue3 + TypeScript + Element Plus 的后台管理系统</p>
          <div class="feature-list">
            <div class="feature-item">
              <i class="el-icon"><Monitor /></i>
              <div class="feature-info">
                <h3>快速开始</h3>
                <p>简单的注册流程，立即体验系统功能</p>
              </div>
            </div>
            <div class="feature-item">
              <i class="el-icon"><Setting /></i>
              <div class="feature-info">
                <h3>安全可靠</h3>
                <p>采用先进的加密技术，保护您的账号安全</p>
              </div>
            </div>
            <div class="feature-item">
              <i class="el-icon"><Promotion /></i>
              <div class="feature-info">
                <h3>专业支持</h3>
                <p>提供全面的技术支持和帮助文档</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧注册表单 -->
      <div class="register-right">
        <div class="register-form-container">
          <!-- Logo -->
          <div class="register-header">
            <div class="register-logo">
              <span>VA</span>
            </div>
            <h2>创建账号</h2>
            <p>请填写以下信息完成注册</p>
          </div>

          <!-- 注册表单 -->
          <div class="register-form">
            <form @submit.prevent="handleRegister">
              <div class="form-item">
                <label>用户名</label>
                <el-input
                  v-model="registerForm.username"
                  placeholder="请输入用户名"
                  :prefix-icon="User"
                />
              </div>

              <div class="form-item">
                <label>邮箱</label>
                <el-input
                  v-model="registerForm.email"
                  placeholder="请输入邮箱"
                  :prefix-icon="Message"
                />
              </div>

              <div class="form-item">
                <label>密码</label>
                <el-input
                  v-model="registerForm.password"
                  type="password"
                  placeholder="请输入密码"
                  :prefix-icon="Lock"
                  show-password
                />
              </div>

              <div class="form-item">
                <label>确认密码</label>
                <el-input
                  v-model="registerForm.confirmPassword"
                  type="password"
                  placeholder="请再次输入密码"
                  :prefix-icon="Lock"
                  show-password
                />
              </div>

              <div class="form-agreement">
                <el-checkbox v-model="registerForm.agreement">
                  我已阅读并同意
                  <a href="#" class="agreement-link">服务条款</a>
                  和
                  <a href="#" class="agreement-link">隐私政策</a>
                </el-checkbox>
              </div>

              <el-button
                type="primary"
                native-type="submit"
                :loading="loading"
                :disabled="!registerForm.agreement"
                class="submit-button"
              >
                {{ loading ? "注册中..." : "注 册" }}
              </el-button>

              <div class="form-switch">
                已有账号？
                <router-link to="/login" class="login-link"
                  >立即登录</router-link
                >
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
  Message,
  Monitor,
  Setting,
  Promotion,
} from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";

const router = useRouter();
const userStore = useUserStore();
const loading = ref(false);

// 注册表单数据
const registerForm = reactive({
  username: "",
  email: "",
  password: "",
  confirmPassword: "",
  agreement: false,
});

// 注册处理
const handleRegister = async () => {
  // 表单验证
  if (!registerForm.username) {
    ElMessage.warning("请输入用户名");
    return;
  }
  if (!registerForm.email) {
    ElMessage.warning("请输入邮箱");
    return;
  }
  if (!registerForm.password) {
    ElMessage.warning("请输入密码");
    return;
  }
  if (registerForm.password !== registerForm.confirmPassword) {
    ElMessage.warning("两次输入的密码不一致");
    return;
  }
  if (!registerForm.agreement) {
    ElMessage.warning("请阅读并同意服务条款和隐私政策");
    return;
  }

  // 邮箱格式验证
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(registerForm.email)) {
    ElMessage.warning("请输入正确的邮箱格式");
    return;
  }

  loading.value = true;
  try {
    const success = await userStore.registerAction({
      username: registerForm.username,
      email: registerForm.email,
      password: registerForm.password,
    });

    if (success) {
      ElMessage.success("注册成功，请登录");
      router.push("/login");
    }
  } catch (error) {
    console.error("Registration error:", error);
    ElMessage.error("注册失败，请重试");
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.register-container {
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

.register-background {
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

.register-content {
  display: flex;
  width: 100%;
  max-width: 1000px;
  min-height: 600px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
  z-index: 1;
  overflow: hidden;
}

.register-left {
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

.register-right {
  width: 420px;
  padding: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  overflow-y: auto;
  max-height: 100%;
}

.register-form-container {
  width: 100%;
  max-width: 360px;
  padding: 20px 0;
  animation: fadeIn 0.6s ease-out;
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-logo {
  width: 64px;
  height: 64px;
  margin: 0 auto 15px;
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

.register-header h2 {
  font-size: 24px;
  color: #1a1a1a;
  margin: 0 0 8px;
}

.register-header p {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.form-item {
  margin-bottom: 20px;
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

.form-agreement {
  margin-bottom: 20px;
}

:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #667eea;
  border-color: #667eea;
}

:deep(.el-checkbox__label) {
  color: #666;
  font-size: 14px;
}

.agreement-link {
  color: #667eea;
  text-decoration: none;
  transition: color 0.3s ease;
}

.agreement-link:hover {
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

.submit-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.form-switch {
  text-align: center;
  font-size: 14px;
  color: #666;
}

.login-link {
  color: #667eea;
  text-decoration: none;
  margin-left: 4px;
  transition: color 0.3s ease;
}

.login-link:hover {
  color: #764ba2;
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
  .register-left {
    display: none;
  }

  .register-right {
    width: 100%;
    max-width: 420px;
    height: 100%;
  }

  .register-content {
    margin: 20px;
    height: auto;
  }
}
</style>
