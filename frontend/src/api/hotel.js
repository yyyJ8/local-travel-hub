import request from './request'

/** I5 酒店列表（筛选：city/minPrice/maxPrice/star/facilities；日历：checkIn/checkOut；排序：sortBy） */
export function getHotels(params) {
  return request.get('/hotels', { params })
}

/** I6 酒店详情（含房型房价与酒店评价） */
export function getHotelDetail(hotelId) {
  return request.get(`/hotels/${hotelId}`)
}

/** 酒店设施选项（筛选面板动态渲染） */
export function getFacilities() {
  return request.get('/hotels/facilities')
}
