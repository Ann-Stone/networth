<template>
  <el-empty :description="message ?? '暫無資料'" />
</template>

<script setup lang="ts">
defineProps<{ message?: string }>()
</script>
