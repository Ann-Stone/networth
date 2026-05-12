<template>
  <el-config-provider :locale="zhTw">
    <router-view />
  </el-config-provider>
</template>

<script setup lang="ts">
import zhTw from 'element-plus/es/locale/lang/zh-tw'
</script>
