import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

const THEME_STORAGE_KEY = 'networth-theme'

type Theme = 'dark' | 'light'

function readStoredTheme(): Theme {
  if (typeof window === 'undefined') return 'dark'
  const saved = window.localStorage.getItem(THEME_STORAGE_KEY)
  return saved === 'light' || saved === 'dark' ? saved : 'dark'
}

function applyThemeClass(theme: Theme) {
  if (typeof document === 'undefined') return
  const root = document.documentElement
  if (theme === 'dark') root.classList.add('dark')
  else root.classList.remove('dark')
}

export const useAppStore = defineStore('app', () => {
  // Sidebar state
  const sidebarCollapsed = ref(false)
  const isMobile = ref(false)
  const sidebarDrawerVisible = ref(false)

  // Language
  const locale = ref<'zh-TW' | 'en'>('zh-TW')

  // Theme
  const theme = ref<Theme>(readStoredTheme())
  applyThemeClass(theme.value)

  watch(theme, (next) => {
    applyThemeClass(next)
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(THEME_STORAGE_KEY, next)
    }
  })

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

  const toggleTheme = () => {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
  }

  const contentClass = computed(() =>
    sidebarCollapsed.value ? 'ml-[64px]' : 'ml-[220px]',
  )

  return {
    sidebarCollapsed,
    isMobile,
    sidebarDrawerVisible,
    locale,
    theme,
    contentClass,
    toggleSidebar,
    closeSidebarDrawer,
    setMobile,
    setLocale,
    toggleTheme,
  }
})
