<script setup>
/**
 * 管理后台（角色：admin）
 * 内容：平台概览 → 用户管理（停用/启用）→ 全平台订单
 * 数据来源：D1 概览 / D2 用户列表 / D3 账号状态 / D4 全平台订单
 */
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAdminOverview, getAdminUsers, setUserStatus, getAdminOrders } from '../api/admin'
import { useAuth } from '../composables/useAuth'
import NavBar from '../components/NavBar.vue'
import DetailSkeleton from '../components/DetailSkeleton.vue'
import { Refresh, User, OfficeBuilding, Setting, Promotion, Ticket } from '@element-plus/icons-vue'

const auth = useAuth()
const loading = ref(true)
const overview = ref(null)
const users = ref([])
const orders = ref([])

const ROLE_TEXT = { user: '普通用户', merchant: '商家', admin: '管理员' }
const ROLE_TYPE = { user: 'info', merchant: 'success', admin: 'danger' }

async function load() {
  loading.value = true
  try {
    const [o, u, od] = await Promise.all([getAdminOverview(), getAdminUsers(), getAdminOrders()])
    overview.value = o
    users.value = u.items || []
    orders.value = od.items || []
  } catch (e) {
    /* 错误提示由拦截器统一处理 */
  } finally {
    loading.value = false
  }
}

async function toggleStatus(row) {
  const next = row.status === '正常' ? '停用' : '正常'
  try {
    await ElMessageBox.confirm(
      `确认将账号「${row.username}」状态改为「${next}」吗？停用会立即失效该账号的所有登录会话。`,
      '账号状态变更',
      { confirmButtonText: '确认', cancelButtonText: '取消', type: 'warning' }
    )
  } catch (e) {
    return
  }
  await setUserStatus(row.id, next)
  ElMessage.success(`账号 ${row.username} 已${next === '停用' ? '停用' : '恢复'}（仅内存生效）`)
  load()
}

function isSelf(row) {
  return row.id === auth.user.value?.id
}

onMounted(load)
</script>

<template>
  <div>
    <NavBar title="管理后台">
      <template #right>
        <el-icon :size="17" style="cursor: pointer" @click="load"><Refresh /></el-icon>
      </template>
    </NavBar>

    <div class="head">
      <div class="head-name">{{ auth.displayName.value }}</div>
      <div class="head-sub">
        <el-tag size="small" type="danger" effect="light">{{ auth.roleText.value }}</el-tag>
        <span>平台级权限 · 全平台数据</span>
      </div>
    </div>

    <DetailSkeleton v-if="loading" hero-height="0px" />

    <template v-else>
      <!-- 平台概览 -->
      <div class="stats">
        <div class="stat">
          <el-icon :size="15" color="#ff6633"><OfficeBuilding /></el-icon>
          <div class="num">{{ overview?.shops ?? 0 }}</div>
          <div class="label">门店</div>
        </div>
        <div class="stat">
          <el-icon :size="15" color="#0086f6"><OfficeBuilding /></el-icon>
          <div class="num">{{ overview?.hotels ?? 0 }}</div>
          <div class="label">酒店</div>
        </div>
        <div class="stat">
          <el-icon :size="15" color="#722ed1"><User /></el-icon>
          <div class="num">{{ overview?.users ?? 0 }}</div>
          <div class="label">用户</div>
        </div>
        <div class="stat">
          <el-icon :size="15" color="#52c41a"><Ticket /></el-icon>
          <div class="num">{{ overview?.orders ?? 0 }}</div>
          <div class="label">订单</div>
        </div>
      </div>
      <div class="stats sub">
        <div class="stat">
          <div class="num">{{ overview?.pendingOrders ?? 0 }}</div>
          <div class="label">待使用订单</div>
        </div>
        <div class="stat">
          <div class="num">{{ overview?.cancelledOrders ?? 0 }}</div>
          <div class="label">已取消</div>
        </div>
        <div class="stat">
          <div class="num">¥{{ overview?.pendingAmount ?? 0 }}</div>
          <div class="label">待使用金额</div>
        </div>
        <div class="stat">
          <div class="num">{{ overview?.sessions ?? 0 }}</div>
          <div class="label">活跃会话</div>
        </div>
      </div>

      <!-- 用户管理 -->
      <section class="block">
        <div class="section-title">
          <span class="bar"></span>用户管理（{{ users.length }}）
          <span class="role-summary">
            普通用户 {{ overview?.usersByRole?.user ?? 0 }} / 商家 {{ overview?.usersByRole?.merchant ?? 0 }} /
            管理员 {{ overview?.usersByRole?.admin ?? 0 }}
          </span>
        </div>
        <el-table :data="users" size="small" style="width: 100%">
          <el-table-column prop="username" label="账号" width="110" />
          <el-table-column prop="nickname" label="昵称" min-width="110" show-overflow-tooltip />
          <el-table-column label="角色" width="90">
            <template #default="{ row }">
              <el-tag :type="ROLE_TYPE[row.role]" size="small" effect="light">{{ ROLE_TEXT[row.role] }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.status === '正常' ? 'success' : 'info'" size="small" effect="plain">
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="92">
            <template #default="{ row }">
              <el-button
                size="small"
                :type="row.status === '正常' ? 'danger' : 'primary'"
                plain
                :disabled="isSelf(row)"
                @click="toggleStatus(row)"
              >
                {{ row.status === '正常' ? '停用' : '启用' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </section>

      <!-- 全平台订单 -->
      <section class="block">
        <div class="section-title"><span class="bar"></span>全平台订单（{{ orders.length }}）</div>
        <el-table :data="orders" size="small" style="width: 100%">
          <el-table-column prop="orderNo" label="订单号" width="150" />
          <el-table-column prop="targetName" label="门店/酒店" min-width="150" show-overflow-tooltip />
          <el-table-column prop="userId" label="归属用户" width="90" />
          <el-table-column label="金额" width="80">
            <template #default="{ row }">¥{{ row.amount }}</template>
          </el-table-column>
          <el-table-column label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.status === '待使用' ? 'warning' : 'info'" size="small" effect="light">
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </section>

      <el-alert
        type="info"
        :closable="false"
        style="margin: 0 10px 16px"
        title="原型说明：管理员操作（停用/启用）只作用于内存用户表，后端重启后恢复；无审计日志、无按钮级细粒度授权。"
      />
    </template>
  </div>
</template>

<style scoped>
.head {
  padding: 14px 12px;
  background: linear-gradient(120deg, #722ed1, #9254de);
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
.stats {
  display: flex;
  background: #fff;
  padding: 12px 0;
}
.stats.sub {
  margin-bottom: 8px;
  border-top: 1px dashed var(--border-color);
}
.stat {
  flex: 1;
  text-align: center;
}
.stat .num {
  font-size: 16px;
  font-weight: 700;
  color: #722ed1;
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
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
}
.bar {
  width: 3px;
  height: 15px;
  border-radius: 2px;
  display: inline-block;
  background: #722ed1;
}
.role-summary {
  width: 100%;
  font-size: 11px;
  font-weight: 400;
  color: var(--text-light);
  margin-top: 2px;
}
</style>
