<script setup>
/**
 * 酒店列表页（旅行住宿业务域）
 * 功能：酒店图片/名称/星级/价格/服务标签展示；日历选择入住与退房时间；
 *      按价格、星级、设施筛选；按价格优先、好评优先排序
 * 数据来源：I5 酒店列表接口（晚数由后端按日历区间计算后回传）
 */
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { getHotels, getFacilities } from '../api/hotel'
import NavBar from '../components/NavBar.vue'
import HotelCard from '../components/HotelCard.vue'
import { Refresh, Calendar } from '@element-plus/icons-vue'

const SORTS = [
  { label: '好评优先', value: 'popularity' },
  { label: '价格优先', value: 'priceAsc' },
  { label: '价格从高到低', value: 'priceDesc' },
  { label: '评分优先', value: 'rating' }
]
const STARS = [
  { label: '星级不限', value: '' },
  { label: '5 星', value: 5 },
  { label: '4 星', value: 4 },
  { label: '3 星', value: 3 }
]
const PRICE_RANGES = [
  { label: '价格不限', value: '', min: null, max: null },
  { label: '600 元以上', value: 'gt600', min: 600, max: null },
  { label: '300 - 600 元', value: 'mid', min: 300, max: 600 },
  { label: '300 元以下', value: 'lt300', min: null, max: 300 }
]

const toStr = (d) => {
  const dt = new Date(d)
  return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`
}
const addDays = (n) => toStr(new Date(Date.now() + n * 86400000))

const dateRange = ref([addDays(1), addDays(3)]) // 默认演示：明天入住、住 2 晚
const dateShortcuts = [
  { text: '今天入住 · 1 晚', value: () => [addDays(0), addDays(1)] },
  { text: '明天入住 · 2 晚', value: () => [addDays(1), addDays(3)] },
  { text: '周末 · 3 晚', value: () => [addDays(2), addDays(5)] }
]

const query = reactive({
  star: '',
  priceRange: '',
  facilities: [],
  sortBy: 'popularity'
})

const list = ref([])
const total = ref(0)
const nights = ref(0)
const facilityOptions = ref([])
const loading = ref(false)

const priceRangeObj = computed(() => PRICE_RANGES.find((p) => p.value === query.priceRange) || PRICE_RANGES[0])

async function load() {
  loading.value = true
  try {
    const params = { city: '成都', sortBy: query.sortBy }
    // 空串表示「不限」：Element Plus 的 el-option 不接受 null 作为 value，故用空串哨兵值
    if (query.star !== '') params.star = query.star
    if (priceRangeObj.value.min !== null) params.minPrice = priceRangeObj.value.min
    if (priceRangeObj.value.max !== null) params.maxPrice = priceRangeObj.value.max
    if (query.facilities.length) params.facilities = query.facilities
    if (dateRange.value && dateRange.value.length === 2) {
      params.checkIn = dateRange.value[0]
      params.checkOut = dateRange.value[1]
    }
    const data = await getHotels(params)
    list.value = data.items || []
    total.value = data.total || 0
    nights.value = data.nights || 0
  } finally {
    loading.value = false
  }
}

function toggleFacility(f) {
  const i = query.facilities.indexOf(f)
  if (i >= 0) query.facilities.splice(i, 1)
  else query.facilities.push(f)
}

function reset() {
  query.star = ''
  query.priceRange = ''
  query.facilities = []
  query.sortBy = 'popularity'
  dateRange.value = [addDays(1), addDays(3)]
}

// 筛选条件与日历变化均触发重新查询（deep 监听已覆盖 dateRange，无需重复注册）
watch(() => [query.star, query.priceRange, query.sortBy, query.facilities.length, dateRange.value], load, { deep: true })
onMounted(async () => {
  facilityOptions.value = await getFacilities()
  load()
})
</script>

<template>
  <div>
    <NavBar title="酒店" show-back color="#0086f6" />

    <!-- 日历 + 筛选 + 排序 -->
    <div class="filter-bar">
      <div class="date-line">
        <el-icon :size="14" color="#0086f6"><Calendar /></el-icon>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          size="small"
          unlink-panels
          range-separator="至"
          start-placeholder="入住日期"
          end-placeholder="退房日期"
          value-format="YYYY-MM-DD"
          :shortcuts="dateShortcuts"
          style="width: 100%"
        />
      </div>
      <div class="selects">
        <el-select v-model="query.sortBy" size="small" style="width: 118px">
          <el-option v-for="s in SORTS" :key="s.value" :label="s.label" :value="s.value" />
        </el-select>
        <el-select v-model="query.star" size="small" style="width: 104px">
          <el-option v-for="s in STARS" :key="String(s.value)" :label="s.label" :value="s.value" />
        </el-select>
        <el-select v-model="query.priceRange" size="small" style="width: 122px">
          <el-option v-for="p in PRICE_RANGES" :key="String(p.value)" :label="p.label" :value="p.value" />
        </el-select>
      </div>
      <div class="facility-line">
        <span
          v-for="f in facilityOptions"
          :key="f"
          class="chip-btn"
          :class="{ on: query.facilities.includes(f) }"
          @click="toggleFacility(f)"
        >{{ f }}</span>
        <span class="reset" @click="reset"><el-icon :size="12"><Refresh /></el-icon>重置</span>
      </div>
    </div>

    <div class="count-line">
      成都 · 符合条件酒店 <b>{{ total }}</b> 家
      <span v-if="nights > 0">｜ {{ dateRange?.[0] }} 至 {{ dateRange?.[1] }} 共 <b>{{ nights }}</b> 晚</span>
    </div>

    <div v-if="loading" style="padding: 16px">
      <el-skeleton :rows="6" animated />
    </div>
    <template v-else>
      <HotelCard
        v-for="h in list"
        :key="h.id"
        :hotel="h"
        :nights="nights"
        :check-in="dateRange?.[0] || ''"
        :check-out="dateRange?.[1] || ''"
      />
      <div v-if="!list.length" class="empty-tip">没有符合条件的酒店，试试放宽筛选条件</div>
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
.date-line {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}
.selects {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
}
.facility-line {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  padding-bottom: 2px;
  align-items: center;
}
.facility-line::-webkit-scrollbar {
  display: none;
}
.chip-btn {
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 12px;
  background: #f4f5f7;
  color: var(--text-sub);
  cursor: pointer;
  white-space: nowrap;
  flex: none;
}
.chip-btn.on {
  background: #e8f4ff;
  color: var(--ctrip-blue);
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
  flex: none;
}
.count-line {
  padding: 8px 12px;
  font-size: 12px;
  color: var(--text-sub);
  background: #fff;
}
.count-line b {
  color: var(--ctrip-blue);
}
</style>
