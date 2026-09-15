<script setup>
/**
 * 门店详情页（本地生活业务域）
 * 功能：门店基础信息、营业时间、地址；团购套餐信息；模拟用户评论
 * 数据来源：I4 门店详情接口
 */
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getShopDetail } from '../api/shop'
import NavBar from '../components/NavBar.vue'
import StarRate from '../components/StarRate.vue'
import CoverImage from '../components/CoverImage.vue'
import OrderDialog from '../components/OrderDialog.vue'
import { Location, Clock, Phone, Ticket } from '@element-plus/icons-vue'

const route = useRoute()
const loading = ref(true)
const shop = ref(null)
const error = ref('')

// 下单弹窗（阶段8：接通 I7 模拟下单接口）
const showOrder = ref(false)
const selectedItem = ref(null)

async function load() {
  loading.value = true
  error.value = ''
  try {
    shop.value = await getShopDetail(route.params.id)
  } catch (e) {
    error.value = '门店信息加载失败或门店不存在'
  } finally {
    loading.value = false
  }
}

function buy(pkg) {
  selectedItem.value = pkg
  showOrder.value = true
}

function avatarStyle(color) {
  return { background: color }
}

onMounted(load)
</script>

<template>
  <div>
    <NavBar title="门店详情" show-back />

    <div v-if="loading" style="padding: 16px">
      <el-skeleton :rows="8" animated />
    </div>
    <div v-else-if="error" class="empty-tip">{{ error }}</div>

    <template v-else-if="shop">
      <!-- 门店基础信息 -->
      <div class="head">
        <CoverImage :color="shop.coverColor" :tag="shop.coverTag" width="100%" height="150px" radius="0" font-size="20px" />
        <div class="head-info">
          <h1 class="shop-name">{{ shop.name }}</h1>
          <div class="rate-line">
            <StarRate :value="shop.rating" :size="15" />
            <span class="review-count">{{ shop.reviewCount }} 条评论</span>
            <span class="chip chip-orange">{{ shop.subCategory }}</span>
            <span class="chip">{{ shop.district }}</span>
          </div>
          <div class="info-row">
            <el-icon :size="13"><Location /></el-icon>
            <span>{{ shop.address }}</span>
          </div>
          <div class="info-row">
            <el-icon :size="13"><Clock /></el-icon>
            <span>营业时间：{{ shop.businessHours }}</span>
          </div>
          <div class="info-row">
            <el-icon :size="13"><Phone /></el-icon>
            <span>{{ shop.phone }}</span>
          </div>
        </div>
      </div>

      <!-- 团购套餐 -->
      <section class="block">
        <div class="section-title"><span class="bar bar-orange"></span>团购套餐（{{ shop.packages.length }}）</div>
        <div v-for="p in shop.packages" :key="p.id" class="pkg">
          <div class="pkg-left">
            <div class="pkg-name ellipsis">{{ p.name }}</div>
            <div class="pkg-desc ellipsis-2">{{ p.desc }}</div>
            <div class="pkg-sold">已售 {{ p.sold }} 份</div>
          </div>
          <div class="pkg-right">
            <div class="price-line">
              <span class="price">¥{{ p.price }}</span>
              <span class="origin">¥{{ p.originalPrice }}</span>
            </div>
            <el-button type="warning" size="small" round @click="buy(p)">立即抢购</el-button>
          </div>
        </div>
      </section>

      <!-- 用户评论 -->
      <section class="block">
        <div class="section-title"><span class="bar bar-orange"></span>用户评论（{{ shop.comments.length }}）</div>
        <div v-for="c in shop.comments" :key="c.id" class="comment">
          <div class="avatar" :style="avatarStyle(c.avatarColor)">{{ c.user.slice(0, 1) }}</div>
          <div class="comment-body">
            <div class="comment-head">
              <span class="user">{{ c.user }}</span>
              <span class="date">{{ c.date }}</span>
            </div>
            <StarRate :value="c.rating" :size="12" />
            <div class="comment-text">{{ c.content }}</div>
          </div>
        </div>
      </section>

      <!-- 底部操作条 -->
      <div class="action-bar">
        <div class="action-price">
          <span class="label">团购价</span>
          <span class="price">¥{{ shop.packages[0]?.price ?? shop.avgPrice }}</span>
          <span class="label">起</span>
        </div>
        <el-button type="warning" round class="action-btn" @click="buy(shop.packages[0])">
          <el-icon style="margin-right: 4px"><Ticket /></el-icon>立即预约
        </el-button>
      </div>
    </template>

    <OrderDialog
      v-model="showOrder"
      type="shop"
      :target-id="shop?.id || ''"
      :target-name="shop?.name || ''"
      :item="selectedItem"
    />
  </div>
</template>

<style scoped>
.head-info {
  padding: 12px;
  background: #fff;
}
.shop-name {
  font-size: 18px;
  margin: 0 0 8px;
}
.rate-line {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}
.review-count {
  font-size: 12px;
  color: var(--text-light);
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
.info-row {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  font-size: 12px;
  color: var(--text-sub);
  line-height: 1.8;
}
.block {
  background: #fff;
  margin: 10px;
  border-radius: var(--card-radius);
  overflow: hidden;
  box-shadow: var(--card-shadow);
}
.section-title {
  padding: 12px 10px 6px;
}
.bar {
  width: 3px;
  height: 15px;
  border-radius: 2px;
  display: inline-block;
  background: var(--dp-orange);
}
.pkg {
  display: flex;
  gap: 10px;
  padding: 10px;
  border-top: 1px solid #f2f3f5;
}
.pkg-left {
  flex: 1;
  min-width: 0;
}
.pkg-name {
  font-size: 14px;
  font-weight: 600;
}
.pkg-desc {
  font-size: 12px;
  color: var(--text-light);
  margin: 4px 0;
}
.pkg-sold {
  font-size: 11px;
  color: var(--dp-orange);
}
.pkg-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: center;
  gap: 6px;
}
.price-line {
  display: flex;
  align-items: baseline;
  gap: 6px;
}
.price {
  color: var(--dp-orange);
  font-weight: 700;
  font-size: 17px;
}
.origin {
  font-size: 11px;
  color: #bbb;
  text-decoration: line-through;
}
.comment {
  display: flex;
  gap: 8px;
  padding: 10px;
  border-top: 1px solid #f2f3f5;
}
.avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  color: #fff;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex: none;
}
.comment-body {
  flex: 1;
  min-width: 0;
}
.comment-head {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-light);
  margin-bottom: 2px;
}
.comment-head .user {
  color: var(--text-main);
  font-weight: 600;
}
.comment-text {
  font-size: 13px;
  line-height: 1.6;
  margin-top: 4px;
}
.action-bar {
  position: fixed;
  bottom: 56px;
  left: 0;
  right: 0;
  margin: 0 auto;
  max-width: 480px;
  height: 52px;
  background: #fff;
  border-top: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  padding: 0 12px;
  gap: 10px;
  z-index: 25;
}
.action-price {
  flex: 1;
  display: flex;
  align-items: baseline;
  gap: 4px;
}
.action-price .label {
  font-size: 11px;
  color: var(--text-light);
}
.action-btn {
  min-width: 120px;
}
</style>
