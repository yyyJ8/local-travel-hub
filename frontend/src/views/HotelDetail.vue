<script setup>
/**
 * 酒店详情页（旅行住宿业务域）
 * 功能：酒店图文信息；不同房型、房价、配套服务；模拟酒店评价
 * 数据来源：I6 酒店详情接口
 */
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getHotelDetail } from '../api/hotel'
import NavBar from '../components/NavBar.vue'
import StarRate from '../components/StarRate.vue'
import CoverImage from '../components/CoverImage.vue'
import OrderDialog from '../components/OrderDialog.vue'
import { Location, Check, Calendar } from '@element-plus/icons-vue'

const route = useRoute()
const loading = ref(true)
const error = ref('')
const hotel = ref(null)

const nights = computed(() => Number(route.query.nights || 0))

// 阶段8 将把此处替换为公共下单弹窗（OrderDialog）并真正提交订单
const showOrder = ref(false)
const selectedRoom = ref(null)

const starText = computed(() => '★'.repeat(hotel.value?.star || 0))

async function load() {
  loading.value = true
  error.value = ''
  try {
    hotel.value = await getHotelDetail(route.params.id)
  } catch (e) {
    error.value = '酒店信息加载失败或酒店不存在'
  } finally {
    loading.value = false
  }
}

function book(room) {
  selectedRoom.value = room
  showOrder.value = true
}

function totalOf(room) {
  return nights.value > 0 ? room.price * nights.value : room.price
}

onMounted(load)
</script>

<template>
  <div>
    <NavBar title="酒店详情" show-back color="#0086f6" />

    <div v-if="loading" style="padding: 16px">
      <el-skeleton :rows="8" animated />
    </div>
    <div v-else-if="error" class="empty-tip">{{ error }}</div>

    <template v-else-if="hotel">
      <!-- 酒店图文信息 -->
      <CoverImage :color="hotel.coverColor" :tag="hotel.coverTag" width="100%" height="160px" radius="0" font-size="20px" />
      <div class="head-info">
        <h1 class="hotel-name">{{ hotel.name }}</h1>
        <div class="star-line">
          <span class="star-text">{{ starText }}</span>
          <span class="star-label">{{ hotel.star }} 星级</span>
          <span class="chip">{{ hotel.district }}</span>
        </div>
        <div class="rate-line">
          <StarRate :value="hotel.rating" :size="15" color="#0086f6" />
          <span class="review-count">{{ hotel.reviewCount }} 条评价</span>
        </div>
        <div class="info-row">
          <el-icon :size="13"><Location /></el-icon><span>{{ hotel.address }}</span>
        </div>
        <div class="facilities">
          <span v-for="f in hotel.facilities" :key="f" class="chip chip-blue">
            <el-icon :size="11"><Check /></el-icon>{{ f }}
          </span>
        </div>
        <p class="intro">{{ hotel.intro }}</p>
      </div>

      <!-- 房型与房价 -->
      <section class="block">
        <div class="section-title">
          <span class="bar bar-blue"></span>房型与房价（{{ hotel.rooms.length }}）
          <span v-if="nights > 0" class="nights-tip">
            <el-icon :size="12"><Calendar /></el-icon> 已选 {{ nights }} 晚
          </span>
        </div>
        <div v-for="r in hotel.rooms" :key="r.id" class="room">
          <div class="room-left">
            <div class="room-name">{{ r.name }}</div>
            <div class="room-meta">
              <span class="chip">{{ r.area }}㎡</span>
              <span class="chip">{{ r.bedType }}</span>
              <span class="chip">{{ r.breakfast }}</span>
              <span class="chip">{{ r.window }}</span>
            </div>
            <div class="room-cancel">{{ r.cancelPolicy }} · 仅剩 {{ r.remain }} 间</div>
          </div>
          <div class="room-right">
            <div class="price-line">
              <span class="price-ctrip">¥{{ r.price }}</span>
              <span class="origin">¥{{ r.originalPrice }}</span>
            </div>
            <div v-if="nights > 0" class="total-line">{{ nights }} 晚共 ¥{{ totalOf(r) }}</div>
            <el-button type="primary" size="small" round @click="book(r)">预订</el-button>
          </div>
        </div>
      </section>

      <!-- 酒店评价 -->
      <section class="block">
        <div class="section-title"><span class="bar bar-blue"></span>酒店评价（{{ hotel.reviews.length }}）</div>
        <div v-for="v in hotel.reviews" :key="v.id" class="comment">
          <div class="avatar" :style="{ background: v.avatarColor }">{{ v.user.slice(0, 1) }}</div>
          <div class="comment-body">
            <div class="comment-head">
              <span class="user">{{ v.user }}</span>
              <span class="date">{{ v.date }}</span>
            </div>
            <StarRate :value="v.rating" :size="12" color="#0086f6" />
            <div class="room-tag">入住房型：{{ v.roomType }}</div>
            <div class="comment-text">{{ v.content }}</div>
          </div>
        </div>
      </section>

      <!-- 底部操作条 -->
      <div class="action-bar">
        <div class="action-price">
          <span class="price-ctrip">¥{{ hotel.minPrice }}</span>
          <span class="label">起 / 晚</span>
        </div>
        <el-button type="primary" round class="action-btn" @click="book(hotel.rooms[0])">立即预订</el-button>
      </div>
    </template>

    <OrderDialog
      v-model="showOrder"
      type="hotel"
      :target-id="hotel?.id || ''"
      :target-name="hotel?.name || ''"
      :item="selectedRoom"
      :default-book-time="String(route.query.checkIn || '')"
      :default-check-out="String(route.query.checkOut || '')"
    />
  </div>
