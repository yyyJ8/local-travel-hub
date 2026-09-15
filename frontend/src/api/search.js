import request from './request'

/** I2 关键词搜索：同时检索门店与酒店 */
export function searchAll(keyword) {
  return request.get('/search', { params: { keyword } })
}
