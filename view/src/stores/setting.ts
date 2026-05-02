import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getAccounts,
  getAlarms,
  getBudgetYears,
  getBudgets,
  getCodesWithSub,
  getCreditCards,
} from '@/api/setting'
import type {
  Account,
  Alarm,
  BudgetRead,
  CodeDataWithSub,
  CreditCard,
} from '@/types/models'

export const useSettingStore = defineStore('setting', () => {
  // Accounts
  const accounts = ref<Account[]>([])
  const accountsLoading = ref(false)
  async function fetchAccounts(params?: {
    name?: string
    account_type?: string
    in_use?: string
  }) {
    accountsLoading.value = true
    try {
      accounts.value = await getAccounts(params)
    } finally {
      accountsLoading.value = false
    }
  }

  // Alarms
  const alarms = ref<Alarm[]>([])
  const alarmsLoading = ref(false)
  async function fetchAlarms() {
    alarmsLoading.value = true
    try {
      alarms.value = await getAlarms()
    } finally {
      alarmsLoading.value = false
    }
  }

  // Budgets
  const budgets = ref<BudgetRead[]>([])
  const budgetsLoading = ref(false)
  const budgetYears = ref<string[]>([])
  async function fetchBudgets(year: number) {
    budgetsLoading.value = true
    try {
      budgets.value = await getBudgets(year)
    } finally {
      budgetsLoading.value = false
    }
  }
  async function fetchBudgetYears() {
    budgetYears.value = await getBudgetYears()
  }

  // Codes (with sub)
  const codesWithSub = ref<CodeDataWithSub[]>([])
  const codesLoading = ref(false)
  async function fetchCodesWithSub() {
    codesLoading.value = true
    try {
      codesWithSub.value = await getCodesWithSub()
    } finally {
      codesLoading.value = false
    }
  }

  // Credit cards
  const creditCards = ref<CreditCard[]>([])
  const creditCardsLoading = ref(false)
  async function fetchCreditCards(params?: {
    card_name?: string
    in_use?: string
  }) {
    creditCardsLoading.value = true
    try {
      creditCards.value = await getCreditCards(params)
    } finally {
      creditCardsLoading.value = false
    }
  }

  return {
    accounts,
    accountsLoading,
    fetchAccounts,
    alarms,
    alarmsLoading,
    fetchAlarms,
    budgets,
    budgetsLoading,
    budgetYears,
    fetchBudgets,
    fetchBudgetYears,
    codesWithSub,
    codesLoading,
    fetchCodesWithSub,
    creditCards,
    creditCardsLoading,
    fetchCreditCards,
  }
})
