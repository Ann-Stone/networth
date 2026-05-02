<template>
  <el-skeleton :rows="rows" animated />
</template>

<script setup lang="ts">
withDefaults(defineProps<{ rows?: number }>(), { rows: 4 })
</script>