</template>

<style scoped>
.head-info {
  padding: 12px;
  background: #fff;
}
.hotel-name {
  font-size: 18px;
  margin: 0 0 8px;
}
.star-line {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.star-text {
  color: #ffb400;
  letter-spacing: 1px;
}
.star-label {
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
.chip-blue {
  background: #e8f4ff;
  color: var(--ctrip-blue);
  display: inline-flex;
  align-items: center;
  gap: 2px;
}
.rate-line {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.review-count {
  font-size: 12px;
  color: var(--text-light);
}
.info-row {
  display: flex;
  gap: 6px;
  font-size: 12px;
  color: var(--text-sub);
  margin-bottom: 8px;
}
.facilities {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 8px;
}
.intro {
  font-size: 12.5px;
  line-height: 1.8;
  color: var(--text-sub);
  margin: 0;
  background: #fafbfc;
  padding: 8px 10px;
  border-radius: 6px;
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
  display: flex;
  align-items: center;
  gap: 6px;
}
.bar {
  width: 3px;
  height: 15px;
  border-radius: 2px;
  display: inline-block;
}
.bar-blue {
  background: var(--ctrip-blue);
}
.nights-tip {
  margin-left: auto;
  font-size: 11px;
  font-weight: 400;
  color: var(--ctrip-blue);
  display: inline-flex;
  align-items: center;
  gap: 3px;
}
.room {
  display: flex;
  gap: 10px;
  padding: 10px;
  border-top: 1px solid #f2f3f5;
}
.room-left {
  flex: 1;
  min-width: 0;
}
.room-name {
  font-size: 14px;
  font-weight: 600;
}
.room-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin: 6px 0;
}
.room-cancel {
  font-size: 11px;
  color: var(--dp-orange);
}
.room-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: center;
  gap: 4px;
}
.price-line {
  display: flex;
  align-items: baseline;
  gap: 6px;
}
.price-ctrip {
  font-size: 17px;
}
.origin {
  font-size: 11px;
  color: #bbb;
  text-decoration: line-through;
}
.total-line {
  font-size: 11px;
  color: var(--text-light);
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
.room-tag {
  font-size: 11px;
  color: var(--text-light);
  margin-top: 3px;
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
