<script setup>
/**
 * 门店卡片（公共组件）：首页推荐、门店列表、搜索结果三处复用。
 */
import { useRouter } from 'vue-router'
import CoverImage from './CoverImage.vue'
import StarRate from './StarRate.vue'
import { Location } from '@element-plus/icons-vue'

const props = defineProps({
  shop: { type: Object, required: true }
})

const router = useRouter()

function open() {
  router.push(`/shops/${props.shop.id}`)
}
</script>

<template>
  <div class="shop-card" @click="open">
    <CoverImage :src="shop.cover" :color="shop.coverColor" :tag="shop.coverTag" width="92px" height="92px" />
    <div class="info">
      <div class="name ellipsis">{{ shop.name }}</div>
      <div class="rate-line">
        <StarRate :value="shop.rating" />
        <span class="review-count">{{ shop.reviewCount }} 条</span>
      </div>
      <div class="tags">
        <span class="chip chip-orange">{{ shop.subCategory }}</span>
        <span class="chip">{{ shop.district }}</span>
        <span v-if="shop.packageCount" class="chip chip-blue">{{ shop.packageCount }} 个团购</span>
      </div>
      <div class="price-line">
        <span class="price">¥{{ shop.avgPrice }}</span>
        <span class="unit">/人</span>
        <span class="addr ellipsis">
          <el-icon :size="12"><Location /></el-icon>{{ shop.address }}
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.shop-card {
  display: flex;
  gap: 10px;
  padding: 12px 10px;
  background: #fff;
  border-bottom: 1px solid #f2f3f5;
  cursor: pointer;
}
.shop-card:active {
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
  background: #f4f5f7;
  color: var(--text-sub);
}
.chip-orange {
  background: #fff1e8;
  color: var(--dp-orange);
}
.chip-blue {
  background: #e8f4ff;
  color: var(--ctrip-blue);
}
.price-line {
  display: flex;
  align-items: baseline;
  gap: 2px;
}
.price {
  color: var(--dp-orange);
  font-weight: 700;
  font-size: 16px;
}
.unit {
  color: var(--text-light);
  font-size: 11px;
}
.addr {
  margin-left: 8px;
  font-size: 11px;
  color: var(--text-light);
  display: inline-flex;
  align-items: center;
  gap: 2px;
  max-width: 55%;
}
</style>
