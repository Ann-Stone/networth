<template>
  <header class="h-14 bg-surface-container border-b border-outline-variant flex items-center px-4 gap-4 shrink-0">
    <!-- Hamburger / toggle -->
    <button
      class="p-1.5 rounded-lg bg-transparent border-0 outline-none cursor-pointer text-on-surface-variant hover:bg-surface-container-high transition-colors"
      @click="appStore.toggleSidebar()"
    >
      <el-icon class="text-xl"><Expand v-if="appStore.sidebarCollapsed" /><Fold v-else /></el-icon>
    </button>

    <!-- Breadcrumb -->
    <el-breadcrumb separator="/">
      <el-breadcrumb-item :to="{ path: '/dashboard' }">首頁</el-breadcrumb-item>
      <el-breadcrumb-item
        v-for="crumb in breadcrumbs"
        :key="crumb"
      >
        {{ crumb }}
      </el-breadcrumb-item>
    </el-breadcrumb>

    <!-- Spacer -->
    <div class="flex-1" />

    <!-- Language toggle -->
    <el-button-group size="small">
      <el-button
        :type="appStore.locale === 'zh-TW' ? 'primary' : 'default'"
        @click="appStore.setLocale('zh-TW')"
      >
        中文
      </el-button>
      <el-button
        :type="appStore.locale === 'en' ? 'primary' : 'default'"
        @click="appStore.setLocale('en')"
      >
        EN
      </el-button>
    </el-button-group>

    <!-- Theme toggle -->
    <el-button
      size="small"
      :title="appStore.theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
      @click="appStore.toggleTheme()"
    >
      <el-icon><Sunny v-if="appStore.theme === 'dark'" /><Moon v-else /></el-icon>
    </el-button>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { Expand, Fold, Sunny, Moon } from '@element-plus/icons-vue'

const appStore = useAppStore()
const route = useRoute()

const breadcrumbs = computed<string[]>(() => {
  const meta = route.meta as { breadcrumb?: string[] }
  return meta.breadcrumb ?? []
})
</script>
