<script setup>
/**
 * 订单详情页（订单业务域）
 * 功能：查看订单完整信息、模拟取消预约
 * 数据来源：I9 订单详情 / I10 模拟取消预约
 */
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getOrderDetail, cancelOrder } from '../api/order'
import NavBar from '../components/NavBar.vue'
import CoverImage from '../components/CoverImage.vue'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const order = ref(null)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    order.value = await getOrderDetail(route.params.orderNo)
  } catch (e) {
    error.value = '订单不存在或已丢失（原型数据存于内存，后端重启后新增订单会丢失）'
  } finally {
    loading.value = false
  }
}

async function onCancel() {
  try {
    await ElMessageBox.confirm('确认取消该预约吗？', '模拟取消预约', {
      confirmButtonText: '确认取消',
      cancelButtonText: '再想想',
      type: 'warning'
    })
  } catch (e) {
    return
  }
  const updated = await cancelOrder(order.value.orderNo)
  order.value = updated
  ElMessage.success('已取消该预约（仅内存状态变更，后端重启后恢复）')
}

onMounted(load)
</script>

<template>
  <div>
    <NavBar title="订单详情" show-back />

    <div v-if="loading" style="padding: 16px">
      <el-skeleton :rows="7" animated />
    </div>
    <div v-else-if="error" class="empty-tip">{{ error }}</div>

    <template v-else-if="order">
      <!-- 状态条 -->
      <div class="status-bar" :class="order.status === '待使用' ? 'pending' : 'cancelled'">
        <div class="status-text">{{ order.status === '待使用' ? '预约成功，待到店使用' : '该预约已取消' }}</div>
        <div class="status-no">订单号：{{ order.orderNo }}</div>
      </div>

      <!-- 预约对象 -->
      <section class="block">
        <div class="target-row">
          <CoverImage :color="order.coverColor" :tag="order.coverTag" width="58px" height="58px" font-size="12px" />
          <div class="target-info">
            <div class="target-name">{{ order.targetName }}</div>
            <div class="item-name">{{ order.itemName }}</div>
          </div>
        </div>
        <div class="rows">
          <div class="row"><span class="k">预约类型</span><span class="v">{{ order.type === 'hotel' ? '酒店房型' : '门店团购套餐' }}</span></div>
          <div class="row"><span class="k">{{ order.type === 'hotel' ? '入住日期' : '预约时间' }}</span><span class="v">{{ order.bookTime }}</span></div>
          <div v-if="order.nights" class="row"><span class="k">退房日期</span><span class="v">{{ order.checkOut }}</span></div>
          <div v-if="order.nights" class="row"><span class="k">入住晚数</span><span class="v">{{ order.nights }} 晚</span></div>
          <div class="row"><span class="k">{{ order.type === 'hotel' ? '房间数' : '份数' }}</span><span class="v">{{ order.count }}</span></div>
          <div class="row"><span class="k">预约人</span><span class="v">{{ order.name }}</span></div>
          <div class="row"><span class="k">手机号</span><span class="v">{{ order.phone }}</span></div>
          <div class="row"><span class="k">下单时间</span><span class="v">{{ order.createdAt }}</span></div>
          <div class="row total"><span class="k">合计金额</span><span class="v price">¥{{ order.amount }}</span></div>
        </div>
      </section>

      <el-alert
        type="info"
        :closable="false"
        style="margin: 0 10px"
        title="原型说明：本订单保存在后端内存集合中，未做数据库持久化；后端服务重启后，本次新增订单与取消状态将全部丢失。"
      />

      <div class="actions">
        <el-button @click="router.push('/profile')">返回订单列表</el-button>
        <el-button v-if="order.status === '待使用'" type="danger" plain @click="onCancel">模拟取消预约</el-button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.status-bar {
  padding: 16px 14px;
  color: #fff;
}
.status-bar.pending {
  background: linear-gradient(120deg, #ff6633, #ff8a5c);
}
.status-bar.cancelled {
  background: linear-gradient(120deg, #8c8c8c, #b0b0b0);
}
.status-text {
  font-size: 16px;
  font-weight: 700;
}
.status-no {
  font-size: 11.5px;
  opacity: 0.9;
  margin-top: 5px;
}
.block {
  background: #fff;
  margin: 10px;
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
  overflow: hidden;
}
.target-row {
  display: flex;
  gap: 10px;
  padding: 12px 10px;
  border-bottom: 1px solid #f2f3f5;
}
.target-name {
  font-size: 14px;
  font-weight: 600;
}
.item-name {
  font-size: 12px;
  color: var(--text-sub);
  margin-top: 4px;
}
.rows {
  padding: 4px 10px 10px;
}
.row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  padding: 8px 0;
  border-bottom: 1px dashed #f2f3f5;
}
.row:last-child {
  border-bottom: none;
}
.k {
  color: var(--text-light);
}
.v {
  color: var(--text-main);
  max-width: 62%;
  text-align: right;
}
.row.total .price {
  color: var(--dp-orange);
  font-weight: 700;
  font-size: 16px;
}
.actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding: 14px 12px 20px;
}
</style>
