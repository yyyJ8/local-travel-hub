<script setup>
/**
 * 星级评分组件（公共组件）
 * 门店列表、酒店列表、门店评论、酒店评价四处复用。
 */
import { computed } from 'vue'
import { StarFilled } from '@element-plus/icons-vue'

const props = defineProps({
  value: { type: Number, default: 0 },
  size: { type: Number, default: 13 },
  showValue: { type: Boolean, default: true },
  color: { type: String, default: '#ff9500' }
})

const fullStars = computed(() => Math.max(0, Math.min(5, Math.round(props.value))))
const scoreText = computed(() => Number(props.value || 0).toFixed(1))
</script>

<template>
  <span class="star-rate">
    <el-icon v-for="i in 5" :key="i" :size="size" :color="i <= fullStars ? color : '#dcdfe6'">
      <StarFilled />
    </el-icon>
    <span v-if="showValue" class="score" :style="{ color }">{{ scoreText }}</span>
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
  font-size: 13px;
  font-weight: 700;
}
</style>
