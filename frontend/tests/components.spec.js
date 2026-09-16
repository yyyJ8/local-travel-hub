/**
 * 公共组件渲染自测（阶段4 验收：组件可复用且渲染正确）
 */
import { describe, it, expect } from 'vitest'
import { mountView } from './helpers'
import StarRate from '../src/components/StarRate.vue'
import CoverImage from '../src/components/CoverImage.vue'
import ShopCard from '../src/components/ShopCard.vue'
import HotelCard from '../src/components/HotelCard.vue'
import { shopFixture, hotelFixture } from './fixtures'

describe('公共组件渲染', () => {
  it('StarRate：渲染 5 个星标与评分文本', async () => {
    const { wrapper } = await mountView(StarRate, '/', { props: { value: 4.8 } })
    expect(wrapper.findAll('.el-icon').length).toBe(5)
    expect(wrapper.text()).toContain('4.8')
  })

  it('CoverImage：无 src 时回退为渐变色块占位图', async () => {
    const { wrapper } = await mountView(CoverImage, '/', { props: { color: '#ff6633', tag: '火锅' } })
    expect(wrapper.text()).toContain('火锅')
    expect(wrapper.find('.cover').attributes('style')).toContain('#ff6633')
    expect(wrapper.find('.cover-img').exists()).toBe(false)
    expect(wrapper.classes()).toContain('is-fallback')
  })

  it('CoverImage：有 src 时渲染懒加载图片', async () => {
    const { wrapper } = await mountView(CoverImage, '/', {
      props: { src: '/images/shops/S001.jpg', tag: '火锅' }
    })
    const img = wrapper.find('.cover-img')
    expect(img.exists()).toBe(true)
    expect(img.attributes('src')).toBe('/images/shops/S001.jpg')
    expect(img.attributes('loading')).toBe('lazy')
  })

  it('CoverImage：图片加载失败时回退为占位图（断网/缺图不破版）', async () => {
    const { wrapper } = await mountView(CoverImage, '/', {
      props: { src: '/images/shops/not-exist.jpg', color: '#ff6633', tag: '火锅' }
    })
    expect(wrapper.find('.cover-img').exists()).toBe(true)
    await wrapper.find('.cover-img').trigger('error') // 模拟图片加载失败
    expect(wrapper.find('.cover-img').exists()).toBe(false)
    expect(wrapper.text()).toContain('火锅')
  })

  it('ShopCard：传入 rank 时渲染榜单名次角标', async () => {
    const { wrapper } = await mountView(ShopCard, '/', { props: { shop: shopFixture, rank: 1 } })
    const badge = wrapper.find('.rank-no')
    expect(badge.exists()).toBe(true)
    expect(badge.text()).toBe('1')
    expect(badge.classes()).toContain('r1')
  })

  it('ShopCard：不传 rank 时不渲染角标（列表页复用同一组件）', async () => {
    const { wrapper } = await mountView(ShopCard, '/', { props: { shop: shopFixture } })
    expect(wrapper.find('.rank-no').exists()).toBe(false)
  })

  it('ShopCard：渲染门店名称、评分、人均、品类标签、团购数量与封面图', async () => {
    const { wrapper } = await mountView(ShopCard, '/', { props: { shop: shopFixture } })
    const text = wrapper.text()
    expect(text).toContain('蜀大侠火锅（春熙路店）')
    expect(text).toContain('4.8')
    expect(text).toContain('8642 条')
    expect(text).toContain('¥128')
    expect(text).toContain('火锅')
    expect(text).toContain('4 个团购')
    expect(wrapper.find('.cover-img').attributes('src')).toBe('/images/shops/S001.jpg')
  })

  it('HotelCard：渲染酒店名称、星级、设施、房价与晚数总价', async () => {
    const { wrapper } = await mountView(HotelCard, '/', {
      props: { hotel: hotelFixture, nights: 2 }
    })
    const text = wrapper.text()
    expect(text).toContain('成都太古里博舍酒店')
    expect(text).toContain('★★★★★')
    expect(text).toContain('5 星级')
    expect(text).toContain('室内泳池')
    expect(text).toContain('¥1280')
    expect(text).toContain('2 晚约 ¥2560')
  })
})
