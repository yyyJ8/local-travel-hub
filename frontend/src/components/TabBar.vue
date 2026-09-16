<script setup>
/**
 * 底部导航栏（公共组件）
 * 按路由前缀高亮当前 Tab；按登录角色动态增减入口（商家/管理员多一个后台 Tab）。
 */
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { HomeFilled, Food, OfficeBuilding, User, Shop, Setting } from '@element-plus/icons-vue'
import { useAuth } from '../composables/useAuth'

const auth = useAuth()
const route = useRoute()
const router = useRouter()

const tabs = computed(() => {
  const list = [
    { path: '/', name: '首页', icon: HomeFilled },
    { path: '/shops', name: '本地生活', icon: Food },
    { path: '/hotels', name: '酒店', icon: OfficeBuilding }
  ]
  if (auth.isMerchant.value) list.push({ path: '/merchant', name: '商家后台', icon: Shop })
  if (auth.isAdmin.value) list.push({ path: '/admin', name: '管理后台', icon: Setting })
  list.push({ path: '/profile', name: auth.isLoggedIn.value ? '我的订单' : '我的', icon: User })
  return list
})

const activePath = computed(() => {
  const p = route.path
  if (p.startsWith('/shops')) return '/shops'
  if (p.startsWith('/hotels')) return '/hotels'
  if (p.startsWith('/merchant')) return '/merchant'
  if (p.startsWith('/admin')) return '/admin'
  if (p.startsWith('/profile')) return '/profile'
  return '/'
})

function go(path) {
  if (route.path !== path) router.push(path)
}
</script>

<template>
  <nav class="tabbar">
    <div
      v-for="t in tabs"
      :key="t.path"
      class="tab"
      :class="{ active: activePath === t.path }"
      @click="go(t.path)"
    >
      <el-icon :size="19"><component :is="t.icon" /></el-icon>
      <span class="tab-name">{{ t.name }}</span>
    </div>
  </nav>
</template>

<style scoped>
.tabbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  margin: 0 auto;
  max-width: var(--shell-width);
  height: 56px;
  display: flex;
  background: #ffffff;
  border-top: 1px solid var(--border-color);
  z-index: 30;
}
.tab {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  color: #9aa0a6;
  cursor: pointer;
  transition: color 0.15s;
}
.tab.active {
  color: var(--dp-orange);
}
.tab-name {
  font-size: 11px;
}
</style>
