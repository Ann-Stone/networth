// =============================================================================
// Networth API — TypeScript model definitions
// Single source of truth. All field names are snake_case to match the API.
// Y/N flag fields are typed as `string`, not `boolean`.
// =============================================================================

// ─── Shared envelope & selection ─────────────────────────────────────────────

export interface ApiResponse<T> {
  status: number
  data: T
  msg: string
}

/**
 * Grouped option list returned by every /utilities/selections/* endpoint.
 * Each group has a label (e.g. account_type) and an `options` array of
 * `{label, value}` pairs ready to feed an `<el-select>`.
 */
export interface SelectionOption {
  label: string
  value: string
}

export interface SelectionGroup {
  label: string
  options: SelectionOption[]
}

export type SelectionItem = SelectionOption

// ─── Settings — Account ──────────────────────────────────────────────────────

export interface Account {
  id: number
  account_id: string
  name: string
  account_type: string
  fx_code: string
  is_calculate: string  // Y/N
  in_use: string        // Y/N
  discount: number
  memo?: string | null
  owner?: string | null
  account_index: number
}

export interface AccountCreate {
  account_id: string
  name: string
  account_type: string
  fx_code: string
  is_calculate?: string
  in_use?: string
  discount?: number
  memo?: string | null
  owner?: string | null
  account_index?: number
}

export type AccountUpdate = Partial<AccountCreate>

// ─── Settings — Alarm ────────────────────────────────────────────────────────

export interface Alarm {
  alarm_id: number
  alarm_type: string
  alarm_date: string    // YYYYMMDD
  content: string
  due_date?: string | null
}

export interface AlarmCreate {
  alarm_type: string
  alarm_date: string
  content: string
  due_date?: string | null
}

export type AlarmUpdate = Partial<AlarmCreate>

// ─── Settings — Budget ───────────────────────────────────────────────────────

export interface Budget {
  budget_year: string   // YYYY
  category_code: string
  category_name: string
  code_type: string
  expected01: number
  expected02: number
  expected03: number
  expected04: number
  expected05: number
  expected06: number
  expected07: number
  expected08: number
  expected09: number
  expected10: number
  expected11: number
  expected12: number
}

export type BudgetRead = Budget

// ─── Settings — CodeData (codes + sub-codes share schema) ────────────────────

export interface CodeData {
  code_id: string
  code_type: string
  name: string
  parent_id?: string | null
  code_group?: string | null
  code_group_name?: string | null
  in_use: string        // Y/N
  code_index: number
}

export interface CodeDataWithSub extends CodeData {
  sub_codes?: CodeData[]
}

export interface CodeDataCreate {
  code_id: string
  code_type: string
  name: string
  parent_id?: string | null
  code_group?: string | null
  code_group_name?: string | null
  in_use?: string
  code_index?: number
}

export type CodeDataUpdate = Partial<CodeDataCreate>

// ─── Settings — CreditCard ───────────────────────────────────────────────────

export interface CreditCard {
  credit_card_id: string
  card_name: string
  card_no?: string | null
  last_day?: number | null
  charge_day?: number | null
  limit_date?: number | null
  feedback_way?: string | null
  fx_code: string
  in_use: string        // Y/N
  credit_card_index: number
  note?: string | null
}

export interface CreditCardCreate {
  credit_card_id: string
  card_name: string
  card_no?: string | null
  last_day?: number | null
  charge_day?: number | null
  limit_date?: number | null
  feedback_way?: string | null
  fx_code: string
  in_use?: string
  credit_card_index?: number
  note?: string | null
}

export type CreditCardUpdate = Partial<CreditCardCreate>

// ─── Monthly Report — Journal ────────────────────────────────────────────────
// Polymorphic FK constraints (enforced server-side):
//   spend_way_table  ↔ spend_way_type  ('Account' ↔ 'account', 'Credit_Card' ↔ 'credit_card')
//   action_main_table is always 'Code_Data' for UI writes
//   action_sub_* fields are populated together OR all null (no partial)

export interface Journal {
  distinct_number: number
  vesting_month: string         // YYYYMM
  spend_date: string            // YYYYMMDD
  spend_way: string
  spend_way_type: string        // 'account' | 'credit_card'
  spend_way_table: string       // 'Account' | 'Credit_Card'
  action_main: string
  action_main_type: string
  action_main_table: string     // 'Code_Data'
  action_sub?: string | null
  action_sub_type?: string | null
  action_sub_table?: string | null
  spending: number
  invoice_number?: string | null
  note?: string | null
}

