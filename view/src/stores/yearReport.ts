import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getAssetsReport,
  getBalanceReport,
  getExpenditureReport,
} from '@/api/yearReport'
import type {
  AssetReport,
  BalanceReport,
  ExpenditureReport,
} from '@/types/models'

export const useYearReportStore = defineStore('yearReport', () => {
  const selectedYear = ref<number>(new Date().getFullYear())

  // Balance report — API takes no year param; year is selection state only.
  const balanceReport = ref<BalanceReport | null>(null)
  const balanceLoading = ref(false)
  async function fetchBalanceReport(year?: number) {
    if (year != null) selectedYear.value = year
    balanceLoading.value = true
    try {
      balanceReport.value = await getBalanceReport()
    } finally {
      balanceLoading.value = false
    }
  }

  // Expenditure report — API anchor is vesting_month YYYYMM; we anchor on
  // December of selectedYear when only year is supplied.
  const expenditureReport = ref<ExpenditureReport | null>(null)
  const expenditureLoading = ref(false)
  async function fetchExpenditureReport(type: string, year?: number) {
    if (year != null) selectedYear.value = year
    const anchorYear = year ?? selectedYear.value
    const vestingMonth = `${anchorYear}12`
    expenditureLoading.value = true
    try {
      expenditureReport.value = await getExpenditureReport(type, {
        vesting_month: vestingMonth,
      })
    } finally {
      expenditureLoading.value = false
    }
  }

  // Assets report — API takes no year param.
  const assetsReport = ref<AssetReport | null>(null)
  const assetsLoading = ref(false)
  async function fetchAssetsReport(year?: number) {
    if (year != null) selectedYear.value = year
    assetsLoading.value = true
    try {
      assetsReport.value = await getAssetsReport()
    } finally {
      assetsLoading.value = false
    }
  }

  return {
    selectedYear,
    balanceReport,
    balanceLoading,
    fetchBalanceReport,
    expenditureReport,
    expenditureLoading,
    fetchExpenditureReport,
    assetsReport,
    assetsLoading,
    fetchAssetsReport,
  }
})
