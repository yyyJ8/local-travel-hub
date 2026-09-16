/**
 * 会话存储（前端）
 * 单独成模块的原因：Axios 拦截器需要读令牌，而 composables/useAuth 又依赖 api/auth，
 * 若拦截器直接依赖 useAuth 会形成循环引用。此处作为唯一的会话读写入口。
 */
const STORAGE_KEY = 'ctrip-prototype-session'

let cache = null

export function readSession() {
  if (cache) return cache
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    cache = raw ? JSON.parse(raw) : { token: '', user: null }
  } catch (e) {
    cache = { token: '', user: null } // 本地数据损坏时直接忽略
  }
  if (!cache || typeof cache !== 'object') cache = { token: '', user: null }
  return cache
}

export function writeSession(token, user) {
  cache = { token: token || '', user: user || null }
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(cache))
  } catch (e) {
    /* 隐私模式等场景写入失败不影响本次会话 */
  }
}

export function clearSession() {
  cache = { token: '', user: null }
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch (e) {
    /* 忽略 */
  }
}

export function getToken() {
  return readSession().token || ''
}

export function getUser() {
  return readSession().user || null
}
