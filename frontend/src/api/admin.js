import request from './request'

/** D1 平台概览 */
export function getAdminOverview() {
  return request.get('/admin/overview')
}

/** D2 用户列表（含角色与状态） */
export function getAdminUsers() {
  return request.get('/admin/users')
}

/** D3 停用 / 启用账号 */
export function setUserStatus(userId, status) {
  return request.post(`/admin/users/${userId}/status`, { status })
}

/** D4 全平台订单 */
export function getAdminOrders() {
  return request.get('/admin/orders')
}
