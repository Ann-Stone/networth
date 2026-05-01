import request from '@/utils/request'
import type {
  ImportResult,
  SelectionAccount,
  SelectionCode,
  SelectionCreditCard,
  SelectionInsurance,
  SelectionLoan,
} from '@/types/models'

// ─── Selection dropdowns ─────────────────────────────────────────────────────

export function getAccountSelections(): Promise<SelectionAccount[]> {
  return request.get('/utilities/selections/accounts')
}

export function getCodeSelections(codeGroup?: string): Promise<SelectionCode[]> {
  const url = codeGroup
    ? `/utilities/selections/codes/${codeGroup}`
    : '/utilities/selections/codes'
  return request.get(url)
}

export function getCreditCardSelections(): Promise<SelectionCreditCard[]> {
  return request.get('/utilities/selections/credit-cards')
}

export function getInsuranceSelections(): Promise<SelectionInsurance[]> {
  return request.get('/utilities/selections/insurances')
}

export function getLoanSelections(): Promise<SelectionLoan[]> {
  return request.get('/utilities/selections/loans')
}

// ─── Import endpoints (background tasks) ─────────────────────────────────────
// API contract: each endpoint takes a JSON body { period: "YYYYMM" } (empty
// string falls back to today). The granular FE-004 ticket assumed multipart
// file upload; the actual spec is JSON. Tracked in phase summary.

export function importStockPrices(period: string): Promise<ImportResult> {
  return request.post('/utilities/import/stock-prices', { period })
}

export function importFxRates(period: string): Promise<ImportResult> {
  return request.post('/utilities/import/fx-rates', { period })
}

export function importInvoices(period: string): Promise<ImportResult> {
  return request.post('/utilities/import/invoices', { period })
}
