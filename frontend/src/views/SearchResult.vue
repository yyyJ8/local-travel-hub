<script setup>
/**
 * 搜索结果页（首页搜索跳转目标）
 * 数据来源：I2 关键词搜索接口，门店与酒店分区展示。
 */
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { searchAll } from '../api/search'
import NavBar from '../components/NavBar.vue'
import ShopCard from '../components/ShopCard.vue'
import HotelCard from '../components/HotelCard.vue'

const route = useRoute()
const loading = ref(false)
const keyword = ref('')
const shops = ref([])
const hotels = ref([])

async function load(kw) {
  keyword.value = kw || ''
  if (!keyword.value) {
    shops.value = []
    hotels.value = []
    return
  }
  loading.value = true
  try {
    const data = await searchAll(keyword.value)
    shops.value = data.shops || []
    hotels.value = data.hotels || []
  } finally {
    loading.value = false
  }
}

onMounted(() => load(route.query.keyword))
watch(() => route.query.keyword, (v) => load(v))
</script>

<template>
  <div>
    <NavBar show-back show-search :keyword="String(route.query.keyword || '')" />

    <div v-if="loading" style="padding: 16px">
      <el-skeleton :rows="6" animated />
    </div>

    <template v-else>
      <div class="summary">
        “{{ keyword }}” 共找到 {{ shops.length + hotels.length }} 条结果
        （门店 {{ shops.length }} · 酒店 {{ hotels.length }}）
      </div>

      <section v-if="shops.length" class="block">
        <div class="section-title"><span class="bar bar-orange"></span>相关门店</div>
        <ShopCard v-for="s in shops" :key="s.id" :shop="s" />
      </section>

      <section v-if="hotels.length" class="block">
        <div class="section-title"><span class="bar bar-blue"></span>相关酒店</div>
        <HotelCard v-for="h in hotels" :key="h.id" :hotel="h" />
      </section>

      <div v-if="!shops.length && !hotels.length" class="empty-tip">
        没有找到与“{{ keyword }}”相关的结果，试试「火锅」「酒店」「青城山」
      </div>
    </template>
  </div>
</template>

<style scoped>
.summary {
  padding: 10px 12px;
  font-size: 12px;
  color: var(--text-sub);
  background: #fff;
}
.block {
  background: #fff;
  margin: 10px;
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
</style>
