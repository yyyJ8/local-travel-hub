<script setup>
/**
 * 首页模块（成员A业务域）
 * 功能：轮播推荐位、业务分类入口、推荐美食门店、推荐酒店、关键词搜索
 * 数据来源：I1 首页推荐接口；搜索跳转 I2（搜索结果页）
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import * as ElIcons from '@element-plus/icons-vue'
import { getHomeRecommend } from '../api/home'
import NavBar from '../components/NavBar.vue'
import ShopCard from '../components/ShopCard.vue'
import HotelCard from '../components/HotelCard.vue'

const router = useRouter()
const loading = ref(true)
const error = ref('')
const banners = ref([])
const categories = ref([])
const shops = ref([])
const hotels = ref([])

const iconOf = (name) => ElIcons[name] || ElIcons.Food

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await getHomeRecommend()
    banners.value = data.banners || []
    categories.value = data.categories || []
    shops.value = data.shops || []
    hotels.value = data.hotels || []
  } catch (e) {
    error.value = '首页数据加载失败，请确认后端服务已启动（127.0.0.1:8000）'
  } finally {
    loading.value = false
  }
}

function openBanner(b) {
  if (b.targetType === 'shop' && b.targetId) router.push(`/shops/${b.targetId}`)
  else if (b.targetType === 'hotel' && b.targetId) router.push(`/hotels/${b.targetId}`)
  else if (b.targetType === 'shop') router.push('/shops')
  else router.push('/hotels')
}

function openCategory(c) {
  if (c.targetType === 'hotel') router.push('/hotels')
  else router.push({ path: '/shops', query: { category: c.targetCategory } })
}

onMounted(load)
</script>

<template>
  <div class="home">
    <NavBar show-search />

    <div v-if="loading" class="loading">
      <el-skeleton :rows="6" animated />
    </div>

    <div v-else-if="error" class="empty-tip">
      {{ error }}
      <div style="margin-top: 12px">
        <el-button type="primary" size="small" @click="load">重新加载</el-button>
      </div>
    </div>

    <template v-else>
      <!-- 轮播推荐位 -->
      <el-carousel height="150px" :interval="4000" class="banner">
        <el-carousel-item v-for="b in banners" :key="b.id">
          <div
            class="banner-item"
            :style="{ background: `linear-gradient(120deg, ${b.colorFrom}, ${b.colorTo})` }"
            @click="openBanner(b)"
          >
            <div class="banner-title">{{ b.title }}</div>
            <div class="banner-sub">{{ b.subtitle }}</div>
            <div class="banner-btn">立即查看 ›</div>
          </div>
        </el-carousel-item>
      </el-carousel>

      <!-- 业务分类入口 -->
      <div class="categories">
        <div v-for="c in categories" :key="c.id" class="cat-item" @click="openCategory(c)">
          <div class="cat-icon" :style="{ background: c.color }">
            <el-icon :size="22" color="#fff"><component :is="iconOf(c.icon)" /></el-icon>
          </div>
          <span class="cat-name">{{ c.name }}</span>
        </div>
      </div>

      <!-- 推荐美食门店 -->
      <section class="block">
        <div class="section-title">
          <span class="bar bar-orange"></span>推荐美食门店
          <span class="more" @click="router.push('/shops')">更多 ›</span>
        </div>
        <ShopCard v-for="s in shops" :key="s.id" :shop="s" />
      </section>

      <!-- 推荐酒店 -->
      <section class="block">
        <div class="section-title">
          <span class="bar bar-blue"></span>推荐酒店
          <span class="more" @click="router.push('/hotels')">更多 ›</span>
        </div>
        <HotelCard v-for="h in hotels" :key="h.id" :hotel="h" />
      </section>
    </template>
  </div>
</template>

<style scoped>
.loading {
  padding: 16px;
}
.banner {
  margin: 10px;
  border-radius: var(--card-radius);
  overflow: hidden;
}
.banner-item {
  height: 100%;
  color: #fff;
  padding: 26px 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
}
.banner-title {
  font-size: 21px;
  font-weight: 700;
  text-shadow: 0 1px 6px rgba(0, 0, 0, 0.18);
}
.banner-sub {
  font-size: 13px;
  opacity: 0.95;
}
.banner-btn {
  margin-top: 6px;
  font-size: 12px;
  background: rgba(255, 255, 255, 0.22);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  padding: 3px 10px;
  width: fit-content;
}
.categories {
  display: flex;
  justify-content: space-around;
  padding: 14px 8px 10px;
  background: #fff;
  margin: 0 10px 10px;
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
}
.cat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}
.cat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.12);
}
.cat-name {
  font-size: 12px;
  color: var(--text-sub);
}
.block {
  background: #fff;
  margin: 0 10px 10px;
  border-radius: var(--card-radius);
  overflow: hidden;
  box-shadow: var(--card-shadow);
}
.section-title {
  padding: 12px 10px 4px;
}
.bar {
  width: 3px;
  height: 15px;
  border-radius: 2px;
  display: inline-block;
}
.bar-orange {
  background: var(--dp-orange);
}
.bar-blue {
  background: var(--ctrip-blue);
}
.more {
  margin-left: auto;
  font-size: 12px;
  font-weight: 400;
  color: var(--text-light);
  cursor: pointer;
}
</style>
