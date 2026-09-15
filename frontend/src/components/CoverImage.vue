<script setup>
/**
 * 封面占位图组件（公共组件）
 * 原型不引入外部图片资源：用主色渐变 + 品类标签模拟门店/酒店封面，
 * 保证断网演示不出现图片加载失败。
 */
import { computed } from 'vue'

const props = defineProps({
  color: { type: String, default: '#ff6633' },
  tag: { type: String, default: '' },
  width: { type: String, default: '96px' },
  height: { type: String, default: '96px' },
  radius: { type: String, default: '8px' },
  fontSize: { type: String, default: '13px' }
})

const styleObj = computed(() => ({
  width: props.width,
  height: props.height,
  borderRadius: props.radius,
  background: `linear-gradient(135deg, ${props.color} 0%, ${props.color} 52%, rgba(255,255,255,0.55) 100%)`,
  fontSize: props.fontSize
}))
</script>

<template>
  <div class="cover" :style="styleObj">
    <span class="cover-text">{{ tag }}</span>
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
.cover::before {
  content: '';
  position: absolute;
  width: 70%;
  height: 70%;
  right: -18%;
  bottom: -22%;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.18);
}
.cover::after {
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
