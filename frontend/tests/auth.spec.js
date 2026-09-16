/**
 * 登录相关内容自测：会话存储 / 登录态 / 登录页 / 角色导航 / 路由守卫
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mountView, flush } from './helpers'
import { writeSession, readSession, getToken, clearSession } from '../src/utils/session'

vi.mock('../src/api/auth', () => ({
  login: vi.fn(),
  register: vi.fn(),
  logout: vi.fn(),
  fetchMe: vi.fn()
}))

import { login as apiLogin, logout as apiLogout, register as apiRegister } from '../src/api/auth'
import { useAuth } from '../src/composables/useAuth'
import Login from '../src/views/Login.vue'
import TabBar from '../src/components/TabBar.vue'
import router from '../src/router'

const USER = {
  id: 'U001', username: 'demo', role: 'user', nickname: '张三',
  phone: '13800001111', avatarColor: '#ff6633', status: '正常', merchantId: ''
}

beforeEach(() => {
  vi.clearAllMocks()
  clearSession()
  const auth = useAuth()
  auth.state.token = ''
  auth.state.user = null
})

describe('会话存储（localStorage）', () => {
  it('写入后可读回令牌与用户，清空后为空', () => {
    writeSession('token-abc', USER)
    expect(getToken()).toBe('token-abc')
    expect(readSession().user.username).toBe('demo')
    clearSession()
    expect(getToken()).toBe('')
    expect(readSession().user).toBeNull()
  })

  it('本地数据损坏时不抛错，返回空会话', () => {
    localStorage.setItem('ctrip-prototype-session', '{不是合法JSON')
    // 清掉模块内缓存，强制重新读取
    vi.resetModules()
    expect(() => readSession()).not.toThrow()
  })
})

describe('登录态（useAuth）', () => {
  it('登录成功写入状态并持久化', async () => {
    apiLogin.mockResolvedValue({ token: 't-1', user: USER })
    const auth = useAuth()
    const user = await auth.login('demo', '123456')
    expect(apiLogin).toHaveBeenCalledWith('demo', '123456')
    expect(user.nickname).toBe('张三')
    expect(auth.isLoggedIn.value).toBe(true)
    expect(auth.roleText.value).toBe('普通用户')
    expect(getToken()).toBe('t-1')
  })

  it('注册成功后直接进入登录态', async () => {
    apiRegister.mockResolvedValue({ token: 't-2', user: { ...USER, username: 'newbie', nickname: '新用户' } })
    const auth = useAuth()
    await auth.register({ username: 'newbie', password: 'abc123456' })
    expect(auth.isLoggedIn.value).toBe(true)
    expect(auth.displayName.value).toBe('新用户')
  })

  it('退出登录清空状态与本地会话', async () => {
    apiLogin.mockResolvedValue({ token: 't-3', user: USER })
    apiLogout.mockResolvedValue({ message: 'ok' })
    const auth = useAuth()
    await auth.login('demo', '123456')
    await auth.logout()
    expect(auth.isLoggedIn.value).toBe(false)
    expect(getToken()).toBe('')
  })

  it('商家与管理员角色判断正确', async () => {
    const auth = useAuth()
    auth.state.token = 't'
    auth.state.user = { ...USER, role: 'merchant', merchantId: 'M001' }
    expect(auth.isMerchant.value).toBe(true)
    expect(auth.isAdmin.value).toBe(false)
    auth.state.user = { ...USER, role: 'admin' }
    expect(auth.isAdmin.value).toBe(true)
    expect(auth.roleText.value).toBe('管理员')
  })
})

describe('登录页', () => {
  it('渲染登录/注册两个页签与三种演示账号入口', async () => {
    const { wrapper } = await mountView(Login, '/login')
    await flush()
    const text = wrapper.text()
    expect(text).toContain('登录')
    expect(text).toContain('注册')
    expect(text).toContain('普通用户')
    expect(text).toContain('商家')
    expect(text).toContain('管理员')
    expect(wrapper.findAll('.demo-item').length).toBe(3)
  })

  it('点击演示账号可一键填入用户名与口令', async () => {
    const { wrapper } = await mountView(Login, '/login')
    await flush()
    const items = wrapper.findAll('.demo-item')
    await items[1].trigger('click') // 商家
    const inputs = wrapper.findAll('input')
    expect(inputs[0].element.value).toBe('shangjia')
    expect(inputs[1].element.value).toBe('123456')
  })
})

describe('角色导航（TabBar）', () => {
  it('普通用户：4 个 Tab，无后台入口', async () => {
    const { wrapper } = await mountView(TabBar, '/')
    const text = wrapper.text()
    expect(wrapper.findAll('.tab').length).toBe(4)
    expect(text).not.toContain('商家后台')
    expect(text).not.toContain('管理后台')
    expect(text).toContain('我的')
  })

  it('商家：多一个「商家后台」Tab', async () => {
    const auth = useAuth()
    auth.state.token = 't'
    auth.state.user = { ...USER, role: 'merchant', merchantId: 'M001' }
    const { wrapper } = await mountView(TabBar, '/')
    const text = wrapper.text()
    expect(text).toContain('商家后台')
    expect(text).not.toContain('管理后台')
    expect(wrapper.findAll('.tab').length).toBe(5)
  })

  it('管理员：多一个「管理后台」Tab', async () => {
    const auth = useAuth()
    auth.state.token = 't'
    auth.state.user = { ...USER, role: 'admin' }
    const { wrapper } = await mountView(TabBar, '/')
    expect(wrapper.text()).toContain('管理后台')
    expect(wrapper.findAll('.tab').length).toBe(5)
  })
})

describe('路由守卫', () => {
  it('未登录访问个人中心 → 跳登录页并带上 redirect', async () => {
    clearSession()
    await router.push('/profile')
    await router.isReady()
    expect(router.currentRoute.value.path).toBe('/login')
    expect(String(router.currentRoute.value.query.redirect)).toBe('/profile')
  })

  it('普通用户访问管理后台 → 被拒绝并回首页', async () => {
    writeSession('t-user', USER)
    await router.push('/admin')
    expect(router.currentRoute.value.path).toBe('/')
  })

  it('管理员访问管理后台 → 放行', async () => {
    writeSession('t-admin', { ...USER, role: 'admin', username: 'admin' })
    await router.push('/admin')
    expect(router.currentRoute.value.path).toBe('/admin')
  })

  it('已登录访问登录页 → 回首页（不再重复登录）', async () => {
    writeSession('t-user2', USER)
    await router.push('/login')
    expect(router.currentRoute.value.path).toBe('/')
  })

  it('浏览类页面免登录', async () => {
    clearSession()
    await router.push('/shops')
    expect(router.currentRoute.value.path).toBe('/shops')
  })
})
