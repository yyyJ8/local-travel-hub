<script setup>
/**
 * 门店卡片（公共组件）：首页推荐、门店列表、搜索结果三处复用。
 * 信息层级：门店名 > 评分数字 > 价格 > 标签/地址（字号字重逐级递减）
 */
import { useRouter } from 'vue-router'
import CoverImage from './CoverImage.vue'
import StarRate from './StarRate.vue'
import { Location } from '@element-plus/icons-vue'

const props = defineProps({
  shop: { type: Object, required: true },
  rank: { type: Number, default: 0 } // 榜单名次（1~3 显示角标），仅首页推荐区传入
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
      <div class="name-line">
        <span v-if="rank >= 1 && rank <= 3" class="rank-no" :class="`r${rank}`">{{ rank }}</span>
        <span class="name ellipsis">{{ shop.name }}</span>
      </div>
      <div class="rate-line">
        <StarRate :value="shop.rating" :size="12" :score-size="15" />
        <span class="review-count">{{ shop.reviewCount }} 条评价</span>
      </div>
      <div class="tags">
        <span class="chip-line is-orange">{{ shop.subCategory }}</span>
        <span class="chip-line">{{ shop.district }}</span>
        <span v-if="shop.packageCount" class="chip-line is-blue">{{ shop.packageCount }} 个团购</span>
      </div>
      <div class="price-line">
        <span class="price price-num">¥{{ shop.avgPrice }}</span>
        <span class="price-unit">/人</span>
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
  transition: background 0.15s;
}
.shop-card:active {
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
.price {
  color: var(--dp-orange);
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
  background: linear-gradient(135deg, #ff4d4f, #ff7875);
}
.r2 {
  background: linear-gradient(135deg, #ff7a45, #ffa940);
}
.r3 {
  background: linear-gradient(135deg, #ffa940, #ffc53d);
}
</style>
