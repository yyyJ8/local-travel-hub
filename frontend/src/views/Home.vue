<script setup>
/**
 * 首页模块（成员A业务域）
 * 结构：品牌渐变头图（定位 + 悬浮搜索框 + 快捷词）→ 分类入口磁贴 → 轮播推荐位 → 推荐榜单
 * 数据来源：I1 首页推荐接口；搜索跳转 I2（搜索结果页）
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import * as ElIcons from '@element-plus/icons-vue'
// 模板里直接使用的图标需具名导入；分类磁贴的动态图标走 ElIcons 命名空间查找
import { Location, Search } from '@element-plus/icons-vue'
import { getHomeRecommend } from '../api/home'
import ShopCard from '../components/ShopCard.vue'
import HotelCard from '../components/HotelCard.vue'
import CardSkeleton from '../components/CardSkeleton.vue'

const router = useRouter()
const loading = ref(true)
const error = ref('')
const banners = ref([])
const categories = ref([])
const shops = ref([])
const hotels = ref([])

const keyword = ref('')
const city = ref('成都')
const quickKeywords = ['火锅', '咖啡', 'SPA', '酒店']

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

function doSearch(kw) {
  const q = (kw ?? keyword.value).trim()
  if (!q) return
  router.push({ path: '/search', query: { keyword: q } })
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

/** 轮播样式：有本地配图则用「深色渐变遮罩 + 照片」，无图/缺图回退品牌渐变色 */
function bannerStyle(b) {
  const base = { backgroundColor: b.colorFrom }
  if (!b.image) {
    return { ...base, background: `linear-gradient(120deg, ${b.colorFrom}, ${b.colorTo})` }
  }
  return {
    ...base,
    backgroundImage: `linear-gradient(90deg, rgba(0,0,0,0.58) 0%, rgba(0,0,0,0.22) 55%, rgba(0,0,0,0.05) 100%), url("${b.image}")`,
    backgroundSize: 'cover',
    backgroundPosition: 'center'
  }
}

onMounted(load)
</script>

<template>
  <div class="home">
    <!-- 品牌渐变头图 + 悬浮搜索框 -->
    <header class="home-header">
      <div class="loc-row">
        <el-icon :size="14"><Location /></el-icon>
        <span class="city">{{ city }}</span>
        <span class="caret">▾</span>
        <span class="slogan">发现身边的好店 · 好房</span>
      </div>
      <div class="search-box">
        <el-icon :size="15" color="#bbbbbb"><Search /></el-icon>
        <input
          v-model="keyword"
          class="search-input"
          type="text"
          placeholder="搜索美食门店、酒店"
          @keyup.enter="doSearch()"
        />
        <span class="search-btn" @click="doSearch()">搜索</span>
      </div>
      <div class="quick-row">
        <span v-for="k in quickKeywords" :key="k" class="quick-chip" @click="doSearch(k)">{{ k }}</span>
      </div>
    </header>

    <CardSkeleton v-if="loading" :count="4" />

    <div v-else-if="error" class="empty-tip">
      {{ error }}
      <div style="margin-top: 12px">
        <el-button type="primary" size="small" @click="load">重新加载</el-button>
      </div>
    </div>

    <template v-else>
      <!-- 业务分类入口（彩色磁贴） -->
      <div class="categories">
        <div v-for="c in categories" :key="c.id" class="cat-item" @click="openCategory(c)">
          <div class="cat-icon" :style="{ background: `linear-gradient(135deg, ${c.color}, ${c.color}bb)` }">
            <el-icon :size="24" color="#fff"><component :is="iconOf(c.icon)" /></el-icon>
          </div>
          <span class="cat-name">{{ c.name }}</span>
        </div>
      </div>

      <!-- 轮播推荐位（本地照片 + 深色遮罩保证文字可读） -->
      <el-carousel height="176px" :interval="4000" class="banner">
        <el-carousel-item v-for="b in banners" :key="b.id">
          <div class="banner-item" :style="bannerStyle(b)" @click="openBanner(b)">
            <span class="banner-badge">限时活动</span>
            <div class="banner-title">{{ b.title }}</div>
            <div class="banner-sub">{{ b.subtitle }}</div>
            <div class="banner-btn">立即查看 ›</div>
          </div>
        </el-carousel-item>
      </el-carousel>

      <!-- 推荐美食门店 -->
      <section class="block">
        <div class="section-title">
          <span class="bar bar-orange"></span>推荐美食门店
          <span class="rank-badge rank-orange">人气榜</span>
          <span class="more" @click="router.push('/shops')">更多 ›</span>
        </div>
        <ShopCard v-for="(s, i) in shops" :key="s.id" :shop="s" :rank="i + 1" />
      </section>

      <!-- 推荐酒店 -->
      <section class="block">
        <div class="section-title">
          <span class="bar bar-blue"></span>推荐酒店
          <span class="rank-badge rank-blue">好评榜</span>
          <span class="more" @click="router.push('/hotels')">更多 ›</span>
        </div>
        <HotelCard v-for="(h, i) in hotels" :key="h.id" :hotel="h" :rank="i + 1" />
      </section>
    </template>
  </div>
