<script setup>
/**
 * 酒店卡片（公共组件）：首页推荐、酒店列表、搜索结果三处复用。
 * 信息层级：酒店名 > 星级/评分数字 > 房价 > 设施标签（字号字重逐级递减）
 */
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import CoverImage from './CoverImage.vue'
import StarRate from './StarRate.vue'
import { Location } from '@element-plus/icons-vue'

const props = defineProps({
  hotel: { type: Object, required: true },
  nights: { type: Number, default: 0 },
  checkIn: { type: String, default: '' },
  checkOut: { type: String, default: '' },
  rank: { type: Number, default: 0 } // 榜单名次（1~3 显示角标），仅首页推荐区传入
})

const router = useRouter()

const starText = computed(() => '★'.repeat(props.hotel.star))
const topFacilities = computed(() => (props.hotel.facilities || []).slice(0, 4))
const totalPrice = computed(() =>
  props.nights > 0 ? props.nights * props.hotel.minPrice : 0
)

function open() {
  // 把日历选择的入住/退房日期带到详情页，供下单弹窗预填
  const query = {}
  if (props.nights > 0) query.nights = props.nights
  if (props.checkIn) query.checkIn = props.checkIn
  if (props.checkOut) query.checkOut = props.checkOut
  router.push({ path: `/hotels/${props.hotel.id}`, query })
}
</script>

<template>
  <div class="hotel-card" @click="open">
    <CoverImage :src="hotel.cover" :color="hotel.coverColor" :tag="hotel.coverTag" width="100px" height="100px" />
    <div class="info">
      <div class="name-line">
        <span v-if="rank >= 1 && rank <= 3" class="rank-no" :class="`r${rank}`">{{ rank }}</span>
        <span class="name ellipsis">{{ hotel.name }}</span>
      </div>
      <div class="star-line">
        <span class="star-text">{{ starText }}</span>
        <span class="star-label">{{ hotel.star }} 星级</span>
        <span class="district">{{ hotel.district }}</span>
      </div>
      <div class="rate-line">
        <StarRate :value="hotel.rating" :size="12" :score-size="15" color="#0086f6" />
        <span class="review-count">{{ hotel.reviewCount }} 条评价</span>
      </div>
      <div class="tags">
        <span v-for="f in topFacilities" :key="f" class="chip-line is-blue">{{ f }}</span>
      </div>
      <div class="price-line">
        <span class="price-ctrip price-num">¥{{ hotel.minPrice }}</span>
        <span class="price-unit">起</span>
        <span v-if="nights > 0" class="nights-chip">{{ nights }} 晚约 ¥{{ totalPrice }}</span>
        <span class="addr ellipsis"><el-icon :size="12"><Location /></el-icon>{{ hotel.district }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.hotel-card {
  display: flex;
  gap: 10px;
  padding: 12px 10px;
  background: #fff;
  border-bottom: 1px solid #f2f3f5;
  cursor: pointer;
  transition: background 0.15s;
}
.hotel-card:active {
  background: #fafafa;
}
.info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.name-line {
  display: flex;
  align-items: center;
  gap: 5px;
  min-width: 0;
}
.name {
  font-size: 15.5px;
  font-weight: 600;
}
.star-line {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
}
.star-text {
  color: #ffb400;
  letter-spacing: 1px;
}
.star-label,
.district {
  color: var(--text-light);
}
.rate-line {
  display: flex;
  align-items: center;
  gap: 7px;
}
.review-count {
  font-size: 11.5px;
  color: var(--text-light);
}
.tags {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}
.price-line {
  display: flex;
  align-items: baseline;
  gap: 2px;
}
.price-ctrip {
  color: var(--ctrip-blue);
}
.nights-chip {
  margin-left: 8px;
  font-size: 11px;
  padding: 0 6px;
  line-height: 16px;
  border-radius: 9px;
  background: #fff1e8;
  color: var(--dp-orange);
}
.addr {
  margin-left: auto;
  font-size: 11px;
  color: var(--text-light);
  display: inline-flex;
  align-items: center;
  gap: 2px;
  max-width: 38%;
}
/* 榜单名次角标（首页推荐区） */
.rank-no {
  flex: none;
  width: 16px;
  height: 16px;
  border-radius: 4px;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.r1 {
  background: linear-gradient(135deg, #0086f6, #40a9ff);
}
.r2 {
  background: linear-gradient(135deg, #1890ff, #69c0ff);
}
.r3 {
  background: linear-gradient(135deg, #40a9ff, #91d5ff);
}
</style>
