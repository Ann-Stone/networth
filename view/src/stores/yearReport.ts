import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getAssetsReport,
  getBalanceReport,
  getBudgetVariance,
  getCashFlow,
  getExpenditureComposition,
  getExpenditureReport,
  getExpenseInsights,
  getIncomeExpenseReport,
  getStockAllocation,
} from '@/api/yearReport'
import type {
  AssetReport,
  BalanceReport,
  BudgetVariance,
  CashFlow,
  ExpenditureComposition,
  ExpenditureReport,
  ExpenseInsights,
  IncomeExpenseReport,
  StockAllocationReport,
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

  // Income vs expense report — same anchor convention as expenditure
  // (December of selectedYear when only a year is supplied).
  const incomeExpenseReport = ref<IncomeExpenseReport | null>(null)
  const incomeExpenseLoading = ref(false)
  async function fetchIncomeExpenseReport(type: string, year?: number) {
    if (year != null) selectedYear.value = year
    const anchorYear = year ?? selectedYear.value
    const vestingMonth = `${anchorYear}12`
    incomeExpenseLoading.value = true
    try {
      incomeExpenseReport.value = await getIncomeExpenseReport(type, {
        vesting_month: vestingMonth,
      })
    } finally {
      incomeExpenseLoading.value = false
    }
  }

  // Expenditure composition tree — same anchor convention as income/expense.
  const compositionReport = ref<ExpenditureComposition | null>(null)
  const compositionLoading = ref(false)
  async function fetchExpenditureComposition(type: string, year?: number) {
    if (year != null) selectedYear.value = year
    const anchorYear = year ?? selectedYear.value
    const vestingMonth = `${anchorYear}12`
    compositionLoading.value = true
    try {
      compositionReport.value = await getExpenditureComposition(type, {
        vesting_month: vestingMonth,
      })
    } finally {
      compositionLoading.value = false
    }
  }

  // Budget vs actual variance — annual, keyed by year only.
  const budgetReport = ref<BudgetVariance | null>(null)
  const budgetLoading = ref(false)
  async function fetchBudgetVariance(year?: number) {
    if (year != null) selectedYear.value = year
    const anchorYear = year ?? selectedYear.value
    budgetLoading.value = true
    try {
      budgetReport.value = await getBudgetVariance(anchorYear)
    } finally {
      budgetLoading.value = false
    }
  }

  // Cash-flow statement (生活/投資/債務) — same anchor convention.
  const cashFlowReport = ref<CashFlow | null>(null)
  const cashFlowLoading = ref(false)
  async function fetchCashFlow(type: string, year?: number) {
    if (year != null) selectedYear.value = year
    const anchorYear = year ?? selectedYear.value
    const vestingMonth = `${anchorYear}12`
    cashFlowLoading.value = true
    try {
      cashFlowReport.value = await getCashFlow(type, { vesting_month: vestingMonth })
    } finally {
      cashFlowLoading.value = false
    }
  }

  // Expense insights — YoY + largest transactions, keyed by year.
  const insightsReport = ref<ExpenseInsights | null>(null)
  const insightsLoading = ref(false)
  async function fetchExpenseInsights(year?: number) {
    if (year != null) selectedYear.value = year
    const anchorYear = year ?? selectedYear.value
    insightsLoading.value = true
    try {
      insightsReport.value = await getExpenseInsights(anchorYear)
    } finally {
      insightsLoading.value = false
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

  // Stock allocation by category — API takes no year param.
  const stockAllocation = ref<StockAllocationReport | null>(null)
  const stockAllocationLoading = ref(false)
  async function fetchStockAllocation() {
    stockAllocationLoading.value = true
    try {
      stockAllocation.value = await getStockAllocation()
    } finally {
      stockAllocationLoading.value = false
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
    incomeExpenseReport,
    incomeExpenseLoading,
    fetchIncomeExpenseReport,
    compositionReport,
    compositionLoading,
    fetchExpenditureComposition,
    budgetReport,
    budgetLoading,
    fetchBudgetVariance,
    cashFlowReport,
    cashFlowLoading,
    fetchCashFlow,
    insightsReport,
    insightsLoading,
    fetchExpenseInsights,
    assetsReport,
    assetsLoading,
    fetchAssetsReport,
    stockAllocation,
    stockAllocationLoading,
    fetchStockAllocation,
  }
})
