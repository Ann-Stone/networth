import axios from 'axios'
import type { AxiosInstance, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResponse } from '@/types/models'

const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
})

service.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error),
)

service.interceptors.response.use(
  (response: AxiosResponse<ApiResponse<unknown>>) => {
    const res = response.data
    if (res.status === 1) {
      return res.data as any
    }
    ElMessage.error(res.msg || '請求失敗')
    return Promise.reject(new Error(res.msg || 'Error'))
  },
  (error) => {
    const msg = error.response?.data?.msg || error.message || '網路錯誤'
    ElMessage.error(msg)
    return Promise.reject(error)
  },
)

export default service
