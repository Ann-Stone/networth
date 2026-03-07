<template>
  <div class="flex flex-col items-center justify-center h-full gap-4 text-gray-500">
    <p class="text-6xl font-bold text-gray-200">404</p>
    <p class="text-xl">找不到此頁面</p>
    <el-button type="primary" @click="router.push('/dashboard')">返回首頁</el-button>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
const router = useRouter()
</script>