export interface JournalCreate {
  vesting_month: string
  spend_date: string
  spend_way: string
  spend_way_type: string
  spend_way_table: string
  action_main: string
  action_main_type: string
  action_main_table: string
  action_sub?: string | null
  action_sub_type?: string | null
  action_sub_table?: string | null
  spending: number
  invoice_number?: string | null
  note?: string | null
}

export type JournalUpdate = Partial<JournalCreate>

export interface JournalListResponse {
  items: Journal[]
  gain_loss: number
}

// ─── Monthly Report — Journal analytics ──────────────────────────────────────

export interface JournalExpenditureBudgetRow {
  action_main_type: string
  actual: number
  expected: number
  diff: number
  usage_rate: number
}

export interface JournalExpenditureBudget {
  rows: JournalExpenditureBudgetRow[]
}

export interface JournalRatioItem {
  name: string
  value: number
}

export interface JournalExpenditureRatio {
  outer: JournalRatioItem[]
  inner: JournalRatioItem[]
}

export interface JournalInvestRatio {
  items: JournalRatioItem[]
}

export interface JournalLiabilityItem {
  credit_card_id: string
  credit_card_name: string
  amount: number
}

export interface JournalLiability {
  items: JournalLiabilityItem[]
}

// ─── Monthly Report — Stock prices ───────────────────────────────────────────

export interface StockPriceEntry {
  stock_code: string
  stock_name: string
  close_price: number
}

export type StockPriceRead = StockPriceEntry

export interface StockPriceHistory {
  stock_code: string
  fetch_date: string            // YYYYMMDD
  open_price: number
  highest_price: number
  lowest_price: number
  close_price: number
}

// ─── Monthly Report — Settle ─────────────────────────────────────────────────

export interface SettleResult {
  vesting_month: string
  estate_rows: number
  insurance_rows: number
  loan_rows: number
  stock_rows: number
  account_rows: number
  credit_card_rows: number
}

// ─── Assets — common detail/journal shape ────────────────────────────────────

export interface AssetDetailBase {
  distinct_number: number
  excute_price: number
  excute_date: string           // YYYYMMDD
  memo?: string | null
}

// ─── Assets — Stock ──────────────────────────────────────────────────────────

export interface StockAsset {
  stock_id: string
  stock_code: string
  stock_name: string
  asset_id: string
  expected_spend: number
}

export interface StockAssetCreate {
  stock_id: string
  stock_code: string
  stock_name: string
  asset_id: string
  expected_spend: number
}

export type StockAssetUpdate = Partial<StockAssetCreate>

export interface StockJournal extends AssetDetailBase {
  stock_id: string
  excute_type: string           // 'buy' | 'sell' | 'stock' | 'cash'
  excute_amount: number
  account_id: string
  account_name: string
}

export interface StockJournalCreate {
  stock_id: string
  excute_type: string
  excute_amount: number
  excute_price: number
  excute_date: string
  account_id: string
  account_name: string
  memo?: string | null
}

export type StockJournalUpdate = Partial<StockJournalCreate>

// ─── Assets — Estate ─────────────────────────────────────────────────────────

export interface EstateAsset {
  estate_id: string
  estate_name: string
  estate_type: string
  estate_address: string
  asset_id: string
  obtain_date: string           // YYYYMMDD
  loan_id?: string | null
  estate_status: string         // 'idle' | 'live' | 'rent' | 'sold'
  memo?: string | null
}

export interface EstateAssetCreate {
  estate_id: string
  estate_name: string
  estate_type: string
  estate_address: string
  asset_id: string
  obtain_date: string
  loan_id?: string | null
  estate_status: string
  memo?: string | null
}

export type EstateAssetUpdate = Partial<EstateAssetCreate>

export interface EstateJournal extends AssetDetailBase {
  estate_id: string
  estate_excute_type: string    // 'tax' | 'fee' | 'insurance' | 'fix' | 'rent' | 'deposit'
}

export interface EstateJournalCreate {
  estate_id: string
  estate_excute_type: string
  excute_price: number
  excute_date: string
  memo?: string | null
}

export type EstateJournalUpdate = Partial<EstateJournalCreate>

// ─── Assets — Insurance ──────────────────────────────────────────────────────

export interface InsuranceAsset {
  insurance_id: string
  insurance_name: string
  asset_id: string
  in_account: string
  out_account: string
  start_date: string            // YYYYMMDD
  end_date: string              // YYYYMMDD
  pay_type: string
  pay_day: number
  expected_spend: number
  has_closed: string            // Y/N
}

export interface InsuranceAssetCreate {
  insurance_id: string
  insurance_name: string
  asset_id: string
  in_account: string
  out_account: string
  start_date: string
  end_date: string
  pay_type: string
  pay_day: number
  expected_spend: number
  has_closed: string
}

export type InsuranceAssetUpdate = Partial<InsuranceAssetCreate>

