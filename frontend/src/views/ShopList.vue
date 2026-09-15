<script setup>
/**
 * 门店列表页（本地生活业务域）
 * 功能：门店图片/名称/评分/人均/业务标签展示；按品类、评分、人均筛选；按人气、评分、价格排序
 * 数据来源：I3 门店列表接口
 */
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getShops } from '../api/shop'
import NavBar from '../components/NavBar.vue'
import ShopCard from '../components/ShopCard.vue'
import { Refresh } from '@element-plus/icons-vue'

const route = useRoute()

const CATEGORIES = [
  { label: '全部', value: '' },
  { label: '美食', value: '美食' },
  { label: '休闲娱乐', value: '休闲娱乐' }
]
const SORTS = [
  { label: '人气优先', value: 'popularity' },
  { label: '评分优先', value: 'rating' },
  { label: '人均从低到高', value: 'priceAsc' },
  { label: '人均从高到低', value: 'priceDesc' }
]
const RATINGS = [
  { label: '评分不限', value: '' },
  { label: '4.5 分以上', value: 4.5 },
  { label: '4.0 分以上', value: 4.0 }
]
const PRICES = [
  { label: '人均不限', value: '' },
  { label: '人均 ≤ 50', value: 50 },
  { label: '人均 ≤ 100', value: 100 },
  { label: '人均 ≤ 150', value: 150 }
]

const query = reactive({
  category: String(route.query.category || ''),
  minRating: '',
  maxPrice: '',
  sortBy: 'popularity'
})

const list = ref([])
const total = ref(0)
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const params = { category: query.category, sortBy: query.sortBy }
    // 空串表示「不限」：Element Plus 的 el-option 不接受 null 作为 value，故用空串哨兵值
    if (query.minRating !== '') params.minRating = query.minRating
    if (query.maxPrice !== '') params.maxPrice = query.maxPrice
    const data = await getShops(params)
    list.value = data.items || []
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

function reset() {
  query.category = ''
  query.minRating = ''
  query.maxPrice = ''
  query.sortBy = 'popularity'
}

watch(() => [query.category, query.minRating, query.maxPrice, query.sortBy], load)
watch(() => route.query.category, (v) => { query.category = String(v || '') })
onMounted(load)
</script>

<template>
  <div>
    <NavBar title="本地生活" show-back />

    <!-- 筛选与排序 -->
    <div class="filter-bar">
      <div class="chips">
        <span
          v-for="c in CATEGORIES"
          :key="c.value"
          class="chip-btn"
          :class="{ on: query.category === c.value }"
          @click="query.category = c.value"
        >{{ c.label }}</span>
        <span class="reset" @click="reset">
          <el-icon :size="12"><Refresh /></el-icon>重置
        </span>
      </div>
      <div class="selects">
        <el-select v-model="query.sortBy" size="small" style="width: 118px">
          <el-option v-for="s in SORTS" :key="s.value" :label="s.label" :value="s.value" />
        </el-select>
        <el-select v-model="query.minRating" size="small" style="width: 104px">
          <el-option v-for="r in RATINGS" :key="String(r.value)" :label="r.label" :value="r.value" />
        </el-select>
        <el-select v-model="query.maxPrice" size="small" style="width: 104px">
          <el-option v-for="p in PRICES" :key="String(p.value)" :label="p.label" :value="p.value" />
        </el-select>
      </div>
    </div>

    <div class="count-line">符合条件的门店共 <b>{{ total }}</b> 家</div>

    <div v-if="loading" style="padding: 16px">
      <el-skeleton :rows="6" animated />
    </div>
    <template v-else>
      <ShopCard v-for="s in list" :key="s.id" :shop="s" />
      <div v-if="!list.length" class="empty-tip">没有符合条件的门店，试试放宽筛选条件</div>
    </template>
  </div>
</template>

<style scoped>
.filter-bar {
  position: sticky;
  top: 48px;
  z-index: 10;
  background: #fff;
  padding: 8px 10px 6px;
  border-bottom: 1px solid var(--border-color);
}
.chips {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.chip-btn {
  font-size: 13px;
  padding: 3px 12px;
  border-radius: 12px;
  background: #f4f5f7;
  color: var(--text-sub);
  cursor: pointer;
}
.chip-btn.on {
  background: #fff1e8;
  color: var(--dp-orange);
  font-weight: 600;
}
.reset {
  margin-left: auto;
  font-size: 12px;
  color: var(--text-light);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 2px;
}
.selects {
  display: flex;
  gap: 6px;
}
.count-line {
  padding: 8px 12px;
  font-size: 12px;
  color: var(--text-sub);
  background: #fff;
}
.count-line b {
  color: var(--dp-orange);
}
</style>
