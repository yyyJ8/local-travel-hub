import request from './request'

/** A1 用户注册（仅普通用户角色，注册成功后直接返回令牌） */
export function register(payload) {
  return request.post('/auth/register', payload)
}

/** A2 登录 → { token, user } */
export function login(username, password) {
  return request.post('/auth/login', { username, password })
}

/** A3 注销（删除后端内存会话） */
export function logout() {
  return request.post('/auth/logout')
}

/** A4 当前登录用户（刷新页面时恢复登录态） */
export function fetchMe() {
  return request.get('/auth/me')
}
