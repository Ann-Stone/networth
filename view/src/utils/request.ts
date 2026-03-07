import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResponse } from '@/types/models'

const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
})

// Request interceptor — attach auth token if present
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// Response interceptor — unwrap data or throw error
service.interceptors.response.use(
  (response: AxiosResponse<ApiResponse<unknown>>) => {
    const res = response.data
    if (res.status === 1) {
      return res.data as any
    }
    ElMessage.error(res.message || '請求失敗')
    return Promise.reject(new Error(res.message || 'Error'))
  },
  (error) => {
    const msg = error.response?.data?.message || error.message || '網路錯誤'
    ElMessage.error(msg)
    return Promise.reject(error)
  },
)

export default service
