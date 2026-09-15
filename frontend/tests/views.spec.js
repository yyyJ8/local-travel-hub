/**
 * 页面渲染自测（阶段5~8 验收）
 * 通过 mock 各 api 模块，验证页面在拿到数据后能真实渲染出业务内容（而非白屏）。
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mountView, flush } from './helpers'
import { homeFixture, shopFixture, hotelFixture, shopDetailFixture, hotelDetailFixture, ordersFixture } from './fixtures'

vi.mock('../src/api/home', () => ({ getHomeRecommend: vi.fn() }))
vi.mock('../src/api/shop', () => ({ getShops: vi.fn(), getShopDetail: vi.fn() }))
vi.mock('../src/api/hotel', () => ({ getHotels: vi.fn(), getHotelDetail: vi.fn(), getFacilities: vi.fn() }))
vi.mock('../src/api/order', () => ({ getOrders: vi.fn(), getOrderDetail: vi.fn(), cancelOrder: vi.fn(), createOrder: vi.fn() }))

import { getHomeRecommend } from '../src/api/home'
import { getShops, getShopDetail } from '../src/api/shop'
import { getHotels, getHotelDetail, getFacilities } from '../src/api/hotel'
import { getOrders } from '../src/api/order'

import Home from '../src/views/Home.vue'
import ShopList from '../src/views/ShopList.vue'
import ShopDetail from '../src/views/ShopDetail.vue'
import HotelList from '../src/views/HotelList.vue'
import HotelDetail from '../src/views/HotelDetail.vue'
import Profile from '../src/views/Profile.vue'

beforeEach(() => {
  vi.clearAllMocks()
  document.body.innerHTML = ''
})

describe('阶段5 首页模块', () => {
  it('渲染轮播、分类入口、推荐门店与推荐酒店', async () => {
    getHomeRecommend.mockResolvedValue(homeFixture)
    const { wrapper } = await mountView(Home, '/')
    await flush()
    const text = wrapper.text()
    expect(text).toContain('春日美食节')
    expect(text).toContain('精选火锅 · 5 折起')
    expect(text).toContain('美食')
    expect(text).toContain('休闲娱乐')
    expect(text).toContain('推荐美食门店')
    expect(text).toContain('推荐酒店')
    expect(text).toContain('蜀大侠火锅（春熙路店）')
    expect(text).toContain('成都太古里博舍酒店')
    expect(text).not.toContain('加载失败')
  })

  it('后端不可用时不白屏，给出错误提示与重新加载按钮', async () => {
    getHomeRecommend.mockRejectedValue(new Error('boom'))
    const { wrapper } = await mountView(Home, '/')
    await flush()
    expect(wrapper.text()).toContain('首页数据加载失败')
    expect(wrapper.text()).toContain('重新加载')
  })
})

describe('阶段6 本地生活模块', () => {
  it('门店列表：按路由品类参数查询并渲染列表与结果统计', async () => {
    getShops.mockResolvedValue({ total: 1, items: [shopFixture] })
    const { wrapper } = await mountView(ShopList, '/shops?category=美食')
    await flush()
    expect(getShops).toHaveBeenCalled()
    expect(getShops.mock.calls[0][0].category).toBe('美食')
    const text = wrapper.text()
    expect(text).toContain('符合条件的门店共')
    expect(text).toContain('蜀大侠火锅（春熙路店）')
    expect(text).toContain('人气优先')
    // 排序 / 评分 / 人均 三个筛选下拉框均已渲染（选项文本在弹层中，不参与本次断言）
    expect(wrapper.findAll('.el-select').length).toBe(3)
  })

  it('门店列表：空结果给出提示文案', async () => {
    getShops.mockResolvedValue({ total: 0, items: [] })
    const { wrapper } = await mountView(ShopList, '/shops')
    await flush()
    expect(wrapper.text()).toContain('没有符合条件的门店')
  })

  it('门店详情：渲染营业时间、地址、团购套餐与用户评论', async () => {
    getShopDetail.mockResolvedValue(shopDetailFixture)
    const { wrapper } = await mountView(ShopDetail, '/shops/S001')
    await flush()
    const text = wrapper.text()
    expect(text).toContain('蜀大侠火锅（春熙路店）')
    expect(text).toContain('营业时间：11:00 - 次日 02:00')
    expect(text).toContain('成都市锦江区春熙路东段 18 号 3 层')
    expect(text).toContain('团购套餐（2）')
    expect(text).toContain('双人套餐·麻辣牛肉')
    expect(text).toContain('¥236')
    expect(text).toContain('用户评论（1）')
    expect(text).toContain('麻辣牛肉真的很惊艳')
    expect(text).toContain('立即预约')
  })
})

describe('阶段7 旅行住宿模块', () => {
  it('酒店列表：渲染日历、晚数联动、筛选与排序控件', async () => {
    getHotels.mockResolvedValue({ total: 1, nights: 2, items: [hotelFixture] })
    getFacilities.mockResolvedValue(['室内泳池', '健身房'])
    const { wrapper } = await mountView(HotelList, '/hotels')
    await flush()
    const text = wrapper.text()
    expect(text).toContain('成都 · 符合条件酒店')
    expect(text).toContain('共')
    expect(text).toContain('2')
    expect(text).toContain('晚')
    expect(text).toContain('成都太古里博舍酒店')
    expect(text).toContain('室内泳池')
    expect(text).toContain('好评优先')
    expect(wrapper.find('.el-date-editor').exists()).toBe(true)
  })

  it('酒店详情：渲染图文、房型房价、晚数总价与酒店评价', async () => {
    getHotelDetail.mockResolvedValue(hotelDetailFixture)
    const { wrapper } = await mountView(HotelDetail, '/hotels/H001?nights=2')
    await flush()
    const text = wrapper.text()
    expect(text).toContain('成都太古里博舍酒店')
    expect(text).toContain('★')
    expect(text).toContain('位于太古里核心区')
    expect(text).toContain('房型与房价（1）')
    expect(text).toContain('高级大床房')
    expect(text).toContain('28㎡')
    expect(text).toContain('2 晚共 ¥2560')
    expect(text).toContain('位置非常方便')
    expect(text).toContain('立即预订')
  })
})

describe('阶段8 个人中心', () => {
  it('订单列表：渲染订单号、状态、金额，且仅「待使用」订单显示取消按钮', async () => {
    getOrders.mockResolvedValue(ordersFixture)
    const { wrapper } = await mountView(Profile, '/profile')
    await flush()
    const text = wrapper.text()
    expect(text).toContain('ORD202609091001')
    expect(text).toContain('ORD202609111002')
    expect(text).toContain('ORD202608311003')
    expect(text).toContain('待使用')
    expect(text).toContain('已取消')
    expect(text).toContain('¥474')
    expect(text).toContain('¥2560')
    expect(text).toContain('演示用户')
    // 3 条订单中 2 条待使用 → 2 个「模拟取消预约」按钮
    const danger = wrapper.findAll('.el-button--danger')
    expect(danger.length).toBe(2)
    expect(danger[0].text()).toContain('模拟取消预约')
  })
})
