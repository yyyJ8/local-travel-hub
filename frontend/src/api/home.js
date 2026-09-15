import request from './request'

/** I1 首页推荐：轮播 + 分类入口 + 推荐门店 + 推荐酒店 */
export function getHomeRecommend() {
  return request.get('/home/recommend')
}
