/**
 * 预约下单弹窗自测（阶段8 验收：表单校验 → 提交 → 成功反馈）
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ElementPlus from 'element-plus'
import OrderDialog from '../src/components/OrderDialog.vue'

vi.mock('../src/api/order', () => ({ createOrder: vi.fn() }))
import { createOrder } from '../src/api/order'

const shopItem = { id: 'S001-P01', name: '双人套餐·麻辣牛肉', price: 236 }
const roomItem = { id: 'H001-R01', name: '高级大床房', price: 1280 }

/** 兼容两种方式读取 <script setup> 的响应式状态 */
function state(wrapper) {
  return wrapper.vm.form ? wrapper.vm : wrapper.vm.$.setupState
}

function clickByText(text) {
  const btn = [...document.body.querySelectorAll('button')].find((b) => b.textContent.includes(text))
  if (!btn) throw new Error(`未找到按钮：${text}`)
  btn.click()
}

function mountDialog(props) {
  return mount(OrderDialog, {
    props: { modelValue: true, ...props },
    global: { plugins: [ElementPlus] },
    attachTo: document.body
  })
}

beforeEach(() => {
  vi.clearAllMocks()
  document.body.innerHTML = ''
})

describe('预约下单弹窗', () => {
  it('门店套餐：渲染项目与合计金额，提交后调用 I7 接口并给出成功反馈', async () => {
    createOrder.mockResolvedValue({
      orderNo: 'ORD202609152001', type: 'shop', targetName: '蜀大侠火锅（春熙路店）',
      itemName: shopItem.name, bookTime: '2026-10-20', checkOut: '', nights: 0,
      count: 1, amount: 236, status: '待使用'
    })
    const wrapper = mountDialog({ type: 'shop', targetId: 'S001', targetName: '蜀大侠火锅（春熙路店）', item: shopItem })
    await wrapper.vm.$nextTick()

    expect(document.body.textContent).toContain('预约下单')
    expect(document.body.textContent).toContain('双人套餐·麻辣牛肉')
    expect(document.body.textContent).toContain('合计 ¥236')

    // 填写表单
    const s = state(wrapper)
    s.form.name = '测试用户'
    s.form.phone = '13800001111'
    s.form.bookTime = '2026-10-20'
    await wrapper.vm.$nextTick()

    clickByText('提交预约')
    await wrapper.vm.$nextTick()
    await new Promise((r) => setTimeout(r, 0))

    expect(createOrder).toHaveBeenCalledTimes(1)
    const payload = createOrder.mock.calls[0][0]
    expect(payload.type).toBe('shop')
    expect(payload.targetId).toBe('S001')
    expect(payload.itemId).toBe('S001-P01')
    expect(payload.name).toBe('测试用户')
    expect(payload.phone).toBe('13800001111')
    expect(payload.count).toBe(1)

    expect(document.body.textContent).toContain('预约提交成功')
    expect(document.body.textContent).toContain('ORD202609152001')
  })

  it('必填校验：姓名为空时不调用下单接口', async () => {
    const wrapper = mountDialog({ type: 'shop', targetId: 'S001', targetName: '门店', item: shopItem })
    await wrapper.vm.$nextTick()

    const s = state(wrapper)
    s.form.name = ''
    await wrapper.vm.$nextTick()

    clickByText('提交预约')
    await wrapper.vm.$nextTick()
    await new Promise((r) => setTimeout(r, 0))

    expect(createOrder).not.toHaveBeenCalled()
  })

  it('手机号格式错误时不调用下单接口', async () => {
    const wrapper = mountDialog({ type: 'shop', targetId: 'S001', targetName: '门店', item: shopItem })
    await wrapper.vm.$nextTick()

    const s = state(wrapper)
    s.form.name = '测试用户'
    s.form.phone = '123'
    await wrapper.vm.$nextTick()

    clickByText('提交预约')
    await wrapper.vm.$nextTick()
    await new Promise((r) => setTimeout(r, 0))

    expect(createOrder).not.toHaveBeenCalled()
  })

  it('酒店房型：按晚数计算合计金额（房价 × 间数 × 晚数）', async () => {
    createOrder.mockResolvedValue({
      orderNo: 'ORD202609152002', type: 'hotel', targetName: '成都太古里博舍酒店',
      itemName: roomItem.name, bookTime: '2026-10-20', checkOut: '2026-10-22',
      nights: 2, count: 1, amount: 2560, status: '待使用'
    })
    const wrapper = mountDialog({
      type: 'hotel', targetId: 'H001', targetName: '成都太古里博舍酒店', item: roomItem,
      defaultBookTime: '2026-10-20', defaultCheckOut: '2026-10-22'
    })
    await wrapper.vm.$nextTick()

    const text = document.body.textContent
    expect(text).toContain('入住日期')
    expect(text).toContain('退房日期')
    expect(text).toContain('合计 ¥2560') // 1280 × 1 间 × 2 晚

    const s = state(wrapper)
    s.form.name = '测试用户'
    s.form.phone = '13800001111'
    await wrapper.vm.$nextTick()

    clickByText('提交预约')
    await wrapper.vm.$nextTick()
    await new Promise((r) => setTimeout(r, 0))

    const payload = createOrder.mock.calls[0][0]
    expect(payload.type).toBe('hotel')
    expect(payload.checkOut).toBe('2026-10-22')
    expect(document.body.textContent).toContain('预约提交成功')
  })
})
