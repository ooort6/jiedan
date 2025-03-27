<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>个人信息</span>
          <el-button type="primary" @click="handleSave">保存修改</el-button>
        </div>
      </template>

      <el-form
        :model="userForm"
        label-width="100px"
        ref="formRef"
        :rules="rules"
      >
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12">
            <!-- 头像上传 -->
            <div class="avatar-container">
              <el-avatar :size="100" :src="userForm.avatar || defaultAvatar" />
              <el-upload
                class="avatar-uploader"
                action="#"
                :auto-upload="false"
                :show-file-list="false"
                :on-change="handleAvatarChange"
              >
                <el-button type="primary" class="upload-btn"
                  >更换头像</el-button
                >
              </el-upload>
            </div>

            <!-- 用户基础信息 -->
            <el-form-item label="用户名" prop="username">
              <el-input v-model="userForm.username" disabled />
            </el-form-item>

            <el-form-item label="昵称" prop="nickname">
              <el-input v-model="userForm.nickname" placeholder="请输入昵称" />
            </el-form-item>

            <el-form-item label="邮箱" prop="email">
              <el-input v-model="userForm.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="12">
            <!-- 修改密码 -->
            <div class="password-section">
              <h3>修改密码</h3>

              <el-form-item label="原密码" prop="oldPassword">
                <el-input
                  v-model="userForm.oldPassword"
                  type="password"
                  placeholder="请输入原密码"
                  show-password
                />
              </el-form-item>

              <el-form-item label="新密码" prop="newPassword">
                <el-input
                  v-model="userForm.newPassword"
                  type="password"
                  placeholder="请输入新密码"
                  show-password
                />
              </el-form-item>

              <el-form-item label="确认密码" prop="confirmPassword">
                <el-input
                  v-model="userForm.confirmPassword"
                  type="password"
                  placeholder="请再次输入新密码"
                  show-password
                />
              </el-form-item>
            </div>
          </el-col>
        </el-row>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import type { FormInstance, FormRules } from "element-plus";
import { ElMessage } from "element-plus";
import { useUserStore } from "@/stores/user";
import { changePassword } from "@/api/auth";
import { useRouter } from "vue-router";

const userStore = useUserStore();
const formRef = ref<FormInstance>();
const defaultAvatar =
  "https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png";
const router = useRouter();

// 表单数据
const userForm = reactive({
  username: "",
  nickname: "",
  email: "",
  avatar: "",
  oldPassword: "",
  newPassword: "",
  confirmPassword: "",
});

// 表单验证规则
const rules = reactive<FormRules>({
  nickname: [{ max: 50, message: "昵称长度不能超过50个字符", trigger: "blur" }],
  email: [{ type: "email", message: "请输入正确的邮箱地址", trigger: "blur" }],
  oldPassword: [{ required: true, message: "请输入原密码", trigger: "blur" }],
  newPassword: [
    { required: true, message: "请输入新密码", trigger: "blur" },
    { min: 6, message: "密码长度不能少于6个字符", trigger: "blur" },
  ],
  confirmPassword: [
    { required: true, message: "请确认新密码", trigger: "blur" },
    {
      validator: (rule, value, callback) => {
        if (value !== userForm.newPassword) {
          callback(new Error("两次输入的密码不一致"));
        } else {
          callback();
        }
      },
      trigger: "blur",
    },
  ],
});

// 头像更改
const handleAvatarChange = (file: any) => {
  // 在实际应用中，这里应该上传文件到服务器
  // 并在成功响应后更新用户的头像URL
  const reader = new FileReader();
  reader.readAsDataURL(file.raw);
  reader.onload = () => {
    userForm.avatar = reader.result as string;
  };
};

// 保存用户信息
const handleSave = async () => {
  if (!formRef.value) return;

  try {
    await formRef.value.validate();

    // 如果有修改密码，先处理密码修改
    if (userForm.oldPassword && userForm.newPassword) {
      try {
        await changePassword({
          oldPassword: userForm.oldPassword,
          newPassword: userForm.newPassword,
        });
        ElMessage.success("密码修改成功，请重新登录");

        // 清空用户状态并跳转到登录页
        userStore.resetState();
        router.push("/login");
        return;
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || "密码修改失败");
        return;
      }
    }

    // TODO: 处理其他信息的更新（昵称、头像等）
    // 这里需要添加更新用户信息的API调用

    // 更新Pinia状态
    userStore.$patch({
      nickname: userForm.nickname,
      avatar: userForm.avatar,
    });

    ElMessage.success("保存成功");
  } catch (error) {
    console.error("表单验证失败", error);
    ElMessage.error("表单验证失败，请检查输入");
  }
};

// 获取用户信息
onMounted(async () => {
  // 如果已经有用户信息，直接使用
  if (userStore.username) {
    userForm.username = userStore.username;
    userForm.nickname = userStore.nickname;
    userForm.avatar = userStore.avatar;
  } else {
    // 否则重新获取
    const userInfo = await userStore.getUserInfoAction();
    if (userInfo) {
      userForm.username = userInfo.username;
      userForm.nickname = userInfo.nickname;
      userForm.email = userInfo.email;
      userForm.avatar = userInfo.avatar;
    }
  }
});
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.profile-card {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.avatar-container {
  text-align: center;
  margin-bottom: 20px;
}

.avatar-uploader {
  margin-top: 10px;
}

.password-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.password-section h3 {
  margin-bottom: 20px;
  color: #606266;
}
</style>
