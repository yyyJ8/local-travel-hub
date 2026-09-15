import request from './request'

/** I3 门店列表（筛选：keyword/category/minRating/maxPrice；排序：sortBy） */
export function getShops(params) {
  return request.get('/shops', { params })
}

/** I4 门店详情（含团购套餐与用户评论） */
export function getShopDetail(shopId) {
  return request.get(`/shops/${shopId}`)
}
