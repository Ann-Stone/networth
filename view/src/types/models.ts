// ─── Account ──────────────────────────────────────────────────────────────────
export interface Account {
  id: number
  name: string
  balance: number
  type: string
}

// ─── Cash Flow Code ───────────────────────────────────────────────────────────
export interface SubCode {
  id: number
  code: string
  name: string
  parentId: number
}

export interface CashFlowCode {
  id: number
  code: string
  name: string
  type: 'income' | 'expense' | 'fixed'
  subCodes?: SubCode[]
}

// ─── Credit Card ──────────────────────────────────────────────────────────────
export interface CreditCard {
  id: number
  name: string
  limit: number
  balance: number
  billingDate: number
}

// ─── Loan ─────────────────────────────────────────────────────────────────────
export interface Loan {
  id: number
  name: string
  type: string
  interestRate: number
  totalPeriods: number
  periodAmount: number
  startDate: string
  remainingBalance: number
}

// ─── Stock ────────────────────────────────────────────────────────────────────
export interface MonthlyPrice {
  yearMonth: string   // YYYYMM
  price: number
}

export interface Stock {
  id: number
  code: string
  name: string
  expectedSpend: number
  buyPrice: number
  sellPrice?: number
  quantity: number
  buyDate: string
  sellDate?: string
  dividendYield?: number
  roi?: number
  monthlyPrices?: MonthlyPrice[]
}

// ─── Estate ───────────────────────────────────────────────────────────────────
export interface Estate {
  id: number
  name: string
  type: string
  purchasePrice: number
  currentValue: number
  mortgageAmount?: number
  purchaseDate?: string
}

// ─── Insurance ────────────────────────────────────────────────────────────────
export interface Insurance {
  id: number
  name: string
  type: string
  premium: number
  coverage: number
  startDate?: string
  expiryDate?: string
}

// ─── Other Asset ──────────────────────────────────────────────────────────────
export interface OtherAsset {
  id: number
  name: string
  type: string
  amount: number
  note?: string
}

// ─── Budget ───────────────────────────────────────────────────────────────────
export interface BudgetItem {
  id: number
  year: number
  codeId: number
  codeName: string
  type: 'floating' | 'fixed'
  amount: number
}

// ─── Remind ───────────────────────────────────────────────────────────────────
export interface Remind {
  id: number
  name: string
  codeId: number
  codeName: string
  amount: number
  month: number
  isPaid: boolean
}

// ─── Dashboard ────────────────────────────────────────────────────────────────
export interface DashboardSummary {
  totalAssets: number
  totalLiabilities: number
  netAssets: number
  monthlyIncome: number
  monthlyExpense: number
  monthlyGainLoss: number
  assetTrend: AssetTrendPoint[]
}

export interface AssetTrendPoint {
  yearMonth: string   // YYYYMM
  cash: number
  stock: number
  estate: number
  insurance: number
  other: number
  total: number
}

export interface AlarmItem {
  id: number
  name: string
  amount: number
  month: number
  isPaid: boolean
  codeId: number
  codeName: string
}

// ─── Monthly Report — Cash Flow ───────────────────────────────────────────────
export interface CashFlowCategory {
  codeId: number
  codeName: string
  type: 'income' | 'expense' | 'fixed'
  actual: number
  budget: number
  diff: number        // actual - budget
}

export interface LiabilityChange {
  id: number
  name: string
  beginBalance: number
  payment: number
  endBalance: number
}

export interface CashFlowReport {
  year: number
  month: number
  income: number
  expense: number
  fixedExpense: number
  gainLoss: number
  categories: CashFlowCategory[]
  liabilityChanges: LiabilityChange[]
  assetChanges: AssetChange[]
}

export interface AssetChange {
  accountName: string
  beginBalance: number
  endBalance: number
  change: number
}

// ─── Year Report ──────────────────────────────────────────────────────────────
export interface BalanceSheetAssets {
  cash: number
  deposit: number
  stock: number
  estate: number
  insurance: number
  other: number
  total: number
}

export interface BalanceSheetLiabilities {
  creditCard: number
  loan: number
  other: number
  total: number
}

export interface BalanceSheet {
  year: number
  assets: BalanceSheetAssets
  liabilities: BalanceSheetLiabilities
  netAssets: number
}

export interface SpendingItem {
  codeId: number
  codeName: string
  amounts: number[]   // one per month (index 0 = Jan)
  total: number
}

export interface YearSpending {
  year: number
  months: string[]    // ['Jan','Feb',...,'Dec']
  items: SpendingItem[]
  monthlyTotals: number[]
  annualTotal: number
}

export interface AssetComposition {
  year: number
  month: number
  items: { name: string; value: number; percentage: number }[]
  total: number
}

// ─── API Response Wrapper ─────────────────────────────────────────────────────
export interface ApiResponse<T> {
  status: number      // 1 = success
  data: T
  message?: string
}
