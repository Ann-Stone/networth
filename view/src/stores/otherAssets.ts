import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getEstateDetails,
  getEstates,
  getInsuranceDetails,
  getInsurances,
  getLoanDetails,
  getLoans,
  getOtherAssets,
  getStockDetails,
  getStocks,
} from '@/api/otherAssets'
import type {
  EstateAsset,
  EstateJournal,
  InsuranceAsset,
  InsuranceJournal,
  LoanAsset,
  LoanJournal,
  OtherAsset,
  StockAsset,
  StockJournal,
} from '@/types/models'

export const useOtherAssetsStore = defineStore('otherAssets', () => {
  const activeTab = ref<string>('stocks')

  // Stocks
  const stocks = ref<StockAsset[]>([])
  const stocksLoading = ref(false)
  async function fetchStocks(assetId: string) {
    stocksLoading.value = true
    try {
      stocks.value = await getStocks({ asset_id: assetId })
    } finally {
      stocksLoading.value = false
    }
  }

  const stockDetails = ref<StockJournal[]>([])
  const stockDetailsLoading = ref(false)
  async function fetchStockDetails(stockId: string) {
    stockDetailsLoading.value = true
    try {
      stockDetails.value = await getStockDetails(stockId)
    } finally {
      stockDetailsLoading.value = false
    }
  }

  // Estates
  const estates = ref<EstateAsset[]>([])
  const estatesLoading = ref(false)
  async function fetchEstates(assetId: string) {
    estatesLoading.value = true
    try {
      estates.value = await getEstates({ asset_id: assetId })
    } finally {
      estatesLoading.value = false
    }
  }

  const estateDetails = ref<EstateJournal[]>([])
  const estateDetailsLoading = ref(false)
  async function fetchEstateDetails(estateId: string) {
    estateDetailsLoading.value = true
    try {
      estateDetails.value = await getEstateDetails(estateId)
    } finally {
      estateDetailsLoading.value = false
    }
  }

  // Insurances
  const insurances = ref<InsuranceAsset[]>([])
  const insurancesLoading = ref(false)
  async function fetchInsurances(assetId: string) {
    insurancesLoading.value = true
    try {
      insurances.value = await getInsurances({ asset_id: assetId })
    } finally {
      insurancesLoading.value = false
    }
  }

  const insuranceDetails = ref<InsuranceJournal[]>([])
  const insuranceDetailsLoading = ref(false)
  async function fetchInsuranceDetails(insuranceId: string) {
    insuranceDetailsLoading.value = true
    try {
      insuranceDetails.value = await getInsuranceDetails(insuranceId)
    } finally {
      insuranceDetailsLoading.value = false
    }
  }

  // Loans
  const loans = ref<LoanAsset[]>([])
  const loansLoading = ref(false)
  async function fetchLoans() {
    loansLoading.value = true
    try {
      loans.value = await getLoans()
    } finally {
      loansLoading.value = false
    }
  }

  const loanDetails = ref<LoanJournal[]>([])
  const loanDetailsLoading = ref(false)
  async function fetchLoanDetails(loanId: string) {
    loanDetailsLoading.value = true
    try {
      loanDetails.value = await getLoanDetails(loanId)
    } finally {
      loanDetailsLoading.value = false
    }
  }

  // Other assets
  const otherAssets = ref<OtherAsset[]>([])
  const otherAssetsLoading = ref(false)
  async function fetchOtherAssets() {
    otherAssetsLoading.value = true
    try {
      otherAssets.value = await getOtherAssets()
    } finally {
      otherAssetsLoading.value = false
    }
  }

  return {
    activeTab,
    stocks,
    stocksLoading,
    fetchStocks,
    stockDetails,
    stockDetailsLoading,
    fetchStockDetails,
    estates,
    estatesLoading,
    fetchEstates,
    estateDetails,
    estateDetailsLoading,
    fetchEstateDetails,
    insurances,
    insurancesLoading,
    fetchInsurances,
    insuranceDetails,
    insuranceDetailsLoading,
    fetchInsuranceDetails,
    loans,
    loansLoading,
    fetchLoans,
    loanDetails,
    loanDetailsLoading,
    fetchLoanDetails,
    otherAssets,
    otherAssetsLoading,
    fetchOtherAssets,
  }
})
