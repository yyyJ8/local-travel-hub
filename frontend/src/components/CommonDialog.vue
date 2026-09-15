<script setup>
/**
 * 通用弹窗组件（公共组件）
 * 预约下单、筛选面板、二次确认等场景复用。
 */
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '' },
  width: { type: String, default: '92%' },
  confirmText: { type: String, default: '确定' },
  cancelText: { type: String, default: '取消' },
  showFooter: { type: Boolean, default: true },
  confirmLoading: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})

function onCancel() {
  emit('cancel')
  visible.value = false
}
</script>

<template>
  <el-dialog
    v-model="visible"
    :title="title"
    :width="width"
    align-center
    append-to-body
    class="common-dialog"
  >
    <slot />
    <template v-if="showFooter" #footer>
      <el-button @click="onCancel">{{ cancelText }}</el-button>
      <el-button type="primary" :loading="confirmLoading" @click="emit('confirm')">
        {{ confirmText }}
      </el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
/* el-dialog 挂载在 body 上，宽度按视口计算（92%）；
   这里补一个上限，避免大屏/投影下弹窗被拉满整个屏幕宽度 */
:deep(.el-dialog) {
  border-radius: 12px;
  max-width: 560px;
}
:deep(.el-dialog__body) {
  padding-top: 6px;
}
</style>
