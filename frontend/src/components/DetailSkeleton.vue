<script setup>
/**
 * 详情页骨架屏（公共组件）
 * 版式与门店/酒店/订单详情一致：头图 + 信息块 + 内容块。
 */
defineProps({
  heroHeight: { type: String, default: '180px' }
})
</script>

<template>
  <div class="sk-detail">
    <div class="sk sk-hero" :style="{ height: heroHeight }"></div>

    <div class="sk-block">
      <div class="sk sk-line" style="width: 62%"></div>
      <div class="sk sk-line" style="width: 40%"></div>
      <div class="sk sk-line" style="width: 84%"></div>
      <div class="sk sk-line" style="width: 55%"></div>
    </div>

    <div class="sk-block">
      <div class="sk sk-line sk-title" style="width: 32%"></div>
      <div class="sk sk-line" style="width: 92%"></div>
      <div class="sk sk-line" style="width: 74%"></div>
    </div>

    <div class="sk-block">
      <div class="sk sk-line sk-title" style="width: 28%"></div>
      <div class="sk sk-line" style="width: 88%"></div>
      <div class="sk sk-line" style="width: 66%"></div>
    </div>
  </div>
</template>

<style scoped>
.sk-hero {
  border-radius: 0;
}
.sk-block {
  background: #fff;
  margin: 10px;
  padding: 14px 12px;
  border-radius: var(--card-radius);
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.sk-line {
  height: 12px;
}
.sk-title {
  height: 15px;
}
</style>