export interface InsuranceJournal extends AssetDetailBase {
  insurance_id: string
  insurance_excute_type: string // 'pay' | 'cash' | 'return' | 'expect'
}

export interface InsuranceJournalCreate {
  insurance_id: string
  insurance_excute_type: string
  excute_price: number
  excute_date: string
  memo?: string | null
}

export type InsuranceJournalUpdate = Partial<InsuranceJournalCreate>

// ─── Assets — Loan ───────────────────────────────────────────────────────────

export interface LoanAsset {
  loan_id: string
  loan_name: string
  loan_type: string
  account_id: string
  account_name: string
  interest_rate: number
  period: number
  apply_date: string            // YYYYMMDD
  grace_expire_date?: string | null
  pay_day: number
  amount: number
  repayed: number
  loan_index: number
}

export interface LoanAssetCreate {
  loan_id: string
  loan_name: string
  loan_type: string
  account_id: string
  account_name: string
  interest_rate: number
  period: number
  apply_date: string
  grace_expire_date?: string | null
  pay_day: number
  amount: number
  repayed: number
  loan_index: number
}

export type LoanAssetUpdate = Partial<LoanAssetCreate>

export interface LoanJournal extends AssetDetailBase {
  loan_id: string
  loan_excute_type: string      // 'principal' | 'interest' | 'increment' | 'fee'
}

export interface LoanJournalCreate {
  loan_id: string
  loan_excute_type: string
  excute_price: number
  excute_date: string
  memo?: string | null
}

export type LoanJournalUpdate = Partial<LoanJournalCreate>

export interface LoanSelection {
  loan_id: string
  loan_name: string
}

// ─── Assets — OtherAsset ─────────────────────────────────────────────────────

export interface OtherAsset {
  asset_id: string
  asset_name: string
  asset_type: string
  vesting_nation: string
  in_use: string                // Y/N
  asset_index: number
}

export interface OtherAssetCreate {
  asset_id: string
  asset_name: string
  asset_type: string
  vesting_nation: string
  in_use: string
  asset_index?: number
}

export type OtherAssetUpdate = Partial<OtherAssetCreate>

export interface OtherAssetItem {
  asset_type: string
}

// ─── Reports ─────────────────────────────────────────────────────────────────

export interface BalanceReportLine {
  name: string
  amount: number
  currency?: string
}

export interface BalanceReport {
  assets: {
    accounts: BalanceReportLine[]
    estates: BalanceReportLine[]
    insurances: BalanceReportLine[]
    stocks: BalanceReportLine[]
  }
  liabilities: {
    credit_cards: BalanceReportLine[]
    loans: BalanceReportLine[]
  }
  net_worth: number
}

export interface ExpenditureReportPoint {
  period: string                // YYYYMM or YYYY
  amount: number
}

export interface ExpenditureReport {
  type: string                  // 'monthly' | 'yearly'
  points: ExpenditureReportPoint[]
}

export interface AssetReportItem {
  type: string
  amount: number
  share: number
}

export interface AssetReport {
  total: number
  items: AssetReportItem[]
}

// ─── Dashboard ───────────────────────────────────────────────────────────────

export interface DashboardSummaryPoint {
  period: string                // YYYYMM
  value: number
}

export interface DashboardSummary {
  type: string
  points: DashboardSummaryPoint[]
}

export interface DashboardAlarm {
  date: string
  content: string
}

export interface DashboardBudgetLine {
  category: string
  planned: number
  actual: number
  usage_pct: number
}

export interface DashboardBudget {
  type: string                  // 'monthly' | 'yearly'
  period: string                // YYYYMM | YYYY
  lines: DashboardBudgetLine[]
  total_planned: number
  total_actual: number
}

export interface DashboardGift {
  owner: string
  amount: number
  rate: number
}

export interface TargetSetting {
  distinct_number: string
  target_year: string           // YYYY
  setting_value: number
  is_done: string               // Y/N
}

export interface TargetSettingCreate {
  distinct_number: string
  setting_value: number
  target_year?: string
  is_done?: string
}

export interface TargetSettingUpdate {
  target_year?: string
  setting_value?: number
  is_done?: string
}

// ─── Utilities — Selections (grouped responses) ──────────────────────────────
// All /utilities/selections/* endpoints return SelectionGroup[].
// These aliases exist so per-domain consumers can import a clearly-named type.

export type SelectionAccount = SelectionGroup
export type SelectionCode = SelectionGroup
export type SelectionCreditCard = SelectionGroup
export type SelectionInsurance = SelectionGroup
export type SelectionLoan = SelectionGroup

// ─── Utilities — Import ──────────────────────────────────────────────────────

export interface ImportResult {
  message: string
}
