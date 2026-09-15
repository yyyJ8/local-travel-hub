import request from './request'

/** 可选城市列表（供门店/酒店列表页的城市切换器渲染） */
export function getCities() {
  return request.get('/meta/cities')
}
