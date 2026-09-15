import request from './request'

/** I7 模拟预约下单（提交后写入后端内存集合） */
export function createOrder(body) {
  return request.post('/orders', body)
}

/** I8 查询内存模拟订单列表 */
export function getOrders() {
  return request.get('/orders')
}

/** I9 订单详情 */
export function getOrderDetail(orderNo) {
  return request.get(`/orders/${orderNo}`)
}

/** I10 模拟取消预约（内存中将状态改为「已取消」） */
export function cancelOrder(orderNo) {
  return request.post(`/orders/${orderNo}/cancel`)
}
