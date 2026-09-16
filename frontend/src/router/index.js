import { createRouter, createWebHashHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import { readSession } from '../utils/session'

/**
 * 全局路由配置（开发架构：页面级组件按业务域组织）
 * 采用 hash 模式，避免本地演示时的服务端路由回退问题。
 *
 * 权限约定：
 * - 浏览类页面（首页 / 搜索 / 门店 / 酒店）免登录，与点评、携程的 C 端行为一致；
 * - 下单、个人中心、订单详情需登录（meta.requiresAuth）；
 * - 商家后台 / 管理后台需对应角色（meta.roles）。
 */
const routes = [
  { path: '/', name: 'home', component: () => import('../views/Home.vue'), meta: { title: '首页' } },
  { path: '/search', name: 'search', component: () => import('../views/SearchResult.vue'), meta: { title: '搜索' } },
  { path: '/shops', name: 'shopList', component: () => import('../views/ShopList.vue'), meta: { title: '本地生活' } },
  { path: '/shops/:id', name: 'shopDetail', component: () => import('../views/ShopDetail.vue'), meta: { title: '门店详情' } },
  { path: '/hotels', name: 'hotelList', component: () => import('../views/HotelList.vue'), meta: { title: '酒店' } },
  { path: '/hotels/:id', name: 'hotelDetail', component: () => import('../views/HotelDetail.vue'), meta: { title: '酒店详情' } },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录 / 注册', guestOnly: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../views/Profile.vue'),
    meta: { title: '我的订单', requiresAuth: true }
  },
  {
    path: '/profile/orders/:orderNo',
    name: 'orderDetail',
    component: () => import('../views/OrderDetail.vue'),
    meta: { title: '订单详情', requiresAuth: true }
  },
  {
    path: '/merchant',
    name: 'merchant',
    component: () => import('../views/MerchantHome.vue'),
    meta: { title: '商家后台', requiresAuth: true, roles: ['merchant', 'admin'] }
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('../views/AdminHome.vue'),
    meta: { title: '管理后台', requiresAuth: true, roles: ['admin'] }
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

  if (to.meta?.requiresAuth && !loggedIn) {
    ElMessage.warning('请先登录后再访问该页面')
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  if (to.meta?.roles && loggedIn) {
    const role = session.user?.role || ''
    if (!to.meta.roles.includes(role)) {
      ElMessage.error('当前账号无权访问该页面')
      return { path: '/' }
    }
  }

  if (to.meta?.guestOnly && loggedIn) {
    return { path: '/' } // 已登录时不再进入登录页
  }

  return true
})

router.afterEach((to) => {
  document.title = to.meta?.title ? `${to.meta.title} · 演示原型系统` : '本地生活旅行 · 演示原型系统'
})

export default router
