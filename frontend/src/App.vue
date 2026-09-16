<script setup>
/**
 * 应用根组件：统一布局（内容区 + 底部导航）
 * 登录页为应用入口：登录页本身不显示底部导航，登录后才进入带底栏的应用界面。
 */
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import TabBar from './components/TabBar.vue'

const route = useRoute()

// 登录页是入口页，不显示底部导航（其余页面均需登录后访问）
const showTabBar = computed(() => route.name !== 'login')
</script>

<template>
  <div class="app-shell">
    <div class="page-body" :class="{ 'no-tabbar': !showTabBar }">
      <router-view v-slot="{ Component }">
        <keep-alive :include="['ShopList', 'HotelList', 'Home']">
          <component :is="Component" />
        </keep-alive>
      </router-view>
    </div>
    <TabBar v-if="showTabBar" />
    <div class="tabbar-holder"></div>
  </div>
</template>

<style scoped>
.tabbar-holder {
  height: 0;
}
.page-body.no-tabbar {
  padding-bottom: 0;
}
</style>
