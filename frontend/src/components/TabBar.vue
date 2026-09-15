<script setup>
/**
 * 底部导航栏（公共组件）
 * 按路由前缀高亮当前 Tab。
 */
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { HomeFilled, Food, OfficeBuilding, User } from '@element-plus/icons-vue'

const tabs = [
  { path: '/', name: '首页', icon: HomeFilled },
  { path: '/shops', name: '本地生活', icon: Food },
  { path: '/hotels', name: '酒店', icon: OfficeBuilding },
  { path: '/profile', name: '个人中心', icon: User }
]

const route = useRoute()
const router = useRouter()

const activePath = computed(() => {
  const p = route.path
  if (p.startsWith('/shops')) return '/shops'
  if (p.startsWith('/hotels')) return '/hotels'
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
  max-width: 480px;
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
