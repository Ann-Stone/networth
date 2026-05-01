import request from '@/utils/request'
import type {
  AssetReport,
  BalanceReport,
  ExpenditureReport,
} from '@/types/models'

export function getBalanceReport(): Promise<BalanceReport> {
  return request.get('/reports/balance')
}

export function getExpenditureReport(
  type: string,
  params: { vesting_month: string },
): Promise<ExpenditureReport> {
  return request.get(`/reports/expenditure/${type}`, { params })
}

export function getAssetsReport(): Promise<AssetReport> {
  return request.get('/reports/assets')
}
