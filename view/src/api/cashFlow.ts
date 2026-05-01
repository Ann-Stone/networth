import request from '@/utils/request'
import type {
  Journal,
  JournalCreate,
  JournalUpdate,
  JournalListResponse,
  JournalExpenditureBudget,
  JournalExpenditureRatio,
  JournalInvestRatio,
  JournalLiability,
  SettleResult,
  StockPriceEntry,
  StockPriceHistory,
} from '@/types/models'

// ─── Journals ────────────────────────────────────────────────────────────────

export function getJournals(vestingMonth: string): Promise<JournalListResponse> {
  return request.get(`/monthly-report/journals/${vestingMonth}`)
}

export function createJournal(data: JournalCreate): Promise<Journal> {
  return request.post('/monthly-report/journals', data)
}

export function updateJournal(id: number, data: JournalUpdate): Promise<Journal> {
  return request.put(`/monthly-report/journals/${id}`, data)
}

export function deleteJournal(id: number): Promise<null> {
  return request.delete(`/monthly-report/journals/${id}`)
}

// ─── Analytics ───────────────────────────────────────────────────────────────

export function getExpenditureBudget(month: string): Promise<JournalExpenditureBudget> {
  return request.get(`/monthly-report/journals/${month}/expenditure-budget`)
}

export function getExpenditureRatio(month: string): Promise<JournalExpenditureRatio> {
  return request.get(`/monthly-report/journals/${month}/expenditure-ratio`)
}

export function getInvestRatio(month: string): Promise<JournalInvestRatio> {
  return request.get(`/monthly-report/journals/${month}/invest-ratio`)
}

export function getLiability(month: string): Promise<JournalLiability> {
  return request.get(`/monthly-report/journals/${month}/liability`)
}

// ─── Settle ──────────────────────────────────────────────────────────────────

export function settleMonth(vestingMonth: string): Promise<SettleResult> {
  return request.put(`/monthly-report/balance/${vestingMonth}/settle`)
}

// ─── Stock prices ────────────────────────────────────────────────────────────
// POST takes a JSON body matching StockPriceHistory (with optional
// trigger_yfinance flag). The granular FE-005 ticket assumed multipart file
// upload; the actual spec is JSON. Tracked in phase summary.

export function getStockPrices(vestingMonth: string): Promise<StockPriceEntry[]> {
  return request.get(`/monthly-report/stock-prices/${vestingMonth}`)
}

export function uploadStockPrices(
  data: StockPriceHistory & { trigger_yfinance?: boolean },
): Promise<StockPriceHistory> {
  return request.post('/monthly-report/stock-prices', data)
}
