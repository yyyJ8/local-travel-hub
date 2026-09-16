<script setup>
/**
 * 商家后台（角色：merchant）
 * 内容：名下门店/酒店概览 → 经营数据 → 我的订单 → 门店信息维护
 * 数据来源：M1 概览 / M2 我的订单 / M3 维护信息（后端按商家 ID 过滤，商家只能看到自己的数据）
 */
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getMerchantSummary, getMerchantOrders, updateMerchantProfile } from '../api/merchant'
import { useAuth } from '../composables/useAuth'
import NavBar from '../components/NavBar.vue'
import CardSkeleton from '../components/CardSkeleton.vue'
import CoverImage from '../components/CoverImage.vue'
import { Refresh, OfficeBuilding, Shop } from '@element-plus/icons-vue'

const auth = useAuth()
const loading = ref(true)
const saving = ref(false)
const summary = ref(null)
const orders = ref([])
const form = ref({ businessHours: '', intro: '' })

const targets = computed(() => summary.value?.targets || [])
const shopTargets = computed(() => targets.value.filter((t) => t.kind === 'shop'))
const hotelTargets = computed(() => targets.value.filter((t) => t.kind === 'hotel'))

async function load() {
  loading.value = true
  try {
    const [s, o] = await Promise.all([getMerchantSummary(), getMerchantOrders()])
    summary.value = s
    orders.value = o.items || []
    form.value.businessHours = s.targets?.[0]?.businessHours || ''
    form.value.intro = s.targets?.[0]?.intro || ''
  } catch (e) {
    /* 错误提示由拦截器统一处理 */
  } finally {
    loading.value = false
  }
}

async function save() {
  if (!form.value.businessHours.trim() && !form.value.intro.trim()) {
    ElMessage.warning('请至少填写营业时间或简介中的一项')
    return
  }
  saving.value = true
  try {
    const res = await updateMerchantProfile({
      businessHours: form.value.businessHours.trim(),
      intro: form.value.intro.trim()
    })
    ElMessage.success(`已保存，更新了 ${res.updated} 个对象（仅内存生效，后端重启后恢复）`)
    load()
  } catch (e) {
    /* 同上 */
  } finally {
    saving.value = false
  }
}

function statusType(status) {
  return status === '待使用' ? 'warning' : 'info'
}

onMounted(load)
</script>

<template>
  <div>
    <NavBar title="商家后台">
      <template #right>
        <el-icon :size="17" style="cursor: pointer" @click="load"><Refresh /></el-icon>
      </template>
    </NavBar>

    <div class="head">
      <div class="head-name">{{ auth.displayName.value }}</div>
      <div class="head-sub">
        <el-tag size="small" type="success" effect="light">{{ auth.roleText.value }}</el-tag>
        <span class="head-id">商家 ID：{{ summary?.merchantId || auth.user.value?.merchantId || '-' }}</span>
      </div>
    </div>

    <CardSkeleton v-if="loading" :count="3" cover="72px" />

    <template v-else>
      <!-- 经营数据 -->
      <div class="stats">
        <div class="stat">
          <div class="num">{{ summary?.targetCount ?? 0 }}</div>
          <div class="label">名下门店/酒店</div>
        </div>
        <div class="stat">
          <div class="num">{{ summary?.orderCount ?? 0 }}</div>
          <div class="label">累计订单</div>
        </div>
        <div class="stat">
          <div class="num">{{ summary?.pendingCount ?? 0 }}</div>
          <div class="label">待使用</div>
        </div>
        <div class="stat">
          <div class="num">¥{{ summary?.pendingAmount ?? 0 }}</div>
          <div class="label">待使用金额</div>
        </div>
      </div>

      <!-- 名下门店 / 酒店 -->
      <section class="block">
        <div class="section-title"><span class="bar"></span>我的门店与酒店</div>
        <div v-for="t in targets" :key="t.id" class="target">
          <CoverImage :src="t.cover" :color="t.coverColor" :tag="t.coverTag" width="72px" height="72px" font-size="12px" />
          <div class="target-info">
            <div class="target-name">
              <el-icon :size="13" color="#999">
                <component :is="t.kind === 'shop' ? Shop : OfficeBuilding" />
              </el-icon>
              {{ t.name }}
            </div>
            <div class="target-meta">
              <span class="chip-line is-plain">{{ t.kind === 'shop' ? '门店' : '酒店' }}</span>
              <span class="chip-line">评分 {{ t.rating }}</span>
              <span class="chip-line">{{ t.reviewCount }} 条评价</span>
            </div>
            <div class="target-sub ellipsis">{{ t.address || t.district }}</div>
          </div>
        </div>
        <div v-if="!targets.length" class="empty-tip">该商家账号暂未绑定门店或酒店</div>
      </section>

      <!-- 我的订单 -->
      <section class="block">
        <div class="section-title"><span class="bar"></span>我的订单（{{ orders.length }}）</div>
        <el-table :data="orders" size="small" style="width: 100%">
          <el-table-column prop="orderNo" label="订单号" width="150" />
          <el-table-column prop="itemName" label="项目" min-width="140" show-overflow-tooltip />
          <el-table-column prop="bookTime" label="预约时间" width="105" />
          <el-table-column label="金额" width="80">
            <template #default="{ row }">¥{{ row.amount }}</template>
          </el-table-column>
          <el-table-column label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="statusType(row.status)" size="small" effect="light">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
        <div v-if="!orders.length" class="empty-tip">暂无订单</div>
      </section>

      <!-- 门店信息维护 -->
      <section class="block">
        <div class="section-title"><span class="bar"></span>维护门店/酒店信息</div>
        <div class="form-body">
          <div class="field-label">营业时间（门店）</div>
          <el-input v-model="form.businessHours" size="default" placeholder="如 11:00 - 次日 02:00" />
          <div class="field-label">简介 / 图文介绍（酒店）</div>
          <el-input v-model="form.intro" type="textarea" :rows="3" placeholder="填写酒店或门店的简介" />
          <div class="form-actions">
            <span class="form-tip">原型只开放这两个字段，且仅内存生效</span>
            <el-button type="primary" size="small" :loading="saving" @click="save">保存</el-button>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.head {
  padding: 14px 12px;
  background: linear-gradient(120deg, #52c41a, #95de64);
  color: #fff;
}
.head-name {
  font-size: 16px;
  font-weight: 700;
}
.head-sub {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
  font-size: 11.5px;
}
.head-id {
  opacity: 0.95;
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
  color: #52c41a;
}
.stat .label {
  font-size: 11px;
  color: var(--text-light);
  margin-top: 2px;
}
.block {
  background: #fff;
  margin: 0 10px 10px;
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
  overflow: hidden;
}
.section-title {
  padding: 12px 10px 6px;
}
.bar {
  width: 3px;
  height: 15px;
  border-radius: 2px;
  display: inline-block;
  background: #52c41a;
}
.target {
  display: flex;
  gap: 10px;
  padding: 10px;
  border-top: 1px solid #f2f3f5;
}
.target-info {
  flex: 1;
  min-width: 0;
}
.target-name {
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
}
.target-meta {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
  margin: 6px 0;
}
.target-sub {
  font-size: 11.5px;
  color: var(--text-light);
}
.form-body {
  padding: 4px 12px 14px;
}
.field-label {
  font-size: 12px;
  color: var(--text-sub);
  margin: 10px 0 6px;
}
.form-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
}
.form-tip {
  font-size: 11px;
  color: var(--text-light);
}
</style>
