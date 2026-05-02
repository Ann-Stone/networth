<template>
  <el-dialog
    :model-value="modelValue"
    :title="title"
    :width="width"
    :close-on-click-modal="false"
    append-to-body
    @update:model-value="(v: boolean) => emit('update:modelValue', v)"
    @close="onCancel"
  >
    <slot />

    <template #footer>
      <slot name="footer">
        <el-button @click="onCancel">{{ cancelText }}</el-button>
        <el-button type="primary" :loading="loading" @click="onSubmit">
          {{ submitText }}
        </el-button>
      </slot>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    modelValue: boolean
    title: string
    loading?: boolean
    submitText?: string
    cancelText?: string
    width?: string
  }>(),
  {
    loading: false,
    submitText: '確認',
    cancelText: '取消',
    width: '520px',
  },
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'submit'): void
  (e: 'cancel'): void
}>()

const onSubmit = () => emit('submit')
const onCancel = () => {
  emit('cancel')
  emit('update:modelValue', false)
}

void props
</script>
