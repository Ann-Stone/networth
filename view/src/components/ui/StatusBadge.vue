<template>
  <el-tag :type="resolvedType" size="small" round>
    {{ value }}
  </el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type TagType = 'success' | 'danger' | 'info' | 'warning'

const props = defineProps<{
  value: string
  type?: TagType
}>()

const resolvedType = computed<TagType>(() => {
  if (props.type) return props.type
  if (props.value === 'Y') return 'success'
  if (props.value === 'N') return 'danger'
  return 'info'
})
</script>
