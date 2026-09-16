<script setup>
/**
 * 列表骨架屏（公共组件）
 * 与 ShopCard / HotelCard 同形的占位卡片，用于列表页加载态，避免通用行骨架造成的版式跳动。
 */
defineProps({
  count: { type: Number, default: 5 },
  cover: { type: String, default: '92px' }
})
</script>

<template>
  <div class="sk-list">
    <div v-for="i in count" :key="i" class="sk-card">
      <div class="sk sk-cover" :style="{ width: cover, height: cover }"></div>
      <div class="sk-info">
        <div class="sk sk-line" style="width: 68%"></div>
        <div class="sk sk-line" style="width: 36%"></div>
        <div class="sk sk-line" style="width: 86%"></div>
        <div class="sk sk-line" style="width: 48%"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sk-card {
  display: flex;
  gap: 10px;
  padding: 12px 10px;
  background: #fff;
  border-bottom: 1px solid #f2f3f5;
}
.sk-cover {
  flex: none;
  border-radius: 8px;
}
.sk-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 9px;
}
.sk-line {
  height: 12px;
}
</style>
