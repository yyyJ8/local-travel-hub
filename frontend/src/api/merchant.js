import request from './request'

/** M1 商家经营概览（名下门店/酒店 + 订单统计） */
export function getMerchantSummary() {
  return request.get('/merchant/summary')
}

/** M2 我的订单（仅自己名下门店/酒店） */
export function getMerchantOrders() {
  return request.get('/merchant/orders')
}

/** M3 维护门店/酒店信息（营业时间 / 简介） */
export function updateMerchantProfile(body) {
  return request.put('/merchant/profile', body)
}
