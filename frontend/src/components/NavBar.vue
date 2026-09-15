<script setup>
/**
 * 顶部导航栏（公共组件）
 * 支持：标题、返回按钮、搜索框（首页使用）、右侧插槽。
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Search } from '@element-plus/icons-vue'

const props = defineProps({
  title: { type: String, default: '' },
  showBack: { type: Boolean, default: false },
  showSearch: { type: Boolean, default: false },
  keyword: { type: String, default: '' },
  bg: { type: String, default: '#ffffff' },
  color: { type: String, default: '' }
})

const emit = defineEmits(['search'])
const router = useRouter()
const inner = ref(props.keyword)

function goBack() {
  if (window.history.length > 1) router.back()
  else router.push('/')
}

function onSearch() {
  const kw = inner.value.trim()
  if (!kw) return
  emit('search', kw)
  router.push({ path: '/search', query: { keyword: kw } })
}
</script>

<template>
  <header class="navbar" :style="{ background: bg, color: color || 'inherit' }">
    <div class="left">
      <el-icon v-if="showBack" class="icon-btn" :size="18" @click="goBack"><ArrowLeft /></el-icon>
      <slot name="left" />
    </div>

    <div v-if="showSearch" class="search-box">
      <el-icon :size="14" color="#bbb"><Search /></el-icon>
      <input
        v-model="inner"
        class="search-input"
        type="text"
        placeholder="搜索美食门店、酒店"
        @keyup.enter="onSearch"
      />
      <span class="search-btn" @click="onSearch">搜索</span>
    </div>
    <div v-else class="title ellipsis">{{ title }}</div>

    <div class="right"><slot name="right" /></div>
  </header>
</template>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 20;
  height: 48px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 10px;
  border-bottom: 1px solid var(--border-color);
}
.left,
.right {
  display: flex;
  align-items: center;
  min-width: 24px;
}
.icon-btn {
  cursor: pointer;
  padding: 4px;
}
.title {
  flex: 1;
  text-align: center;
  font-size: 16px;
  font-weight: 600;
}
.search-box {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 6px;
  height: 32px;
  padding: 0 10px;
  background: #f2f3f5;
  border-radius: 16px;
}
.search-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 13px;
  color: var(--text-main);
}
.search-btn {
  font-size: 13px;
  color: var(--dp-orange);
  font-weight: 600;
  cursor: pointer;
}
</style>
