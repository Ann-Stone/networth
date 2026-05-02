<template>
  <div class="flex flex-col h-full">
    <!-- Logo -->
    <div class="flex items-center h-14 px-4 border-b border-surface-dark shrink-0">
      <span v-if="!collapsed" class="font-bold text-base tracking-wide truncate text-cream">
        Balance Sheet
      </span>
      <span v-else class="font-bold text-base text-cream">BS</span>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 overflow-y-auto py-3 space-y-1 px-2">
      <template v-for="item in menuItems" :key="item.name">
        <!-- Group label -->
        <div
          v-if="!collapsed && item.type === 'group'"
          class="px-2 pt-3 pb-1 text-[10px] font-bold uppercase tracking-widest text-muted-text"
        >
          {{ item.label }}
        </div>

        <!-- Nav item with children -->
        <template v-if="item.children">
          <button
            class="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-muted-text hover:bg-surface-dark hover:text-cream transition-colors"
            :class="{ 'justify-center': collapsed }"
            @click="toggleGroup(item.name)"
          >
            <el-icon class="shrink-0 text-base">
              <component :is="item.icon" />
            </el-icon>
            <span v-if="!collapsed" class="flex-1 text-left">{{ item.label }}</span>
            <el-icon
              v-if="!collapsed"
              class="text-xs transition-transform"
              :class="openGroups.has(item.name) ? 'rotate-90' : ''"
            >
              <ArrowRight />
            </el-icon>
          </button>
          <div v-show="!collapsed && openGroups.has(item.name)" class="ml-4 space-y-1">
            <router-link
              v-for="child in item.children"
              :key="child.name"
              :to="child.path"
              class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors"
              :class="
                isActive(child.path)
                  ? 'bg-primary/15 text-primary'
                  : 'text-muted-text hover:bg-surface-dark hover:text-cream'
              "
              @click="onNavClick"
            >
              <span class="w-1.5 h-1.5 rounded-full bg-current shrink-0" />
              {{ child.label }}
            </router-link>
          </div>
        </template>

        <!-- Single nav item -->
        <router-link
          v-else-if="item.type === 'link'"
          :to="item.path!"
          class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors"
          :class="[
            { 'justify-center': collapsed },
            isActive(item.path!)
              ? 'bg-primary/15 text-primary'
              : 'text-muted-text hover:bg-surface-dark hover:text-cream',
          ]"
          @click="onNavClick"
        >
          <el-icon class="shrink-0 text-base">
            <component :is="item.icon" />
          </el-icon>
          <span v-if="!collapsed" class="truncate">{{ item.label }}</span>
        </router-link>
      </template>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import {
  Odometer,
  TrendCharts,
  Document,
  Coin,
  Setting,
  Tools,
  ArrowRight,
} from '@element-plus/icons-vue'

defineProps<{ collapsed: boolean }>()

const route = useRoute()
const appStore = useAppStore()
const openGroups = ref<Set<string>>(new Set(['monthlyReport', 'yearReport', 'setting', 'utilities']))

const menuItems = [
  {
    type: 'link',
    name: 'dashboard',
    label: '儀表板',
    path: '/dashboard',
    icon: Odometer,
  },
  {
    type: 'group',
    name: 'monthlyReport',
    label: '月報',
    icon: TrendCharts,
    children: [
      { name: 'cashFlow', label: '現金流', path: '/monthly-report/cash-flow' },
    ],
  },
  {
    type: 'group',
    name: 'yearReport',
    label: '年報',
    icon: Document,
    children: [
      { name: 'balanceSheet', label: '資產負債表', path: '/year-report/balance-sheet' },
      { name: 'spending', label: '年度支出', path: '/year-report/spending' },
      { name: 'assets', label: '資產概覽', path: '/year-report/assets' },
    ],
  },
  {
    type: 'link',
    name: 'otherAssets',
    label: '資產管理',
    path: '/other-assets',
    icon: Coin,
  },
  {
    type: 'group',
    name: 'setting',
    label: '設定',
    icon: Setting,
    children: [
      { name: 'settingMenu', label: '選單設定', path: '/setting/menu' },
      { name: 'settingBudget', label: '預算設定', path: '/setting/budget' },
      { name: 'settingRemind', label: '提醒設定', path: '/setting/remind' },
    ],
  },
  {
    type: 'group',
    name: 'utilities',
    label: '工具',
    icon: Tools,
    children: [
      { name: 'utilitiesImport', label: '資料匯入', path: '/utilities/import' },
    ],
  },
]

const toggleGroup = (name: string) => {
  if (openGroups.value.has(name)) {
    openGroups.value.delete(name)
  } else {
    openGroups.value.add(name)
  }
}

const isActive = (path: string) => route.path === path || route.path.startsWith(path + '/')

const onNavClick = () => {
  if (appStore.isMobile) {
    appStore.closeSidebarDrawer()
  }
}
</script>
