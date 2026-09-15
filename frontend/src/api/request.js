import axios from 'axios'
import { ElMessage } from 'element-plus'

/**
 * Axios 统一封装（开发架构：请求层与页面解耦）
 * - 后端统一响应结构 { code, message, data }，此处自动解包出 data
 * - baseURL 使用相对路径 /api，由 Vite 代理转发到本地后端（无需处理跨域）
 */
const request = axios.create({
  baseURL: '/api',
  timeout: 10000
})

request.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res && typeof res === 'object' && 'code' in res) {
      if (res.code === 0) return res.data
      ElMessage.error(res.message || '接口返回异常')
      return Promise.reject(new Error(res.message || '接口返回异常'))
    }
    return res
  },
  (error) => {
    ElMessage.error('网络请求失败，请确认后端服务已启动（127.0.0.1:8000）')
    return Promise.reject(error)
  }
)

export default request
