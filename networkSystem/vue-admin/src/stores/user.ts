import { defineStore } from "pinia";
import { login, getUserInfo, logout, register } from "@/api/auth";
import { ElMessage } from "element-plus";
import router from "@/router";
import { ref } from "vue";

interface UserState {
  token: string;
  username: string;
  nickname: string;
  avatar: string;
}

interface UserInfo {
  username: string;
  email?: string;
  avatar?: string;
  roles?: string[];
}

interface RegisterParams {
  username: string;
  email: string;
  password: string;
}

interface ApiResponse<T = any> {
  code: number;
  message: string;
  token?: string;
  user?: UserInfo;
  data?: T;
}

export const useUserStore = defineStore("user", {
  state: (): UserState => ({
    token: localStorage.getItem("token") || "",
    username: "",
    nickname: "",
    avatar: "",
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
  },

  actions: {
    // 登录
    async loginAction(username: string, password: string) {
      try {
        const res = (await login({ username, password })) as ApiResponse;
        if (res.code === 200 && res.token) {
          this.token = res.token;
          localStorage.setItem("token", res.token);
          if (res.user) {
            this.username = res.user.username;
            this.nickname = res.user.username;
            this.avatar = res.user.avatar || "";
          }
          ElMessage.success(res.message || "登录成功");
          router.push("/");
          return true;
        }
        return false;
      } catch (error) {
        console.error("登录失败", error);
        return false;
      }
    },

    // 获取用户信息
    async getUserInfoAction() {
      try {
        const res = await getUserInfo();
        const { username, nickname, avatar } = res.data;
        this.username = username;
        this.nickname = nickname || username;
        this.avatar = avatar || "";
        return res.data;
      } catch (error) {
        console.error("获取用户信息失败", error);
        return null;
      }
    },

    // 登出
    async logoutAction() {
      try {
        await logout();
        this.resetState();
        ElMessage.success("退出成功");
        router.push("/login");
      } catch (error) {
        console.error("登出失败", error);
      }
    },

    // 重置状态
    resetState() {
      this.token = "";
      this.username = "";
      this.nickname = "";
      this.avatar = "";
      localStorage.removeItem("token");
    },

    // 注册
    async registerAction(params: RegisterParams): Promise<boolean> {
      try {
        const res = await register(params);
        if (res.code === 200) {
          ElMessage.success(res.message || "注册成功");
          return true;
        }
        ElMessage.error(res.message || "注册失败");
        return false;
      } catch (error: any) {
        console.error("注册失败:", error);
        ElMessage.error(error.response?.data?.message || "注册失败，请重试");
        return false;
      }
    },
  },
});
