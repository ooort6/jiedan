import request from "@/utils/request";

interface LoginParams {
  username: string;
  password: string;
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
  user?: {
    username: string;
    email?: string;
    avatar?: string;
    roles?: string[];
  };
  data?: T;
}

// 登录接口
export function login(data: LoginParams): Promise<ApiResponse> {
  return request({
    url: "/api/auth/login",
    method: "post",
    data,
    headers: {
      "Content-Type": "application/json",
    },
  });
}

// 注册接口
export function register(data: RegisterParams): Promise<ApiResponse> {
  return request({
    url: "/api/auth/register",
    method: "post",
    data,
  });
}

// 获取当前用户信息
export function getUserInfo(): Promise<ApiResponse> {
  return request({
    url: "/api/auth/info",
    method: "get",
  });
}

// 登出接口
export function logout(): Promise<ApiResponse> {
  return request({
    url: "/api/auth/logout",
    method: "post",
  });
}

// 修改密码接口
export function changePassword(data: {
  oldPassword: string;
  newPassword: string;
}) {
  return request({
    url: "/api/auth/change-password",
    method: "post",
    data,
  });
}
