/**
 * 骨架屏组件自测（P0 美化：加载态与真实卡片同形）
 */
import { describe, it, expect } from 'vitest'
import { mountView } from './helpers'
import CardSkeleton from '../src/components/CardSkeleton.vue'
import DetailSkeleton from '../src/components/DetailSkeleton.vue'
import StarRate from '../src/components/StarRate.vue'

describe('骨架屏组件', () => {
  it('CardSkeleton：按 count 渲染同形占位卡片，封面尺寸可配', async () => {
    const { wrapper } = await mountView(CardSkeleton, '/', { props: { count: 3, cover: '100px' } })
    expect(wrapper.findAll('.sk-card').length).toBe(3)
    expect(wrapper.findAll('.sk-cover').length).toBe(3)
    expect(wrapper.find('.sk-cover').attributes('style')).toContain('width: 100px')
    // 每个占位卡片内有 4 条文本占位线
    expect(wrapper.findAll('.sk-line').length).toBe(12)
  })

  it('CardSkeleton：默认渲染 5 张占位卡片', async () => {
    const { wrapper } = await mountView(CardSkeleton, '/')
    expect(wrapper.findAll('.sk-card').length).toBe(5)
  })

  it('DetailSkeleton：渲染头图 + 信息块 + 内容块，头图高度可配', async () => {
    const { wrapper } = await mountView(DetailSkeleton, '/', { props: { heroHeight: '200px' } })
    expect(wrapper.find('.sk-hero').attributes('style')).toContain('height: 200px')
    expect(wrapper.findAll('.sk-block').length).toBe(3)
    expect(wrapper.findAll('.sk-line').length).toBe(10)
  })

  it('StarRate：scoreSize 控制评分数字字号（数字大于星标形成层级）', async () => {
    const { wrapper } = await mountView(StarRate, '/', { props: { value: 4.8, size: 12, scoreSize: 15 } })
    expect(wrapper.find('.score').attributes('style')).toContain('font-size: 15px')
    expect(wrapper.text()).toContain('4.8')
  })
})
