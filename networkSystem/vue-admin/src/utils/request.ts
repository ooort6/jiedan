import axios from "axios";
import type { AxiosRequestConfig, AxiosResponse } from "axios";
import { ElMessage } from "element-plus";
import router from "@/router";

// 创建axios实例
const service = axios.create({
  baseURL: "", // 使用空字符串作为基础路径
  timeout: 15000, // 请求超时时间
  withCredentials: false, // 确保不发送cookies
});

// 请求拦截器
service.interceptors.request.use(
  (config: AxiosRequestConfig) => {
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
    const res = response.data;

    // 判断请求是否成功
    if (res.code && res.code !== 200) {
      ElMessage.error(res.message || "请求失败");

      // 处理401错误（未授权）
      if (res.code === 401) {
        localStorage.removeItem("token");
        router.push("/login");
      }

      return Promise.reject(new Error(res.message || "请求失败"));
    }

    // 直接返回响应数据，而不是整个 response 对象
    return res;
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
          ElMessage.error(error.message || "请求失败");
      }
    } else {
      ElMessage.error("网络错误，请检查您的网络连接");
    }

    return Promise.reject(error);
  }
);

export default service;
