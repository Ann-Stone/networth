import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  // Sidebar state
  const sidebarCollapsed = ref(false)
  const isMobile = ref(false)
  const sidebarDrawerVisible = ref(false)

  // Language
  const locale = ref<'zh-TW' | 'en'>('zh-TW')

  const toggleSidebar = () => {
    if (isMobile.value) {
      sidebarDrawerVisible.value = !sidebarDrawerVisible.value
    } else {
      sidebarCollapsed.value = !sidebarCollapsed.value
    }
  }

  const closeSidebarDrawer = () => {
    sidebarDrawerVisible.value = false
  }

  const setMobile = (val: boolean) => {
    isMobile.value = val
  }

  const setLocale = (lang: 'zh-TW' | 'en') => {
    locale.value = lang
  }

  const contentClass = computed(() =>
    sidebarCollapsed.value ? 'ml-[64px]' : 'ml-[220px]',
  )

  return {
    sidebarCollapsed,
    isMobile,
    sidebarDrawerVisible,
    locale,
    contentClass,
    toggleSidebar,
    closeSidebarDrawer,
    setMobile,
    setLocale,
  }
})
