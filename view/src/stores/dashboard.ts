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

export interface DashboardSummaryParams {
  type: string
  period: string
}

export interface DashboardBudgetParams {
  type: string
  period: string
}

export const useDashboardStore = defineStore('dashboard', () => {
  // Summary
  const summary = ref<DashboardSummary | null>(null)
  const summaryLoading = ref(false)
  async function fetchSummary(params: DashboardSummaryParams) {
    summaryLoading.value = true
    try {
      summary.value = await getDashboardSummary(params)
    } finally {
      summaryLoading.value = false
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
    summary,
    summaryLoading,
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
