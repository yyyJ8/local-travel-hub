<script setup>
/**
 * 酒店卡片（公共组件）：首页推荐、酒店列表、搜索结果三处复用。
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
  checkOut: { type: String, default: '' }
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
      <div class="name ellipsis">{{ hotel.name }}</div>
      <div class="star-line">
        <span class="star-text">{{ starText }}</span>
        <span class="star-label">{{ hotel.star }} 星级</span>
        <span class="district">{{ hotel.district }}</span>
      </div>
      <div class="rate-line">
        <StarRate :value="hotel.rating" :size="12" color="#0086f6" />
        <span class="review-count">{{ hotel.reviewCount }} 条评价</span>
      </div>
      <div class="tags">
        <span v-for="f in topFacilities" :key="f" class="chip">{{ f }}</span>
      </div>
      <div class="price-line">
        <span class="price-ctrip">¥{{ hotel.minPrice }}</span>
        <span class="unit">起</span>
        <span v-if="nights > 0" class="total">{{ nights }} 晚约 ¥{{ totalPrice }}</span>
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
}
.hotel-card:active {
  background: #fafafa;
}
.info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.name {
  font-size: 15px;
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
  gap: 6px;
}
.review-count {
  font-size: 12px;
  color: var(--text-light);
}
.tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}
.chip {
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 3px;
  background: #eef7ff;
  color: var(--ctrip-blue);
}
.price-line {
  display: flex;
  align-items: baseline;
  gap: 3px;
}
.price-ctrip {
  font-size: 17px;
}
.unit {
  color: var(--text-light);
  font-size: 11px;
}
.total {
  margin-left: 8px;
  font-size: 11px;
  color: var(--dp-orange);
}
.addr {
  margin-left: auto;
  font-size: 11px;
  color: var(--text-light);
  display: inline-flex;
  align-items: center;
  gap: 2px;
  max-width: 40%;
}
</style>
