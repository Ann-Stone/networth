import { http } from 'msw'
import { ok, fail } from '../util'
import type {
  Journal,
  JournalCreate,
  JournalUpdate,
  JournalListResponse,
  StockPriceEntry,
  StockPriceHistory,
} from '@/types/models'

const CURRENT_MONTH = '202605'

let journals: Journal[] = [
  { distinct_number: 1, vesting_month: CURRENT_MONTH, spend_date: '20260503', spend_way: 'BANK_CTBC', spend_way_type: 'account',     spend_way_table: 'Account',     action_main: 'INC',  action_main_type: 'Income',   action_main_table: 'Code_Data', action_sub: 'INC_SAL',  action_sub_type: 'Income',   action_sub_table: 'Code_Data', spending: 80000, invoice_number: null, note: '5 月薪資' },
  { distinct_number: 2, vesting_month: CURRENT_MONTH, spend_date: '20260505', spend_way: 'BANK_CTBC', spend_way_type: 'account',     spend_way_table: 'Account',     action_main: 'FIX',  action_main_type: 'Fixed',    action_main_table: 'Code_Data', action_sub: 'FIX_RNT',  action_sub_type: 'Fixed',    action_sub_table: 'Code_Data', spending: -18000, invoice_number: null, note: '5 月房租' },
  { distinct_number: 3, vesting_month: CURRENT_MONTH, spend_date: '20260508', spend_way: 'CC_VISA',   spend_way_type: 'credit_card', spend_way_table: 'Credit_Card', action_main: 'FLT',  action_main_type: 'Floating', action_main_table: 'Code_Data', action_sub: 'FLT_FOOD', action_sub_type: 'Floating', action_sub_table: 'Code_Data', spending: -1280, invoice_number: 'AB-12345678', note: '聚餐' },
  { distinct_number: 4, vesting_month: CURRENT_MONTH, spend_date: '20260512', spend_way: 'CC_VISA',   spend_way_type: 'credit_card', spend_way_table: 'Credit_Card', action_main: 'FLT',  action_main_type: 'Floating', action_main_table: 'Code_Data', action_sub: 'FLT_TRP',  action_sub_type: 'Floating', action_sub_table: 'Code_Data', spending: -540,  invoice_number: null, note: '高鐵' },
  { distinct_number: 5, vesting_month: CURRENT_MONTH, spend_date: '20260520', spend_way: 'BANK_CTBC', spend_way_type: 'account',     spend_way_table: 'Account',     action_main: 'INV',  action_main_type: 'Invest',   action_main_table: 'Code_Data', action_sub: 'INV_STK',  action_sub_type: 'Invest',   action_sub_table: 'Code_Data', spending: -15000, invoice_number: null, note: '台股定期定額' },
  { distinct_number: 6, vesting_month: CURRENT_MONTH, spend_date: '20260518', spend_way: 'BANK_CTBC', spend_way_type: 'account',     spend_way_table: 'Account',     action_main: 'FIX',  action_main_type: 'Fixed',    action_main_table: 'Code_Data', action_sub: 'FIX_UTL',  action_sub_type: 'Fixed',    action_sub_table: 'Code_Data', spending: -2400, invoice_number: null, note: '電費' },
  { distinct_number: 7, vesting_month: '202604',     spend_date: '20260418', spend_way: 'BANK_CTBC', spend_way_type: 'account',     spend_way_table: 'Account',     action_main: 'INC',  action_main_type: 'Income',   action_main_table: 'Code_Data', action_sub: 'INC_SAL',  action_sub_type: 'Income',   action_sub_table: 'Code_Data', spending: 80000, invoice_number: null, note: '4 月薪資' },
]
let journalSeq = journals.length

function listForMonth(month: string): JournalListResponse {
  const items = journals.filter((j) => j.vesting_month === month)
  const gain_loss = items.reduce((sum, j) => sum + j.spending, 0)
  return { items, gain_loss }
}

// ─── Analytics fixtures ──────────────────────────────────────────────────────

function expenditureBudget() {
  return {
    rows: [
      { action_main_type: 'Fixed',    actual: 20400, expected: 21000, diff: 600,   usage_rate: 0.97 },
      { action_main_type: 'Floating', actual: 1820,  expected: 15000, diff: 13180, usage_rate: 0.12 },
      { action_main_type: 'Invest',   actual: 15000, expected: 15000, diff: 0,     usage_rate: 1.0  },
      { action_main_type: 'Income',   actual: 80000, expected: 90000, diff: 10000, usage_rate: 0.89 },
    ],
  }
}

function expenditureRatio() {
  return {
    outer: [
      { name: '固定支出', value: 20400 },
      { name: '浮動支出', value: 1820 },
      { name: '投資',   value: 15000 },
    ],
    inner: [
      { name: '房租', value: 18000 },
      { name: '水電', value: 2400 },
      { name: '伙食', value: 1280 },
      { name: '交通', value: 540 },
      { name: '股票', value: 15000 },
    ],
  }
}

