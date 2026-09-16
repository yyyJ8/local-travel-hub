/**
 * 登录态（组合式函数，全局单例）
 *
 * 说明：
 * - 令牌与用户信息同时存内存与 localStorage，刷新页面后由路由守卫读取本地会话恢复；
 * - 后端重启后令牌失效，任何请求返回 401 时由 Axios 拦截器清理会话并跳登录页；
 * - 原型口径：无令牌签名/有效期/刷新机制，仅用于课程演示。
 */
import { reactive, computed } from 'vue'
import { login as apiLogin, register as apiRegister, logout as apiLogout, fetchMe } from '../api/auth'
import { readSession, writeSession, clearSession } from '../utils/session'

const saved = readSession()

const state = reactive({
  token: saved.token || '',
  user: saved.user || null,
  submitting: false
})

export function useAuth() {
  const isLoggedIn = computed(() => !!state.token && !!state.user)
  const user = computed(() => state.user)
  const role = computed(() => state.user?.role || '')
  const isMerchant = computed(() => role.value === 'merchant')
  const isAdmin = computed(() => role.value === 'admin')
  const displayName = computed(() => state.user?.nickname || state.user?.username || '未登录')

  const ROLE_TEXT = { user: '普通用户', merchant: '商家', admin: '管理员' }
  const roleText = computed(() => ROLE_TEXT[role.value] || '')

  function apply(token, userInfo) {
    state.token = token || ''
    state.user = userInfo || null
    writeSession(state.token, state.user)
  }

  async function login(username, password) {
    state.submitting = true
    try {
      const data = await apiLogin(username, password)
      apply(data.token, data.user)
      return data.user
    } finally {
      state.submitting = false
    }
  }

  async function register(payload) {
    state.submitting = true
    try {
      const data = await apiRegister(payload)
      apply(data.token, data.user) // 注册后直接进入登录态
      return data.user
    } finally {
      state.submitting = false
    }
  }

  async function logout() {
    try {
      if (state.token) await apiLogout()
    } catch (e) {
      /* 会话已失效时忽略注销报错 */
    }
    state.token = ''
    state.user = null
    clearSession()
  }

  /** 刷新页面后校验本地令牌是否仍然有效（后端重启会失效） */
  async function verify() {
    if (!state.token) return null
    try {
      const info = await fetchMe()
      apply(state.token, info)
      return info
    } catch (e) {
      state.token = ''
      state.user = null
      clearSession()
      return null
    }
  }

  return {
    state,
    user,
    role,
    roleText,
    displayName,
    isLoggedIn,
    isMerchant,
    isAdmin,
    login,
    register,
    logout,
    verify
  }
}
