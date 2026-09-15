<script setup>
/**
 * 预约下单弹窗（公共组件，成员B/成员C 共用）
 * 功能：选择套餐/房型 → 填写姓名、手机号 → 选择预约/入住时间 → 提交 → 预约成功反馈
 * 接口：I7 模拟预约下单（提交后写入后端内存集合）
 * 原型说明：不做真实支付、消息通知与服务端校验，前端仅做基础必填校验。
 */
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { createOrder } from '../api/order'
import CommonDialog from './CommonDialog.vue'
import { CircleCheckFilled } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  type: { type: String, default: 'shop' },          // shop | hotel
  targetId: { type: String, default: '' },
  targetName: { type: String, default: '' },
  item: { type: Object, default: null },            // 套餐或房型对象
  nights: { type: Number, default: 0 },
  defaultBookTime: { type: String, default: '' },   // 由列表页日历带入的入住日期
  defaultCheckOut: { type: String, default: '' }    // 由列表页日历带入的退房日期
})

const emit = defineEmits(['update:modelValue', 'success'])

const toStr = (d) => {
  const dt = new Date(d)
  return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`
}
const addDays = (n) => toStr(new Date(Date.now() + n * 86400000))

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})

const form = ref({
  name: '',
  phone: '',
  // 初始化即套用列表页日历带入的日期，避免弹窗首次渲染时先显示默认日期
  bookTime: props.defaultBookTime || addDays(1),
  checkOut: props.defaultCheckOut || addDays(3),
  count: 1
})
const submitting = ref(false)
const successOrder = ref(null)

const isHotel = computed(() => props.type === 'hotel')
const nightCount = computed(() => {
  if (!isHotel.value) return 0
  const d1 = new Date(form.value.bookTime)
  const d2 = new Date(form.value.checkOut)
  const n = Math.round((d2 - d1) / 86400000)
  return n > 0 ? n : 1
})
const amount = computed(() => {
  const unit = Number(props.item?.price || 0)
  const cnt = Number(form.value.count || 1)
  return isHotel.value ? unit * cnt * nightCount.value : unit * cnt
})

watch(visible, (v) => {
  if (v) {
    // 打开弹窗时重置表单，并清空上一次的成功状态；酒店场景带入列表页日历选择的日期
    successOrder.value = null
    form.value = {
      name: '',
      phone: '',
      bookTime: props.defaultBookTime || addDays(1),
      checkOut: props.defaultCheckOut || addDays(3),
      count: 1
    }
  }
})

function validate() {
  if (!form.value.name.trim()) {
    ElMessage.warning('请填写预约人姓名')
    return false
  }
  if (!/^\d{11}$/.test(form.value.phone.trim())) {
    ElMessage.warning('请填写 11 位手机号')
    return false
  }
  if (!form.value.bookTime) {
    ElMessage.warning('请选择预约/入住时间')
    return false
  }
  if (isHotel.value && !form.value.checkOut) {
    ElMessage.warning('请选择退房时间')
    return false
  }
  return true
}

async function submit() {
  if (!validate()) return
  submitting.value = true
  try {
    const order = await createOrder({
      type: props.type,
      targetId: props.targetId,
      itemId: props.item.id,
      name: form.value.name.trim(),
      phone: form.value.phone.trim(),
      bookTime: form.value.bookTime,
      checkOut: isHotel.value ? form.value.checkOut : '',
      count: Number(form.value.count || 1)
    })
    successOrder.value = order
    ElMessage.success('预约提交成功')
    emit('success', order)
  } finally {
    submitting.value = false
  }
}

function closeSuccess() {
  visible.value = false
}
</script>

<template>
  <CommonDialog
    v-model="visible"
    :title="successOrder ? '预约成功' : '预约下单'"
    :show-footer="!successOrder"
    :confirm-loading="submitting"
    confirm-text="提交预约"
    @confirm="submit"
  >
    <!-- 下单成功反馈 -->
    <div v-if="successOrder" class="success">
      <el-icon :size="46" color="#67c23a"><CircleCheckFilled /></el-icon>
      <div class="success-title">预约提交成功</div>
      <div class="success-no">订单号：{{ successOrder.orderNo }}</div>
      <div class="success-info">
        <div>{{ successOrder.targetName }}</div>
        <div>{{ successOrder.itemName }}</div>
        <div>
          {{ successOrder.bookTime }}
          <span v-if="successOrder.nights"> 至 {{ successOrder.checkOut }}（{{ successOrder.nights }} 晚）</span>
        </div>
        <div class="price">合计 ¥{{ successOrder.amount }}</div>
      </div>
      <el-alert
        type="success"
        :closable="false"
        style="margin-top: 10px; text-align: left"
        title="订单已写入后端内存集合，可在「个人中心」查看；后端服务重启后该订单将丢失（原型限制）"
      />
      <el-button type="primary" round style="margin-top: 14px; width: 100%" @click="closeSuccess">
        知道了
      </el-button>
    </div>

    <!-- 下单表单 -->
    <el-form v-else label-width="76px" label-position="left" size="default">
      <el-form-item label="预约项目">
        <div class="item-box">
          <div class="item-name">{{ item?.name }}</div>
          <div class="item-target">{{ targetName }}</div>
        </div>
      </el-form-item>
      <el-form-item label="姓名" required>
        <el-input v-model="form.name" placeholder="请输入预约人姓名" maxlength="12" />
      </el-form-item>
      <el-form-item label="手机号" required>
        <el-input v-model="form.phone" placeholder="请输入 11 位手机号" maxlength="11" />
      </el-form-item>
      <el-form-item :label="isHotel ? '入住日期' : '预约时间'" required>
        <el-date-picker
          v-model="form.bookTime"
          type="date"
          value-format="YYYY-MM-DD"
          placeholder="选择日期"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item v-if="isHotel" label="退房日期" required>
        <el-date-picker
          v-model="form.checkOut"
          type="date"
          value-format="YYYY-MM-DD"
          placeholder="选择退房日期"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item :label="isHotel ? '房间数' : '份数'">
        <el-input-number v-model="form.count" :min="1" :max="9" size="default" />
      </el-form-item>
      <div class="amount-line">
        <span class="amount-label">
          ¥{{ item?.price }}{{ isHotel ? ' / 晚' : ' / 份' }}
          <template v-if="isHotel"> × {{ form.count }} 间 × {{ nightCount }} 晚</template>
          <template v-else> × {{ form.count }} 份</template>
        </span>
        <span class="amount-total">合计 ¥{{ amount }}</span>
      </div>
      <div class="tip">原型不做真实支付与短信通知，提交后仅在界面反馈并写入后端内存。</div>
    </el-form>
  </CommonDialog>
</template>

<style scoped>
.item-box {
  line-height: 1.5;
}
.item-name {
  font-weight: 600;
  font-size: 13px;
}
.item-target {
  font-size: 12px;
  color: var(--text-light);
}
.amount-line {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  padding: 8px 2px 0;
  border-top: 1px dashed var(--border-color);
}
.amount-label {
  font-size: 12px;
  color: var(--text-sub);
}
.amount-total {
  font-size: 16px;
  font-weight: 700;
  color: var(--dp-orange);
}
.tip {
  font-size: 11px;
  color: var(--text-light);
  margin-top: 6px;
  line-height: 1.6;
}
.success {
  text-align: center;
  padding: 6px 0 2px;
}
.success-title {
  font-size: 16px;
  font-weight: 700;
  margin: 8px 0 4px;
}
.success-no {
  font-size: 12px;
  color: var(--text-light);
  margin-bottom: 10px;
}
.success-info {
  font-size: 13px;
  line-height: 1.9;
  background: #fafbfc;
  border-radius: 8px;
  padding: 10px;
}
</style>
