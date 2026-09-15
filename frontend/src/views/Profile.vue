<script setup>
/**
 * 个人中心（订单业务域）
 * 功能：查看模拟预约订单列表、查看订单详情、模拟执行取消预约操作
 * 数据来源：I8 订单列表 / I10 模拟取消预约（原型无登录注册，展示内存集合中的全部模拟订单）
 */
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getOrders, cancelOrder } from '../api/order'
import NavBar from '../components/NavBar.vue'
import CoverImage from '../components/CoverImage.vue'
import { User, Refresh } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const orders = ref([])
const filter = ref('全部')

const FILTERS = ['全部', '待使用', '已取消']

const shown = computed(() =>
  filter.value === '全部' ? orders.value : orders.value.filter((o) => o.status === filter.value)
)
const pendingCount = computed(() => orders.value.filter((o) => o.status === '待使用').length)
const cancelledCount = computed(() => orders.value.filter((o) => o.status === '已取消').length)
const totalAmount = computed(() =>
  orders.value.filter((o) => o.status === '待使用').reduce((sum, o) => sum + Number(o.amount || 0), 0)
)

async function load() {
  loading.value = true
  try {
    const data = await getOrders()
    orders.value = data.items || []
  } finally {
    loading.value = false
  }
}

async function onCancel(order) {
  try {
    await ElMessageBox.confirm(
      `确认取消订单 ${order.orderNo}（${order.itemName}）吗？取消后状态将变为「已取消」。`,
      '模拟取消预约',
      { confirmButtonText: '确认取消', cancelButtonText: '再想想', type: 'warning' }
    )
  } catch (e) {
    return // 用户放弃取消
  }
  await cancelOrder(order.orderNo)
  ElMessage.success('已取消该预约（仅内存状态变更，后端重启后恢复）')
  load()
}

function goDetail(order) {
  router.push(`/profile/orders/${order.orderNo}`)
}

function statusType(status) {
  return status === '待使用' ? 'warning' : 'info'
}

onMounted(load)
</script>

<template>
  <div>
    <NavBar title="个人中心">
      <template #right>
        <el-icon :size="17" style="cursor: pointer" @click="load"><Refresh /></el-icon>
      </template>
    </NavBar>

    <!-- 模拟用户信息（原型无登录注册） -->
    <div class="user-head">
      <div class="avatar"><el-icon :size="22" color="#fff"><User /></el-icon></div>
      <div class="user-info">
        <div class="user-name">演示用户</div>
        <div class="user-sub">原型无注册登录，展示内存中的全部模拟订单</div>
      </div>
    </div>

    <!-- 订单概览 -->
    <div class="stats">
      <div class="stat">
        <div class="num">{{ orders.length }}</div>
        <div class="label">全部订单</div>
      </div>
      <div class="stat">
        <div class="num">{{ pendingCount }}</div>
        <div class="label">待使用</div>
      </div>
      <div class="stat">
        <div class="num">{{ cancelledCount }}</div>
        <div class="label">已取消</div>
      </div>
      <div class="stat">
        <div class="num">¥{{ totalAmount }}</div>
        <div class="label">待使用金额</div>
      </div>
    </div>

    <!-- 状态筛选 -->
    <div class="filters">
      <span
        v-for="f in FILTERS"
        :key="f"
        class="chip-btn"
        :class="{ on: filter === f }"
        @click="filter = f"
      >{{ f }}</span>
    </div>

    <div v-if="loading" style="padding: 16px">
      <el-skeleton :rows="5" animated />
    </div>

    <template v-else>
      <div v-for="o in shown" :key="o.orderNo" class="order-card">
        <div class="order-top">
          <span class="order-no">订单号 {{ o.orderNo }}</span>
          <el-tag :type="statusType(o.status)" size="small" effect="light">{{ o.status }}</el-tag>
        </div>
        <div class="order-main" @click="goDetail(o)">
          <CoverImage :src="o.cover" :color="o.coverColor" :tag="o.coverTag" width="62px" height="62px" font-size="12px" />
          <div class="order-info">
            <div class="target ellipsis">{{ o.targetName }}</div>
            <div class="item ellipsis">{{ o.itemName }}</div>
            <div class="time">
              {{ o.type === 'hotel' ? '入住' : '预约' }}：{{ o.bookTime }}
              <template v-if="o.nights"> 至 {{ o.checkOut }}（{{ o.nights }} 晚）</template>
            </div>
            <div class="meta">
              <span class="amount">¥{{ o.amount }}</span>
              <span class="count">×{{ o.count }}</span>
            </div>
          </div>
        </div>
        <div class="order-actions">
          <el-button size="small" @click="goDetail(o)">查看详情</el-button>
          <el-button v-if="o.status === '待使用'" size="small" type="danger" plain @click="onCancel(o)">
            模拟取消预约
          </el-button>
        </div>
      </div>

      <div v-if="!shown.length" class="empty-tip">
        暂无{{ filter === '全部' ? '' : filter }}订单，去门店或酒店下单试试
      </div>
    </template>
  </div>
</template>

<style scoped>
.user-head {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 12px;
  background: linear-gradient(120deg, #ff6633, #ff8a5c);
  color: #fff;
}
.avatar {
  width: 46px;
  height: 46px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
}
.user-name {
  font-size: 16px;
  font-weight: 700;
}
.user-sub {
  font-size: 11.5px;
  opacity: 0.92;
  margin-top: 3px;
}
.stats {
  display: flex;
  background: #fff;
  padding: 12px 0;
  margin-bottom: 8px;
}
.stat {
  flex: 1;
  text-align: center;
}
.stat .num {
  font-size: 16px;
  font-weight: 700;
  color: var(--dp-orange);
}
.stat .label {
  font-size: 11px;
  color: var(--text-light);
  margin-top: 2px;
}
.filters {
  display: flex;
  gap: 8px;
  padding: 0 12px 10px;
}
.chip-btn {
  font-size: 12.5px;
  padding: 3px 14px;
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
.order-card {
  background: #fff;
  margin: 0 10px 10px;
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
  overflow: hidden;
}
.order-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px;
  border-bottom: 1px solid #f2f3f5;
}
.order-no {
  font-size: 11.5px;
  color: var(--text-light);
}
.order-main {
  display: flex;
  gap: 10px;
  padding: 10px;
  cursor: pointer;
}
.order-info {
  flex: 1;
  min-width: 0;
}
.target {
  font-size: 14px;
  font-weight: 600;
}
.item {
  font-size: 12px;
  color: var(--text-sub);
  margin: 3px 0;
}
.time {
  font-size: 11.5px;
  color: var(--text-light);
}
.meta {
  margin-top: 4px;
}
.amount {
  color: var(--dp-orange);
  font-weight: 700;
  font-size: 15px;
}
.count {
  font-size: 11px;
  color: var(--text-light);
  margin-left: 6px;
}
.order-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 8px 10px;
  border-top: 1px solid #f2f3f5;
}
</style>
