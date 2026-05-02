import { defineStore } from 'pinia'
import { ref } from 'vue'
import dayjs from 'dayjs'
import {
  getExpenditureBudget,
  getExpenditureRatio,
  getInvestRatio,
  getJournals,
  getLiability,
  getStockPrices,
} from '@/api/cashFlow'
import type {
  Journal,
  JournalExpenditureBudget,
  JournalExpenditureRatio,
  JournalInvestRatio,
  JournalLiability,
  StockPriceRead,
} from '@/types/models'

export const useCashFlowStore = defineStore('cashFlow', () => {
  const selectedMonth = ref<string>(dayjs().format('YYYYMM'))

  // Journals
  const journals = ref<Journal[]>([])
  const journalsLoading = ref(false)
  const journalsGainLoss = ref<number>(0)
  async function fetchJournals(month?: string) {
    const m = month ?? selectedMonth.value
    journalsLoading.value = true
    try {
      const res = await getJournals(m)
      journals.value = res.items
      journalsGainLoss.value = res.gain_loss
    } finally {
      journalsLoading.value = false
    }
  }

  // Expenditure budget
  const expenditureBudget = ref<JournalExpenditureBudget | null>(null)
  const expenditureBudgetLoading = ref(false)
  async function fetchExpenditureBudget(month?: string) {
    const m = month ?? selectedMonth.value
    expenditureBudgetLoading.value = true
    try {
      expenditureBudget.value = await getExpenditureBudget(m)
    } finally {
      expenditureBudgetLoading.value = false
    }
  }

  // Expenditure ratio
  const expenditureRatio = ref<JournalExpenditureRatio | null>(null)
  const expenditureRatioLoading = ref(false)
  async function fetchExpenditureRatio(month?: string) {
    const m = month ?? selectedMonth.value
    expenditureRatioLoading.value = true
    try {
      expenditureRatio.value = await getExpenditureRatio(m)
    } finally {
      expenditureRatioLoading.value = false
    }
  }

  // Invest ratio
  const investRatio = ref<JournalInvestRatio | null>(null)
  const investRatioLoading = ref(false)
  async function fetchInvestRatio(month?: string) {
    const m = month ?? selectedMonth.value
    investRatioLoading.value = true
    try {
      investRatio.value = await getInvestRatio(m)
    } finally {
      investRatioLoading.value = false
    }
  }

  // Liability
  const liability = ref<JournalLiability | null>(null)
  const liabilityLoading = ref(false)
  async function fetchLiability(month?: string) {
    const m = month ?? selectedMonth.value
    liabilityLoading.value = true
    try {
      liability.value = await getLiability(m)
    } finally {
      liabilityLoading.value = false
    }
  }

  // Stock prices
  const stockPrices = ref<StockPriceRead[]>([])
  const stockPricesLoading = ref(false)
  async function fetchStockPrices(month?: string) {
    const m = month ?? selectedMonth.value
    stockPricesLoading.value = true
    try {
      stockPrices.value = await getStockPrices(m)
    } finally {
      stockPricesLoading.value = false
    }
  }

  return {
    selectedMonth,
    journals,
    journalsLoading,
    journalsGainLoss,
    fetchJournals,
    expenditureBudget,
    expenditureBudgetLoading,
    fetchExpenditureBudget,
    expenditureRatio,
    expenditureRatioLoading,
    fetchExpenditureRatio,
    investRatio,
    investRatioLoading,
    fetchInvestRatio,
    liability,
    liabilityLoading,
    fetchLiability,
    stockPrices,
    stockPricesLoading,
    fetchStockPrices,
  }
})