</template>

<style scoped>
/* ---------- 品牌渐变头图 ---------- */
.home-header {
  padding: 14px 12px 16px;
  background: linear-gradient(135deg, #ff6633 0%, #ff8a3c 48%, #ffa940 100%);
  color: #fff;
}
.loc-row {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  margin-bottom: 12px;
}
.loc-row .city {
  font-weight: 700;
}
.loc-row .caret {
  font-size: 10px;
  opacity: 0.9;
}
.loc-row .slogan {
  margin-left: auto;
  font-size: 11.5px;
  opacity: 0.9;
}
.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 40px;
  padding: 0 6px 0 12px;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.14);
}
.search-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 13.5px;
  color: var(--text-main);
}
.search-btn {
  padding: 4px 14px;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #ff6633, #ff8a3c);
  cursor: pointer;
}
.quick-row {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}
.quick-chip {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 11px;
  background: rgba(255, 255, 255, 0.22);
  border: 1px solid rgba(255, 255, 255, 0.45);
  cursor: pointer;
}

/* ---------- 内容区 ---------- */
.loading {
  padding: 16px;
}
.categories {
  display: flex;
  justify-content: space-around;
  padding: 14px 8px 12px;
  background: #fff;
  margin: -10px 10px 10px;
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
  position: relative;
  z-index: 1;
}
.cat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 7px;
  cursor: pointer;
}
.cat-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.14);
  transition: transform 0.15s ease;
}
.cat-item:active .cat-icon {
  transform: scale(0.94);
}
.cat-name {
  font-size: 12.5px;
  color: var(--text-sub);
  font-weight: 500;
}
.banner {
  margin: 0 10px 10px;
  border-radius: var(--card-radius);
  overflow: hidden;
  box-shadow: var(--card-shadow);
}
.banner-item {
  height: 100%;
  color: #fff;
  padding: 22px 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  cursor: pointer;
}
.banner-badge {
  width: fit-content;
  font-size: 11px;
  padding: 1px 8px;
  border-radius: 9px;
  background: rgba(255, 255, 255, 0.9);
  color: var(--dp-orange);
  font-weight: 700;
  margin-bottom: 2px;
}
.banner-title {
  font-size: 22px;
  font-weight: 700;
  text-shadow: 0 1px 8px rgba(0, 0, 0, 0.3);
}
.banner-sub {
  font-size: 13px;
  opacity: 0.95;
}
.banner-btn {
  margin-top: 4px;
  font-size: 12px;
  background: rgba(255, 255, 255, 0.22);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  padding: 3px 10px;
  width: fit-content;
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
.rank-badge {
  font-size: 10.5px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 8px;
  margin-left: 2px;
}
.rank-orange {
  color: var(--dp-orange);
  background: #fff1e8;
}
.rank-blue {
  color: var(--ctrip-blue);
  background: #e8f4ff;
}
.more {
  margin-left: auto;
  font-size: 12px;
  font-weight: 400;
  color: var(--text-light);
  cursor: pointer;
}
</style>
