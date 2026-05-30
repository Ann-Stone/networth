import { http } from 'msw'
import { ok } from '../util'
import type {
  AssetReport,
  BalanceReport,
  ExpenditureReport,
  StockAllocationReport,
} from '@/types/models'

const balance: BalanceReport = {
  assets: {
    accounts: [
      { name: '現金 (TWD)', amount: 125000, currency: 'TWD' },
      { name: '中信活存',   amount: 480000, currency: 'TWD' },
      { name: 'Wise USD',  amount: 240000, currency: 'TWD' },
    ],
    estates: [
      { name: '主要住所', amount: 12500000, currency: 'TWD' },
      { name: '投資宅 A', amount: 8500000,  currency: 'TWD' },
    ],
    insurances: [
      { name: '終身壽險', amount: 320000,   currency: 'TWD' },
      { name: '醫療險',   amount: 80000,    currency: 'TWD' },
    ],
    stocks: [
      { name: '元大台灣 50',     amount: 169800, currency: 'TWD' },
      { name: '台積電',         amount: 372800, currency: 'TWD' },
      { name: 'Vanguard S&P500', amount: 192500, currency: 'TWD' },
    ],
  },
  liabilities: {
    credit_cards: [
      { name: 'Visa 御璽', amount: 1820, currency: 'TWD' },
    ],
    loans: [
      { name: '房貸主貸', amount: 6800000, currency: 'TWD' },
      { name: '車貸',     amount: 480000,  currency: 'TWD' },
      { name: '信貸',     amount: 400000,  currency: 'TWD' },
    ],
  },
  net_worth: 14998480,
}

function expenditureSeries(type: string, vestingMonth: string): ExpenditureReport {
  const baseYear = Number(vestingMonth.slice(0, 4))
  if (type === 'yearly') {
    return {
      type,
      points: [
        { period: String(baseYear - 2), amount: 480000 },
        { period: String(baseYear - 1), amount: 520000 },
        { period: String(baseYear),     amount: 560000 },
      ],
    }
  }
  // monthly default — 12 points ending at vestingMonth
  const points: { period: string; amount: number }[] = []
  let y = baseYear
  let m = Number(vestingMonth.slice(4, 6))
  for (let i = 0; i < 12; i++) {
    points.unshift({ period: `${y}${String(m).padStart(2, '0')}`, amount: 32000 + Math.round(Math.sin(i) * 6000) })
    m -= 1
    if (m === 0) { m = 12; y -= 1 }
  }
  return { type, points }
}

const assetReport: AssetReport = {
  total: 22810100,
  items: [
    { type: '存款',     amount: 845000,   share: 0.037 },
    { type: '不動產',   amount: 21000000, share: 0.92  },
    { type: '保單',     amount: 400000,   share: 0.018 },
    { type: '股票',     amount: 735100,   share: 0.032 },
    { type: '其他',     amount: -169000,  share: -0.007 },
  ],
}

const stockAllocation: StockAllocationReport = {
  total: 735100,
  items: [
    { category_id: 'SC-001', category_name: '成長型', amount: 542600, share: 73.8 },
    { category_id: 'SC-002', category_name: '債券',   amount: 110000, share: 15.0 },
    { category_id: null,     category_name: '未分類', amount: 82500,  share: 11.2 },
  ],
}

export const reportsHandlers = [
  http.get('*/reports/balance', () => ok(balance)),
  http.get('*/reports/expenditure/:type', ({ params, request }) => {
    const url = new URL(request.url)
    const month = url.searchParams.get('vesting_month') ?? '202604'
    return ok(expenditureSeries(String(params.type), month))
  }),
  http.get('*/reports/assets', () => ok(assetReport)),
  http.get('*/reports/stock-allocation', () => ok(stockAllocation)),
]
