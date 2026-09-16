import { createRouter, createWebHashHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import { readSession } from '../utils/session'

/**
 * 全局路由配置（开发架构：页面级组件按业务域组织）
 * 采用 hash 模式，避免本地演示时的服务端路由回退问题。
 *
 * 入口与权限约定（登录优先）：
 * - **登录页是整个应用的入口**：未登录访问任何页面都会被引导到登录页，登录成功后回到目标页面；
 * - 登录后按角色区分可见范围：普通用户用 C 端功能，商家/管理员额外可见各自后台；
 * - 仅登录页标记 meta.public，其余页面默认需要登录（未标记也一律拦住）。
 */
const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录 / 注册', public: true, guestOnly: true }
  },
  { path: '/', name: 'home', component: () => import('../views/Home.vue'), meta: { title: '首页' } },
  { path: '/search', name: 'search', component: () => import('../views/SearchResult.vue'), meta: { title: '搜索' } },
  { path: '/shops', name: 'shopList', component: () => import('../views/ShopList.vue'), meta: { title: '本地生活' } },
  { path: '/shops/:id', name: 'shopDetail', component: () => import('../views/ShopDetail.vue'), meta: { title: '门店详情' } },
  { path: '/hotels', name: 'hotelList', component: () => import('../views/HotelList.vue'), meta: { title: '酒店' } },
  { path: '/hotels/:id', name: 'hotelDetail', component: () => import('../views/HotelDetail.vue'), meta: { title: '酒店详情' } },
  { path: '/profile', name: 'profile', component: () => import('../views/Profile.vue'), meta: { title: '我的订单' } },
  {
    path: '/profile/orders/:orderNo',
    name: 'orderDetail',
    component: () => import('../views/OrderDetail.vue'),
    meta: { title: '订单详情' }
  },
  {
    path: '/merchant',
    name: 'merchant',
    component: () => import('../views/MerchantHome.vue'),
    meta: { title: '商家后台', roles: ['merchant', 'admin'] }
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('../views/AdminHome.vue'),
    meta: { title: '管理后台', roles: ['admin'] }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
})

router.beforeEach((to) => {
  const session = readSession()
  const loggedIn = !!session.token

  // 登录优先：除登录页外，一律要求已登录
  if (!to.meta?.public && !loggedIn) {
    if (to.path !== '/login') {
      ElMessage.warning('请先登录后再进入系统')
      return { path: '/login', query: { redirect: to.fullPath } }
    }
    return true
  }

  // 角色校验：进入非本人角色的后台时拒绝
  if (to.meta?.roles && loggedIn) {
    const role = session.user?.role || ''
    if (!to.meta.roles.includes(role)) {
      ElMessage.error('当前账号无权访问该页面')
      return { path: '/' }
    }
  }

  // 已登录时不再进入登录页
  if (to.meta?.guestOnly && loggedIn) {
    return { path: '/' }
  }

  return true
})

router.afterEach((to) => {
  document.title = to.meta?.title ? `${to.meta.title} · 演示原型系统` : '本地生活旅行 · 演示原型系统'
})

export default router
