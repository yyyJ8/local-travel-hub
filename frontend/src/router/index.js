import { createRouter, createWebHashHistory } from 'vue-router'

/**
 * 全局路由配置（开发架构：页面级组件按业务域组织）
 * 采用 hash 模式，避免本地演示时的服务端路由回退问题。
 */
const routes = [
  { path: '/', name: 'home', component: () => import('../views/Home.vue'), meta: { title: '首页' } },
  { path: '/search', name: 'search', component: () => import('../views/SearchResult.vue'), meta: { title: '搜索' } },
  { path: '/shops', name: 'shopList', component: () => import('../views/ShopList.vue'), meta: { title: '本地生活' } },
  { path: '/shops/:id', name: 'shopDetail', component: () => import('../views/ShopDetail.vue'), meta: { title: '门店详情' } },
  { path: '/hotels', name: 'hotelList', component: () => import('../views/HotelList.vue'), meta: { title: '酒店' } },
  { path: '/hotels/:id', name: 'hotelDetail', component: () => import('../views/HotelDetail.vue'), meta: { title: '酒店详情' } },
  { path: '/profile', name: 'profile', component: () => import('../views/Profile.vue'), meta: { title: '个人中心' } },
  { path: '/profile/orders/:orderNo', name: 'orderDetail', component: () => import('../views/OrderDetail.vue'), meta: { title: '订单详情' } }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
})

router.afterEach((to) => {
  document.title = to.meta?.title ? `${to.meta.title} · 演示原型系统` : '本地生活旅行 · 演示原型系统'
})

export default router
