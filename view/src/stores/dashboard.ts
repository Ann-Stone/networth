import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import dayjs from 'dayjs'
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

export function trailingTwelveMonthsPeriod(now: Date = new Date()): string {
  const end = dayjs(now)
  const start = end.subtract(11, 'month')
  return `${start.format('YYYYMM')}-${end.format('YYYYMM')}`
}

export type SummaryType =
  | 'spending'
  | 'freedom_ratio'
  | 'asset_debt_trend'
  | 'work_freedom_ratio'

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
  work_freedom_ratio: null,
})

const emptyLoadingMap = (): Record<SummaryType, boolean> => ({
  spending: false,
  freedom_ratio: false,
  asset_debt_trend: false,
  work_freedom_ratio: false,
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

  async function fetchSummariesForDashboard(now: Date = new Date()) {
    const period = trailingTwelveMonthsPeriod(now)
    await Promise.all([
      fetchSummary({ type: 'asset_debt_trend', period }),
      fetchSummary({ type: 'freedom_ratio', period }),
      fetchSummary({ type: 'work_freedom_ratio', period }),
    ])
  }

  // Rolling 12-month financial-freedom ratio:
  // (sum(income) - sum(fixed_expenses)) / sum(income) over the returned points.
  // Avoids arithmetic-mean-of-ratios trap. Returns 0 when total income is 0.
  const freedomRatioRolling12M = computed<number>(() => {
    const points = summaries.value.freedom_ratio?.points ?? []
    let income = 0
    let fixed = 0
    for (const p of points) {
      income += p.breakdown?.income ?? 0
      fixed += p.breakdown?.fixed_expenses ?? 0
    }
    return income > 0 ? (income - fixed) / income : 0
  })

  // Rolling 12-month work-freedom ratio: passive / (passive + active).
  // Same numerator-then-denominator strategy as freedomRatioRolling12M.
  const workFreedomRatioRolling12M = computed<number>(() => {
    const points = summaries.value.work_freedom_ratio?.points ?? []
    let passive = 0
    let active = 0
    for (const p of points) {
      passive += p.breakdown?.passive ?? 0
      active += p.breakdown?.active ?? 0
    }
    const total = passive + active
    return total > 0 ? passive / total : 0
  })

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
    fetchSummariesForDashboard,
    freedomRatioRolling12M,
    workFreedomRatioRolling12M,
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
