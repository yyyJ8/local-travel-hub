<script setup>
/**
 * 应用根组件：统一布局（顶部导航 + 内容区 + 底部导航）
 * 内容区由路由视图填充，底部导航在详情页也可保留。
 */
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import TabBar from './components/TabBar.vue'

const route = useRoute()

// 详情页自带导航栏，根组件不再重复渲染顶部栏
const hideTabBar = computed(() => false)
</script>

<template>
  <div class="app-shell">
    <div class="page-body">
      <router-view v-slot="{ Component }">
        <keep-alive :include="['ShopList', 'HotelList', 'Home']">
          <component :is="Component" />
        </keep-alive>
      </router-view>
    </div>
    <TabBar v-if="!hideTabBar" />
    <div class="tabbar-holder"></div>
  </div>
</template>

<style scoped>
.tabbar-holder {
  height: 0;
}
</style>
