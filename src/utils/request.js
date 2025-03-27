import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/user'

// 创建axios实例
const service = axios.create({
  baseURL: process.env.VUE_APP_BASE_API || '/api', // API基础URL
  timeout: 10000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json;charset=utf-8'
  }
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    const userStore = useUserStore()
    // 添加token到请求头
    if (userStore.token) {
      config.headers['Authorization'] = `Bearer ${userStore.token}`
    }
    return config
  },
  error => {
    console.error('请求错误：', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data
    
    // 如果响应成功但是业务状态码不是200，则显示错误信息
    if (res.code !== 200) {
      ElMessage({
        message: res.message || '操作失败',
        type: 'error',
        duration: 5 * 1000
      })
      
      // 特定错误码处理
      if (res.code === 401) {
        // 未授权，需要重新登录
        handleUnauthorized()
      }
      
      return Promise.reject(new Error(res.message || '操作失败'))
    } else {
      return res
    }
  },
  error => {
    console.error('响应错误：', error)
    
    // 获取错误状态码
    const status = error.response ? error.response.status : null
    
    // 根据状态码处理不同情况
    if (status === 401) {
      // 未授权，需要重新登录
      handleUnauthorized()
    } else if (status === 403) {
      ElMessage({
        message: '权限不足，无法访问',
        type: 'error',
        duration: 5 * 1000
      })
    } else if (status === 404) {
      ElMessage({
        message: '请求的资源不存在',
        type: 'error',
        duration: 5 * 1000
      })
    } else if (status === 500) {
      ElMessage({
        message: '服务器内部错误',
        type: 'error',
        duration: 5 * 1000
      })
    } else {
      ElMessage({
        message: error.message || '请求失败',
        type: 'error',
        duration: 5 * 1000
      })
    }
    
    return Promise.reject(error)
  }
)

// 处理未授权情况
function handleUnauthorized() {
  const userStore = useUserStore()
  
  ElMessageBox.confirm(
    '登录状态已过期，您可以继续留在该页面，或者重新登录',
    '系统提示',
    {
      confirmButtonText: '重新登录',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    userStore.resetState()
    // 刷新页面，重定向到登录页
    location.reload()
  }).catch(() => {})
}

// 通用请求方法
export function request(config) {
  return service(config)
}

// 导出封装的请求方法
export default {
  get(url, params, config = {}) {
    return request({
      method: 'get',
      url,
      params,
      ...config
    })
  },
  
  post(url, data, config = {}) {
    return request({
      method: 'post',
      url,
      data,
      ...config
    })
  },
  
  put(url, data, config = {}) {
    return request({
      method: 'put',
      url,
      data,
      ...config
    })
  },
  
  delete(url, params, config = {}) {
    return request({
      method: 'delete',
      url,
      params,
      ...config
    })
  }
} 