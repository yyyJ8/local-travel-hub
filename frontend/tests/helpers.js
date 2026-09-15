/**
 * 测试辅助：统一挂载环境（内存路由 + Element Plus）
 */
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import ElementPlus from 'element-plus'

const blank = { template: '<div />' }

export function makeRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: blank },
      { path: '/search', component: blank },
      { path: '/shops', component: blank },
      { path: '/shops/:id', component: blank },
      { path: '/hotels', component: blank },
      { path: '/hotels/:id', component: blank },
      { path: '/profile', component: blank },
      { path: '/profile/orders/:orderNo', component: blank }
    ]
  })
}

export async function mountView(component, route = '/', options = {}) {
  const router = makeRouter()
  await router.push(route)
  await router.isReady()
  const wrapper = mount(component, {
    global: { plugins: [router, ElementPlus] },
    ...options
  })
  return { wrapper, router }
}

/** 等待所有 pending 的 Promise 链与渲染刷新完成 */
export async function flush(times = 6) {
  for (let i = 0; i < times; i++) {
    await Promise.resolve()
  }
  await new Promise((r) => setTimeout(r, 0))
}
