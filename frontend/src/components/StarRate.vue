<script setup>
/**
 * 星级评分组件（公共组件）
 * 门店列表、酒店列表、门店评论、酒店评价四处复用。
 * scoreSize：评分数字字号（默认为星标 +2px，形成「数字大、星标小」的视觉层级）。
 */
import { computed } from 'vue'
import { StarFilled } from '@element-plus/icons-vue'

const props = defineProps({
  value: { type: Number, default: 0 },
  size: { type: Number, default: 13 },
  scoreSize: { type: Number, default: 0 },
  showValue: { type: Boolean, default: true },
  color: { type: String, default: '#ff9500' }
})

const fullStars = computed(() => Math.max(0, Math.min(5, Math.round(props.value))))
const scoreText = computed(() => Number(props.value || 0).toFixed(1))
const scoreStyle = computed(() => ({
  color: props.color,
  fontSize: `${props.scoreSize || props.size + 2}px`
}))
</script>

<template>
  <span class="star-rate">
    <el-icon v-for="i in 5" :key="i" :size="size" :color="i <= fullStars ? color : '#dcdfe6'">
      <StarFilled />
    </el-icon>
    <span v-if="showValue" class="score" :style="scoreStyle">{{ scoreText }}</span>
  </span>
</template>

<style scoped>
.star-rate {
  display: inline-flex;
  align-items: center;
  gap: 1px;
  vertical-align: middle;
}
.score {
  margin-left: 4px;
  font-weight: 700;
  line-height: 1;
}
</style>
