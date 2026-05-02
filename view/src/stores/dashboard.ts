import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getDashboardAlarms,
  getDashboardBudget,
  getDashboardGifts,
  getDashboardSummary,
  getTargets,
} from '@/api/dashboard'
import type {
  DashboardAlarm,
  DashboardBudget,
  DashboardGift,
  DashboardSummary,
  TargetSetting,
} from '@/types/models'

export type SummaryType = 'spending' | 'freedom_ratio' | 'asset_debt_trend'

export interface DashboardSummaryParams {
  type: SummaryType
  period: string
}

export interface DashboardBudgetParams {
  type: 'monthly' | 'yearly'
  period: string
}

const emptySummaryMap = (): Record<SummaryType, DashboardSummary | null> => ({
  spending: null,
  freedom_ratio: null,
  asset_debt_trend: null,
})

const emptyLoadingMap = (): Record<SummaryType, boolean> => ({
  spending: false,
  freedom_ratio: false,
  asset_debt_trend: false,
})

export const useDashboardStore = defineStore('dashboard', () => {
  // Summary — keyed by SummaryType variant
  const summaries = ref<Record<SummaryType, DashboardSummary | null>>(emptySummaryMap())
  const summariesLoading = ref<Record<SummaryType, boolean>>(emptyLoadingMap())
  async function fetchSummary(params: DashboardSummaryParams) {
    summariesLoading.value[params.type] = true
    try {
      summaries.value[params.type] = await getDashboardSummary(params)
    } finally {
      summariesLoading.value[params.type] = false
    }
  }

  // Alarms
  const alarms = ref<DashboardAlarm[]>([])
  const alarmsLoading = ref(false)
  async function fetchAlarms() {
    alarmsLoading.value = true
    try {
      alarms.value = await getDashboardAlarms()
    } finally {
      alarmsLoading.value = false
    }
  }

  // Targets
  const targets = ref<TargetSetting[]>([])
  const targetsLoading = ref(false)
  async function fetchTargets() {
    targetsLoading.value = true
    try {
      targets.value = await getTargets()
    } finally {
      targetsLoading.value = false
    }
  }

  // Budget
  const budget = ref<DashboardBudget | null>(null)
  const budgetLoading = ref(false)
  async function fetchBudget(params: DashboardBudgetParams) {
    budgetLoading.value = true
    try {
      budget.value = await getDashboardBudget(params)
    } finally {
      budgetLoading.value = false
    }
  }

  // Gifts
  const gifts = ref<DashboardGift[]>([])
  const giftsLoading = ref(false)
  async function fetchGifts(year: number) {
    giftsLoading.value = true
    try {
      gifts.value = await getDashboardGifts(year)
    } finally {
      giftsLoading.value = false
    }
  }

  return {
    summaries,
    summariesLoading,
    fetchSummary,
    alarms,
    alarmsLoading,
    fetchAlarms,
    targets,
    targetsLoading,
    fetchTargets,
    budget,
    budgetLoading,
    fetchBudget,
    gifts,
    giftsLoading,
    fetchGifts,
  }
})
