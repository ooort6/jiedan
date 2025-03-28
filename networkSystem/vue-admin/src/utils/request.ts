import axios from "axios";
import type { InternalAxiosRequestConfig, AxiosResponse } from "axios";
import { ElMessage } from "element-plus";
import router from "@/router";

// 创建axios实例
const service = axios.create({
  baseURL: "/api", // 使用相对路径以便使用Vite代理
  timeout: 5000,
});

// 请求拦截器
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 请求前的处理
    const token = localStorage.getItem("token");
    if (token && config.headers) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }

    // 添加必要的头部
    if (config.headers) {
      config.headers["Content-Type"] = "application/json";
    }

    console.log("发送请求：", config.url, config);
    return config;
  },
  (error) => {
    console.error("请求错误：", error);
    return Promise.reject(error);
  }
);

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log("收到响应：", response);
    return response.data;
  },
  (error) => {
    console.error("响应错误：", error);

    // 处理HTTP错误状态
    if (error.response) {
      switch (error.response.status) {
        case 401:
          ElMessage.error("未授权，请重新登录");
          localStorage.removeItem("token");
          router.push("/login");
          break;
        case 403:
          ElMessage.error("拒绝访问");
          break;
        case 404:
          ElMessage.error("请求的资源不存在");
          break;
        case 500:
          ElMessage.error("服务器错误");
          break;
        default:
          ElMessage.error(error.response.data?.error || "请求失败");
      }
    } else {
      ElMessage.error("网络错误，请检查您的网络连接");
    }

    return Promise.reject(error);
  }
);

export default service;
