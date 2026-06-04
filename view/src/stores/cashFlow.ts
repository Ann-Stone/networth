import { defineStore } from 'pinia'
import { ref } from 'vue'
import dayjs from 'dayjs'
import {
  getEstateValues,
  getEstateValueSuggestions,
  getExpenditureBudget,
  getExpenditureRatio,
  getInvestRatio,
  getInsuranceValues,
  getJournals,
  getLiability,
  getStockPrices,
  refreshHousePriceIndex,
} from '@/api/cashFlow'
import type {
  EstateValueMonth,
  EstateValueSuggestion,
  IndexRefreshResult,
  InsuranceValueMonth,
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

  // Insurance surrender values (解約金)
  const insuranceValues = ref<InsuranceValueMonth[]>([])
  const insuranceValuesLoading = ref(false)
  async function fetchInsuranceValues(month?: string) {
    const m = month ?? selectedMonth.value
    insuranceValuesLoading.value = true
    try {
      insuranceValues.value = await getInsuranceValues(m)
    } finally {
      insuranceValuesLoading.value = false
    }
  }

  // Estate market values (估值)
  const estateValues = ref<EstateValueMonth[]>([])
  const estateValuesLoading = ref(false)
  async function fetchEstateValues(month?: string) {
    const m = month ?? selectedMonth.value
    estateValuesLoading.value = true
    try {
      estateValues.value = await getEstateValues(m)
    } finally {
      estateValuesLoading.value = false
    }
  }

  // Index-based suggested market values (P3)
  const estateSuggestions = ref<EstateValueSuggestion[]>([])
  async function fetchEstateSuggestions(month?: string) {
    const m = month ?? selectedMonth.value
    estateSuggestions.value = await getEstateValueSuggestions(m)
  }
  async function refreshEstateIndex(): Promise<IndexRefreshResult> {
    const res = await refreshHousePriceIndex()
    await fetchEstateSuggestions()
    return res
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
    insuranceValues,
    insuranceValuesLoading,
    fetchInsuranceValues,
    estateValues,
    estateValuesLoading,
    fetchEstateValues,
    estateSuggestions,
    fetchEstateSuggestions,
    refreshEstateIndex,
  }
})
