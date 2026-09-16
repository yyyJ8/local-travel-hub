<script setup>
/**
 * 登录 / 注册页
 * - 登录：三个预置演示账号一键填入（普通用户 / 商家 / 管理员），便于答辩现场演示
 * - 注册：仅开放普通用户角色；注册成功后直接进入登录态
 * - 支持 ?redirect= 参数：登录后回到原目标页面（比如下单前的个人中心）
 */
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuth } from '../composables/useAuth'
import NavBar from '../components/NavBar.vue'
import { User, Lock, Iphone, ShoppingBag, OfficeBuilding, Setting } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const auth = useAuth()

const tab = ref('login')
const loading = ref(false)

const loginForm = ref({ username: '', password: '' })
const regForm = ref({ username: '', password: '', nickname: '', phone: '' })

const DEMO_ACCOUNTS = [
  { username: 'demo', password: '123456', label: '普通用户', desc: '下单 / 我的订单', icon: User, color: '#ff6633' },
  { username: 'shangjia', password: '123456', label: '商家', desc: '只看自己门店订单', icon: OfficeBuilding, color: '#52c41a' },
  { username: 'admin', password: '123456', label: '管理员', desc: '全平台数据 / 停用账号', icon: Setting, color: '#722ed1' }
]

const redirect = computed(() => String(route.query.redirect || '/'))

function fill(account) {
  tab.value = 'login'
  loginForm.value = { username: account.username, password: account.password }
  ElMessage.success(`已填入${account.label}演示账号，点击登录即可`)
}

async function doLogin() {
  if (!loginForm.value.username.trim() || !loginForm.value.password) {
    ElMessage.warning('请填写用户名与密码')
    return
  }
  loading.value = true
  try {
    const user = await auth.login(loginForm.value.username.trim(), loginForm.value.password)
    ElMessage.success(`欢迎回来，${user.nickname || user.username}`)
    router.replace(redirect.value)
  } catch (e) {
    /* 错误提示已由 Axios 拦截器统一弹出 */
  } finally {
    loading.value = false
  }
}

async function doRegister() {
  if (!regForm.value.username.trim()) {
    ElMessage.warning('请填写用户名')
    return
  }
  if ((regForm.value.password || '').length < 6) {
    ElMessage.warning('密码至少 6 位')
    return
  }
  loading.value = true
  try {
    const user = await auth.register({
      username: regForm.value.username.trim(),
      password: regForm.value.password,
      nickname: regForm.value.nickname.trim(),
      phone: regForm.value.phone.trim()
    })
    ElMessage.success(`注册成功，已自动登录：${user.nickname || user.username}`)
    router.replace(redirect.value)
  } catch (e) {
    /* 同上 */
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // 从"下单被拦截"跳过来时，默认展示登录表单
  tab.value = 'login'
})
</script>

<template>
  <div>
    <NavBar title="登录 / 注册" show-back />

    <div class="brand">
      <div class="logo">本地生活 · 旅行</div>
      <div class="slogan">仿大众点评 + 携程 演示原型系统</div>
    </div>

    <el-tabs v-model="tab" class="tabs">
      <el-tab-pane label="登录" name="login">
        <el-form label-position="top">
          <el-form-item label="用户名">
            <el-input v-model="loginForm.username" placeholder="请输入用户名" :prefix-icon="User" size="large" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              :prefix-icon="Lock"
              size="large"
              show-password
              @keyup.enter="doLogin"
            />
          </el-form-item>
          <el-button type="primary" size="large" class="submit" :loading="loading" @click="doLogin">
            登录
          </el-button>
        </el-form>

        <div class="demo-title">演示账号一键填入（口令均为 123456）</div>
        <div class="demo-list">
          <div v-for="a in DEMO_ACCOUNTS" :key="a.username" class="demo-item" @click="fill(a)">
            <div class="demo-icon" :style="{ background: a.color }">
              <el-icon :size="16" color="#fff"><component :is="a.icon" /></el-icon>
            </div>
            <div class="demo-info">
              <div class="demo-label">{{ a.label }}<span class="demo-user">{{ a.username }}</span></div>
              <div class="demo-desc">{{ a.desc }}</div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="注册" name="register">
        <el-form label-position="top">
          <el-form-item label="用户名（3~20 位）">
            <el-input v-model="regForm.username" placeholder="如 zhangsan" :prefix-icon="User" size="large" />
          </el-form-item>
          <el-form-item label="密码（至少 6 位）">
            <el-input v-model="regForm.password" type="password" placeholder="请输入密码" :prefix-icon="Lock" size="large" show-password />
          </el-form-item>
          <el-form-item label="昵称（可空）">
            <el-input v-model="regForm.nickname" placeholder="留空则与用户名相同" size="large" />
          </el-form-item>
          <el-form-item label="手机号（可空，11 位）">
            <el-input v-model="regForm.phone" placeholder="13800000000" :prefix-icon="Iphone" size="large" />
          </el-form-item>
          <el-button type="primary" size="large" class="submit" :loading="loading" @click="doRegister">
            注册并登录
          </el-button>
        </el-form>
        <el-alert
          type="info"
          :closable="false"
          style="margin-top: 12px"
          title="原型说明：注册只开放普通用户角色；商家与管理员请使用上方演示账号。账号存于后端内存，服务重启后自注册账号会丢失。"
        />
      </el-tab-pane>
    </el-tabs>

    <div class="tip">
      <el-icon :size="13"><ShoppingBag /></el-icon>
      浏览门店与酒店无需登录，下单与个人中心需要登录
    </div>
  </div>
</template>

<style scoped>
.brand {
  padding: 22px 16px 10px;
  background: linear-gradient(135deg, #ff6633 0%, #ff8a3c 48%, #ffa940 100%);
  color: #fff;
}
.logo {
  font-size: 21px;
  font-weight: 700;
}
.slogan {
  font-size: 12px;
  opacity: 0.92;
  margin-top: 5px;
}
.tabs {
  padding: 0 16px;
  --el-color-primary: var(--dp-orange);
}
.submit {
  width: 100%;
  margin-top: 4px;
}
.demo-title {
  font-size: 12px;
  color: var(--text-light);
  margin: 18px 0 8px;
}
.demo-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.demo-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 10px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}
.demo-item:active {
  background: #fafafa;
  border-color: var(--dp-orange);
}
.demo-icon {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex: none;
}
.demo-label {
  font-size: 13.5px;
  font-weight: 600;
}
.demo-user {
  margin-left: 6px;
  font-size: 11.5px;
  color: var(--text-light);
  font-weight: 400;
}
.demo-desc {
  font-size: 11.5px;
  color: var(--text-light);
  margin-top: 2px;
}
.tip {
  display: flex;
  align-items: center;
  gap: 4px;
  justify-content: center;
  font-size: 11.5px;
  color: var(--text-light);
  padding: 16px 0 20px;
}
</style>