function investRatio() {
  return {
    items: [
      { name: '台股 ETF', value: 9000 },
      { name: '美股',   value: 4500 },
      { name: '債券',   value: 1500 },
    ],
  }
}

function liability() {
  return {
    items: [
      { credit_card_id: 'CC_VISA', credit_card_name: 'Visa 御璽',   amount: 1820 },
      { credit_card_id: 'CC_MC',   credit_card_name: 'MasterCard 鈦金', amount: 0 },
      { credit_card_id: 'CC_AMEX', credit_card_name: 'Amex Gold',    amount: 0 },
    ],
  }
}

// ─── Stock prices ────────────────────────────────────────────────────────────

let stockPriceHistory: StockPriceHistory[] = [
  { stock_code: '0050', fetch_date: '20260430', open_price: 168.5, highest_price: 170.2, lowest_price: 167.0, close_price: 169.8 },
  { stock_code: '2330', fetch_date: '20260430', open_price: 920,   highest_price: 935,   lowest_price: 918,   close_price: 932   },
  { stock_code: 'VOO',  fetch_date: '20260430', open_price: 510,   highest_price: 514,   lowest_price: 508,   close_price: 512.5 },
]

function currentPrices(month: string): StockPriceEntry[] {
  void month
  return [
    { stock_code: '0050', stock_name: '元大台灣 50',     close_price: 169.8 },
    { stock_code: '2330', stock_name: '台積電',         close_price: 932   },
    { stock_code: 'VOO',  stock_name: 'Vanguard S&P500', close_price: 512.5 },
  ]
}

// ─── Handlers ────────────────────────────────────────────────────────────────

export const monthlyReportHandlers = [
  // Journal CRUD — specific paths first
  http.get('*/monthly-report/journals/:month/expenditure-budget', () => ok(expenditureBudget())),
  http.get('*/monthly-report/journals/:month/expenditure-ratio',  () => ok(expenditureRatio())),
  http.get('*/monthly-report/journals/:month/invest-ratio',       () => ok(investRatio())),
  http.get('*/monthly-report/journals/:month/liability',          () => ok(liability())),
  http.get('*/monthly-report/journals/:month', ({ params }) => ok(listForMonth(String(params.month)))),
  http.post('*/monthly-report/journals', async ({ request }) => {
    const body = (await request.json()) as JournalCreate
    journalSeq += 1
    const created: Journal = {
      distinct_number: journalSeq,
      vesting_month: body.vesting_month,
      spend_date: body.spend_date,
      spend_way: body.spend_way,
      spend_way_type: body.spend_way_type,
      spend_way_table: body.spend_way_table,
      action_main: body.action_main,
      action_main_type: body.action_main_type,
      action_main_table: body.action_main_table,
      action_sub: body.action_sub ?? null,
      action_sub_type: body.action_sub_type ?? null,
      action_sub_table: body.action_sub_table ?? null,
      spending: body.spending,
      invoice_number: body.invoice_number ?? null,
      note: body.note ?? null,
    }
    journals.push(created)
    return ok(created)
  }),
  http.put('*/monthly-report/journals/:id', async ({ params, request }) => {
    const id = Number(params.id)
    const body = (await request.json()) as JournalUpdate
    const idx = journals.findIndex((j) => j.distinct_number === id)
    const cur = journals[idx]
    if (!cur) return fail('journal not found', 404)
    const next: Journal = { ...cur, ...body }
    journals[idx] = next
    return ok(next)
  }),
  http.delete('*/monthly-report/journals/:id', ({ params }) => {
    const id = Number(params.id)
    const before = journals.length
    journals = journals.filter((j) => j.distinct_number !== id)
    if (journals.length === before) return fail('journal not found', 404)
    return ok(null)
  }),

  // Settle
  http.put('*/monthly-report/balance/:month/settle', ({ params }) =>
    ok({
      vesting_month: String(params.month),
      estate_rows: 2,
      insurance_rows: 3,
      loan_rows: 2,
      stock_rows: 4,
      account_rows: 3,
      credit_card_rows: 3,
    }),
  ),

  // Stock prices
  http.get('*/monthly-report/stock-prices/:month', ({ params }) =>
    ok(currentPrices(String(params.month))),
  ),
  http.post('*/monthly-report/stock-prices', async ({ request }) => {
    const body = (await request.json()) as StockPriceHistory
    stockPriceHistory = stockPriceHistory.filter(
      (h) => !(h.stock_code === body.stock_code && h.fetch_date === body.fetch_date),
    )
    stockPriceHistory.push(body)
    return ok(body)
  }),
]
