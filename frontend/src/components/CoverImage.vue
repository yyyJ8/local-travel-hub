<script setup>
/**
 * 封面图组件（公共组件）
 * 两种渲染模式：
 *  1. 有 src（本地真实照片）→ 渲染 <img>，懒加载 + 淡入；
 *  2. 无 src 或加载失败 → 回退为「主色渐变 + 品类标签」占位图。
 * 回退机制保证断网、图片缺失时页面不破版（现场演示安全网）。
 */
import { computed, ref, watch } from 'vue'

const props = defineProps({
  src: { type: String, default: '' },
  color: { type: String, default: '#ff6633' },
  tag: { type: String, default: '' },
  width: { type: String, default: '96px' },
  height: { type: String, default: '96px' },
  radius: { type: String, default: '8px' },
  fontSize: { type: String, default: '13px' }
})

const failed = ref(false)
const loaded = ref(false)

// 切换图片地址时重置状态（同一组件被复用于不同门店/酒店）
watch(
  () => props.src,
  () => {
    failed.value = false
    loaded.value = false
  }
)

const hasImage = computed(() => !!props.src && !failed.value)

const styleObj = computed(() => ({
  width: props.width,
  height: props.height,
  borderRadius: props.radius,
  background: hasImage.value
    ? '#eef0f3'
    : `linear-gradient(135deg, ${props.color} 0%, ${props.color} 52%, rgba(255,255,255,0.55) 100%)`,
  fontSize: props.fontSize
}))
</script>

<template>
  <div class="cover" :class="{ 'is-fallback': !hasImage }" :style="styleObj">
    <img
      v-if="hasImage"
      class="cover-img"
      :class="{ 'is-loaded': loaded }"
      :src="src"
      :alt="tag || '封面图'"
      loading="lazy"
      decoding="async"
      @load="loaded = true"
      @error="failed = true"
    />
    <span v-else class="cover-text">{{ tag }}</span>
  </div>
</template>

<style scoped>
.cover {
  position: relative;
  flex: none;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  color: #fff;
  font-weight: 600;
  letter-spacing: 1px;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.25);
}
.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  opacity: 0;
  transition: opacity 0.35s ease;
}
.cover-img.is-loaded {
  opacity: 1;
}
/* 仅占位模式绘制装饰圆，避免压在照片上 */
.cover.is-fallback::before {
  content: '';
  position: absolute;
  width: 70%;
  height: 70%;
  right: -18%;
  bottom: -22%;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.18);
}
.cover.is-fallback::after {
  content: '';
  position: absolute;
  width: 40%;
  height: 40%;
  left: -10%;
  top: -12%;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.14);
}
.cover-text {
  position: relative;
  z-index: 1;
  padding: 0 4px;
  text-align: center;
  line-height: 1.25;
}
</style>
