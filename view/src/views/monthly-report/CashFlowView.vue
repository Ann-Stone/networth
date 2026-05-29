<template>
  <div class="flex flex-col gap-8">
    <PageHeader title="月度現金流" :subtitle="store.selectedMonth">
      <template #actions>
        <el-date-picker
          v-model="selectedMonthDate"
          type="month"
          placeholder="選擇月份"
          format="YYYY/MM"
          :clearable="false"
        />
        <el-button :icon="TrendCharts" @click="openStockPriceSnapshot">
          股價快照
        </el-button>
        <el-button type="warning" :loading="settling" @click="confirmSettle">
          執行月結
        </el-button>
      </template>
    </PageHeader>

    <section class="flex flex-col gap-4">
      <SectionHeader title="日記帳">
        <template #actions>
          <el-button type="primary" :icon="Plus" size="small" @click="openCreateJournal">
            新增
          </el-button>
        </template>
      </SectionHeader>
      <el-skeleton v-if="store.journalsLoading" :rows="5" animated />
      <EmptyState v-else-if="store.journals.length === 0" message="本月尚無日記帳資料" />
      <template v-else>
        <el-table :data="store.journals" stripe border style="width: 100%">
          <el-table-column prop="spend_date" label="日期" width="110" />
          <el-table-column label="帳戶" min-width="140">
            <template #default="{ row }">
              <span>{{ spendWayLabel(row) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="類別" width="140">
            <template #default="{ row }">
              <span>{{ actionMainLabel(row) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="子類" width="140">
            <template #default="{ row }">
              <span>{{ actionSubLabel(row) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="金額" width="180" align="right">
            <template #default="{ row }">
              <MoneyDisplay
                :amount="row.spending"
                :positive="row.spending > 0 ? true : row.spending < 0 ? false : null"
                size="sm"
              />
            </template>
          </el-table-column>
          <el-table-column prop="note" label="備註" min-width="160">
            <template #default="{ row }">
              <span>{{ row.note ?? '' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" align="center">
            <template #default="{ row }">
              <div class="flex items-center justify-center gap-2 whitespace-nowrap">
              <el-button size="small" :icon="Edit" @click="editJournal(row)">編輯</el-button>
              <el-popconfirm
                title="確定刪除這筆日記帳?"
                @confirm="handleDeleteJournal(row.distinct_number)"
              >
                <template #reference>
                  <el-button size="small" type="danger" :icon="Delete">刪除</el-button>
                </template>
              </el-popconfirm>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <div
          class="grid grid-cols-1 md:grid-cols-3 gap-4 rounded-xl border border-outline-variant bg-surface-container p-6"
        >
          <div class="flex flex-col gap-1">
            <p class="text-on-surface-variant text-xs uppercase tracking-wider">本月收入</p>
            <MoneyDisplay :amount="totalIncome" :positive="true" size="lg" />
          </div>
          <div class="flex flex-col gap-1">
            <p class="text-on-surface-variant text-xs uppercase tracking-wider">本月支出</p>
            <MoneyDisplay :amount="totalExpense" :positive="false" size="lg" />
          </div>
          <div class="flex flex-col gap-1">
            <p class="text-on-surface-variant text-xs uppercase tracking-wider">本月淨額</p>
            <MoneyDisplay
              :amount="netTotal"
              :positive="netTotal > 0 ? true : netTotal < 0 ? false : null"
              size="lg"
            />
          </div>
        </div>
      </template>
    </section>

    <section class="flex flex-col gap-4">
      <SectionHeader title="月度分析" />
      <el-tabs v-model="activeChartTab">
        <el-tab-pane label="收支預算" name="budget">
          <el-skeleton v-if="store.expenditureBudgetLoading" :rows="4" animated />
          <EmptyState
            v-else-if="!store.expenditureBudget || store.expenditureBudget.rows.length === 0"
            message="本月無預算資料"
          />
          <BarChart
            v-else
            :x-data="budgetChart.xData"
            :series="budgetChart.series"
            height="320px"
          />
        </el-tab-pane>
        <el-tab-pane label="支出比例" name="expenditureRatio">
          <el-skeleton v-if="store.expenditureRatioLoading" :rows="4" animated />
          <EmptyState
            v-else-if="!store.expenditureRatio || store.expenditureRatio.outer.length === 0"
            message="本月無支出資料"
          />
          <DonutChart v-else :data="store.expenditureRatio.outer" height="320px" />
        </el-tab-pane>
        <el-tab-pane label="投資比例" name="investRatio">
          <el-skeleton v-if="store.investRatioLoading" :rows="4" animated />
          <EmptyState
            v-else-if="!store.investRatio || store.investRatio.items.length === 0"
            message="本月無投資資料"
          />
          <DonutChart v-else :data="store.investRatio.items" height="320px" />
        </el-tab-pane>
        <el-tab-pane label="負債" name="liability">
          <el-skeleton v-if="store.liabilityLoading" :rows="4" animated />
          <EmptyState
            v-else-if="!store.liability || store.liability.items.length === 0"
            message="本月無信用卡負債資料"
          />
          <el-table v-else :data="store.liability.items" border>
            <el-table-column prop="credit_card_id" label="信用卡 ID" width="160" />
            <el-table-column prop="credit_card_name" label="名稱" min-width="160" />
            <el-table-column label="金額" width="200" align="right">
              <template #default="{ row }">
                <MoneyDisplay :amount="row.amount" :positive="false" size="sm" />
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </section>

    <el-dialog
      v-model="stockPriceSnapshotVisible"
      title="股價快照"
      width="640px"
    >
      <div class="flex justify-end mb-3">
        <el-button type="primary" :icon="Plus" size="small" @click="openStockPriceDialog">
          新增股價
        </el-button>
      </div>
      <el-skeleton v-if="store.stockPricesLoading" :rows="3" animated />
      <EmptyState
        v-else-if="store.stockPrices.length === 0"
        message="本月尚無股價快照"
      />
      <el-table v-else :data="store.stockPrices" border>
        <el-table-column prop="stock_code" label="代號" width="140" />
        <el-table-column prop="stock_name" label="名稱" min-width="200" />
        <el-table-column label="收盤價" width="180" align="right">
          <template #default="{ row }">
            <MoneyDisplay :amount="row.close_price" size="sm" />
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <FormDialog
      v-model="stockPriceDialogVisible"
      title="新增股價記錄"
      :loading="stockPriceSubmitting"
      width="520px"
      @submit="submitStockPrice"
    >
      <el-form ref="stockPriceFormRef" :model="stockPriceForm" :rules="stockPriceRules" label-width="120px">
        <el-form-item label="代號" prop="stock_code">
          <el-input v-model="stockPriceForm.stock_code" placeholder="例如 AAPL" />
        </el-form-item>
        <el-form-item label="日期" prop="fetch_date">
          <el-date-picker
            v-model="stockPriceFormDate"
            type="date"
            format="YYYY/MM/DD"
            :clearable="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="開盤" prop="open_price">
          <el-input-number v-model="stockPriceForm.open_price" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="最高" prop="highest_price">
          <el-input-number v-model="stockPriceForm.highest_price" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="最低" prop="lowest_price">
          <el-input-number v-model="stockPriceForm.lowest_price" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="收盤" prop="close_price">
          <el-input-number v-model="stockPriceForm.close_price" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="自動抓取">
          <el-switch v-model="stockPriceForm.trigger_yfinance" />
          <p class="text-xs text-on-surface-variant ml-3">
            開啟後會以 yfinance 收盤價覆寫
          </p>
        </el-form-item>
      </el-form>
    </FormDialog>

    <FormDialog
      v-model="journalDialogVisible"
      :title="formMode === 'create' ? '新增日記帳' : '編輯日記帳'"
      :loading="submitting"
      width="640px"
      @submit="submitJournal"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="日期" prop="spend_date">
          <el-date-picker
            v-model="formDateValue"
            type="date"
            placeholder="選擇日期"
            format="YYYY/MM/DD"
            :clearable="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="支付來源" prop="spend_way_type">
          <el-radio-group v-model="formData.spend_way_type" @change="onSpendWayTypeChange">
            <el-radio value="account">帳戶</el-radio>
            <el-radio value="credit_card">信用卡</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="帳戶/卡片" prop="spend_way">
          <el-select v-model="formData.spend_way" placeholder="選擇" filterable style="width: 100%">
            <el-option-group
              v-for="group in activeSpendWayGroups"
              :key="group.label"
              :label="translateGroupLabel(group.label)"
            >
              <el-option
                v-for="opt in group.options"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-option-group>
          </el-select>
        </el-form-item>
        <el-form-item label="主類別" prop="action_main">
          <el-select
            v-model="formData.action_main"
            placeholder="選擇主類別"
            filterable
            style="width: 100%"
            @change="onActionMainChange"
          >
            <el-option-group
              v-for="(group, idx) in mainSelectionGroups"
              :key="`${group.label}-${idx}`"
              :label="translateGroupLabel(group.label)"
            >
              <el-option
                v-for="opt in group.options"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
                :data-type="group.label"
              />
            </el-option-group>
          </el-select>
        </el-form-item>
        <el-form-item label="子類別">
          <el-select
            v-model="formData.action_sub"
            placeholder="(可選)"
            filterable
            clearable
            style="width: 100%"
            :disabled="!formData.action_main"
            @change="onActionSubChange"
          >
            <template
              v-for="(group, idx) in subSelectionGroups"
              :key="`${group.label}-${idx}`"
            >
              <template v-if="group.label === 'sub'">
                <el-option
                  v-for="opt in group.options"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </template>
              <el-option-group v-else :label="translateGroupLabel(group.label)">
                <el-option
                  v-for="opt in group.options"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                  :data-type="group.label"
                />
              </el-option-group>
            </template>
          </el-select>
        </el-form-item>
        <el-form-item label="金額" prop="spending">
          <el-input-number
            v-model="formData.spending"
            :precision="2"
            :step="100"
            controls-position="right"
            style="width: 100%"
          />
          <p class="text-xs text-on-surface-variant mt-1">
            正數 = 收入,負數 = 支出
          </p>
        </el-form-item>
        <el-form-item label="發票號碼">
          <el-input v-model="formData.invoice_number" placeholder="(可選)" />
        </el-form-item>
        <el-form-item label="備註">
          <el-input
            v-model="formData.note"
            type="textarea"
            :rows="2"
            :placeholder="notePlaceholder"
          />
        </el-form-item>

        <template v-if="shouldShowAssetSync && syncAssetType">
          <el-divider />
          <el-alert
            type="info"
            :closable="false"
            show-icon
            title="同步資產為單向操作"
            description="送出後會把這筆現金流同時寫入對應的資產明細。若需移除錯誤資料，請至『其他資產』頁面手動處理。"
            class="mb-4"
          />
          <el-form-item :label="syncHoldingLabel">
            <el-select
              v-model="syncHoldingId"
              :placeholder="`選擇${syncHoldingLabel}`"
              filterable
              style="width: 100%"
              :disabled="currentSyncSelectionGroups.length === 0"
            >
              <el-option-group
                v-for="group in currentSyncSelectionGroups"
                :key="group.label"
                :label="group.label"
              >
                <el-option
                  v-for="opt in group.options"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-option-group>
            </el-select>
            <p
              v-if="currentSyncSelectionGroups.length === 0"
              class="text-xs text-on-surface-variant mt-1"
            >
              {{ syncHoldingEmptyHint }}
            </p>
          </el-form-item>
          <StockDetailFormFields
            v-if="syncAssetType === 'stock'"
            v-model="syncStockDetail"
            mode="cashflow-sync"
          />
          <InsuranceDetailFormFields
            v-else-if="syncAssetType === 'insurance'"
            v-model="syncInsuranceDetail"
            mode="cashflow-sync"
          />
          <EstateDetailFormFields
            v-else-if="syncAssetType === 'estate'"
            v-model="syncEstateDetail"
            mode="cashflow-sync"
          />
        </template>
      </el-form>
    </FormDialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import dayjs from 'dayjs'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus, Edit, Delete, TrendCharts } from '@element-plus/icons-vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import SectionHeader from '@/components/ui/SectionHeader.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import FormDialog from '@/components/ui/FormDialog.vue'
import BarChart from '@/components/charts/BarChart.vue'
import DonutChart from '@/components/charts/DonutChart.vue'
import StockDetailFormFields, {
  type StockDetailFormState,
} from '@/components/forms/StockDetailFormFields.vue'
import InsuranceDetailFormFields, {
  type InsuranceDetailFormState,
} from '@/components/forms/InsuranceDetailFormFields.vue'
import EstateDetailFormFields, {
  type EstateDetailFormState,
} from '@/components/forms/EstateDetailFormFields.vue'
import { useCashFlowStore } from '@/stores/cashFlow'
import {
  createJournal,
  createJournalWithStockTransaction,
  createJournalWithInsuranceTransaction,
  createJournalWithEstateTransaction,
  updateJournal,
  updateJournalWithStockTransaction,
  updateJournalWithInsuranceTransaction,
  updateJournalWithEstateTransaction,
  deleteJournal,
  settleMonth,
  uploadStockPrices,
} from '@/api/cashFlow'
import {
  getAccountSelections,
  getCodeSelections,
  getCreditCardSelections,
  getEstateSelections,
  getInsuranceSelections,
  getLoanSelections,
  getOtherAssetTypeSelections,
  getStockSelections,
} from '@/api/utilities'
import { getCodesWithSub } from '@/api/setting'
import {
  FINANCIAL_BEHAVIORS,
  getFinancialBehaviorLabel,
} from '@/constants/financialBehavior'
import { getNotePlaceholder } from '@/constants/noteHints'
import { translateGroupLabel } from '@/constants/selectionLabels'
import type { CodeDataWithSub, Journal, JournalCreate, SelectionGroup } from '@/types/models'

const store = useCashFlowStore()

const selectedMonthDate = ref<Date>(dayjs(store.selectedMonth, 'YYYYMM').toDate())

watch(selectedMonthDate, (date) => {
  if (!date) return
  const next = dayjs(date).format('YYYYMM')
  if (next === store.selectedMonth) return
  store.selectedMonth = next
  store.fetchJournals()
})

const totalIncome = computed(() =>
  store.journals
    .filter((j) => j.spending > 0)
    .reduce((sum, j) => sum + j.spending, 0),
)

const totalExpense = computed(() =>
  store.journals
    .filter((j) => j.spending < 0)
    .reduce((sum, j) => sum + j.spending, 0),
)

const netTotal = computed(() => totalIncome.value + totalExpense.value)

// ─── Analytics tabs ────────────────────────────────────────────────────────
type ChartTab = 'budget' | 'expenditureRatio' | 'investRatio' | 'liability'
const activeChartTab = ref<ChartTab>('budget')
const loadedTabs = ref<Set<ChartTab>>(new Set())

async function loadChartTab(tab: ChartTab) {
  if (tab === 'budget') await store.fetchExpenditureBudget()
  else if (tab === 'expenditureRatio') await store.fetchExpenditureRatio()
  else if (tab === 'investRatio') await store.fetchInvestRatio()
  else if (tab === 'liability') await store.fetchLiability()
  loadedTabs.value.add(tab)
}

watch(activeChartTab, (tab) => {
  if (!loadedTabs.value.has(tab)) void loadChartTab(tab)
})

watch(
  () => store.selectedMonth,
  () => {
    loadedTabs.value.clear()
    void loadChartTab(activeChartTab.value)
  },
)

const budgetChart = computed(() => {
  const rows = store.expenditureBudget?.rows ?? []
  return {
    xData: rows.map((r) => r.action_main_type),
    series: [
      { name: '預算', data: rows.map((r) => r.expected) },
      { name: '實際', data: rows.map((r) => Math.abs(r.actual)) },
    ],
  }
})

// ─── Selection caches ──────────────────────────────────────────────────────
const accountGroups = ref<SelectionGroup[]>([])
const creditCardGroups = ref<SelectionGroup[]>([])
const loanGroups = ref<SelectionGroup[]>([])
const insuranceGroups = ref<SelectionGroup[]>([])
const codeGroups = ref<SelectionGroup[]>([])
const subCodeGroups = ref<SelectionGroup[]>([])
const otherAssetDbTypes = ref<Set<string>>(new Set())

// Maps Other_Asset.asset_type (DB-driven) → the capitalized form historically
// stored in Journal.action_sub plus the matching detail table. Kept inline
// rather than in a constants file: this is dispatch glue, not domain data.
const OTHER_ASSET_DISPATCH: Record<
  string,
  { subKey: string; subTable: string; label: string }
> = {
  stock:     { subKey: 'Stock',     subTable: 'Stock_Detail',     label: '股票' },
  insurance: { subKey: 'Insurance', subTable: 'Insurance_Journal', label: '保險' },
  estate:    { subKey: 'Estate',    subTable: 'Estate_Journal',   label: '房地產' },
}
// Composite endpoints exist for all three asset types (CFL-A01). Filter
// narrows the sub dropdown to what we can actually round-trip atomically.
const SUPPORTED_SYNC_ASSET_TYPES: readonly string[] = ['stock', 'insurance', 'estate']
const OTHER_ASSET_SUB_TABLES = new Set(
  Object.values(OTHER_ASSET_DISPATCH).map((m) => m.subTable),
)

const financialBehaviorGroup: SelectionGroup = {
  label: '金融行為',
  options: FINANCIAL_BEHAVIORS.map((b) => ({ value: b.key, label: b.label })),
}

const mainSelectionGroups = computed<SelectionGroup[]>(() => [
  ...codeGroups.value,
  financialBehaviorGroup,
])

const otherAssetSubGroup = computed<SelectionGroup | null>(() => {
  const options = Object.entries(OTHER_ASSET_DISPATCH)
    .filter(([dbType]) => otherAssetDbTypes.value.has(dbType))
    .filter(([dbType]) => SUPPORTED_SYNC_ASSET_TYPES.includes(dbType))
    .map(([, m]) => ({ value: m.subKey, label: m.label }))
  if (options.length === 0) return null
  return { label: 'Other_Asset', options }
})

const subSelectionGroups = computed<SelectionGroup[]>(() => {
  const behavior = FINANCIAL_BEHAVIORS.find((b) => b.key === formData.value.action_main)
  if (!behavior) return subCodeGroups.value
  if (behavior.table === 'Account') {
    // Transfer → accounts + Other_Asset (Stock/Insurance/Estate, filtered by
    // what's set up in DB and what the backend can sync atomically).
    return otherAssetSubGroup.value
      ? [...accountGroups.value, otherAssetSubGroup.value]
      : accountGroups.value
  }
  if (behavior.table === 'Credit_Card') return creditCardGroups.value
  if (behavior.table === 'Loan') return loanGroups.value
  if (behavior.table === 'Insurance') return insuranceGroups.value
  return []
})

const notePlaceholder = computed<string>(() => {
  const main = formData.value.action_main
  if (!main) return '(可選)'
  if (FINANCIAL_BEHAVIORS.some((b) => b.key === main)) {
    return getNotePlaceholder(main)
  }
  const mainName = codeNameMap.value.get(main)
  if (!mainName) return '(可選)'
  const sub = formData.value.action_sub
  const subName = sub ? codeNameMap.value.get(sub) : undefined
  return getNotePlaceholder(mainName, subName ?? undefined)
})

const activeSpendWayGroups = computed(() =>
  formData.value.spend_way_type === 'credit_card' ? creditCardGroups.value : accountGroups.value,
)

const codeTree = ref<CodeDataWithSub[]>([])

const codeNameMap = computed(() => {
  const map = new Map<string, string>()
  for (const c of codeTree.value) {
    map.set(c.code_id, c.name)
    for (const sub of c.sub_codes ?? []) map.set(sub.code_id, sub.name)
  }
  return map
})

function codeName(id?: string | null): string {
  if (!id) return '-'
  return codeNameMap.value.get(id) ?? id
}

function isCodeTable(table?: string | null): boolean {
  return table === 'Code_Data' || table === 'Code'
}

function actionMainLabel(row: Journal): string {
  if (!row.action_main || row.action_main === 'No') return '-'
  if (isCodeTable(row.action_main_table)) return codeName(row.action_main)
  const behavior = getFinancialBehaviorLabel(row.action_main, row.action_main_table)
  return behavior ?? row.action_main
}

function actionSubLabel(row: Journal): string {
  if (!row.action_sub || row.action_sub === 'No') return '-'
  if (isCodeTable(row.action_sub_table)) return codeName(row.action_sub)
  const table = row.action_sub_table ?? ''
  if (table === 'Account' || table === 'Credit_Card') {
    return spendWayLabelMap.value.get(`${table}:${row.action_sub}`) ?? row.action_sub
  }
  if (table === 'Stock_Detail') return row.action_sub === 'Stock' ? '股票' : row.action_sub
  if (table === 'Insurance_Journal') return '保險'
  if (table === 'Estate_Journal') return '房地產'
  return row.action_sub
}

async function loadCodeTree() {
  if (codeTree.value.length === 0) {
    codeTree.value = await getCodesWithSub()
  }
}

const spendWayLabelMap = computed(() => {
  const map = new Map<string, string>()
  const collect = (groups: SelectionGroup[], table: 'Account' | 'Credit_Card') => {
    for (const group of groups) {
      for (const opt of group.options) {
        map.set(`${table}:${opt.value}`, opt.label)
      }
    }
  }
  collect(accountGroups.value, 'Account')
  collect(creditCardGroups.value, 'Credit_Card')
  return map
})

function spendWayLabel(row: Journal): string {
  const key = `${row.spend_way_table}:${row.spend_way}`
  return spendWayLabelMap.value.get(key) ?? row.spend_way
}

async function loadSpendWaySelections() {
  if (accountGroups.value.length === 0) {
    accountGroups.value = await getAccountSelections()
  }
  if (creditCardGroups.value.length === 0) {
    creditCardGroups.value = await getCreditCardSelections()
  }
}

async function loadLoanSelections() {
  if (loanGroups.value.length === 0) {
    try {
      loanGroups.value = await getLoanSelections()
    } catch {
      loanGroups.value = []
    }
  }
}

async function loadInsuranceSelections() {
  if (insuranceGroups.value.length === 0) {
    try {
      insuranceGroups.value = await getInsuranceSelections()
    } catch {
      insuranceGroups.value = []
    }
  }
}

async function loadCodeSelections() {
  if (codeGroups.value.length === 0) {
    codeGroups.value = await getCodeSelections()
  }
}

async function loadSubCodeSelections(parent: string) {
  if (!parent) {
    subCodeGroups.value = []
    return
  }
  try {
    subCodeGroups.value = await getCodeSelections(parent)
  } catch {
    subCodeGroups.value = []
  }
}

// ─── Form state ────────────────────────────────────────────────────────────
type JournalFormState = JournalCreate & { distinct_number?: number; action_sub?: string | null }

function emptyForm(): JournalFormState {
  return {
    vesting_month: store.selectedMonth,
    spend_date: dayjs().format('YYYYMMDD'),
    spend_way: '',
    spend_way_type: 'account',
    spend_way_table: 'Account',
    action_main: '',
    action_main_type: '',
    action_main_table: 'Code_Data',
    action_sub: null,
    action_sub_type: null,
    action_sub_table: null,
    spending: 0,
    invoice_number: null,
    note: null,
  }
}

const journalDialogVisible = ref(false)
const formMode = ref<'create' | 'edit'>('create')
const formData = ref<JournalFormState>(emptyForm())
const formRef = ref<FormInstance>()
const submitting = ref(false)

const formDateValue = computed<Date | null>({
  get: () => (formData.value.spend_date ? dayjs(formData.value.spend_date, 'YYYYMMDD').toDate() : null),
  set: (date) => {
    formData.value.spend_date = date ? dayjs(date).format('YYYYMMDD') : ''
  },
})

const formRules: FormRules = {
  spend_date: [{ required: true, message: '請選擇日期', trigger: 'change' }],
  spend_way: [{ required: true, message: '請選擇帳戶/卡片', trigger: 'change' }],
  spend_way_type: [{ required: true, message: '請選擇支付來源類型', trigger: 'change' }],
  action_main: [{ required: true, message: '請選擇主類別', trigger: 'change' }],
  spending: [{ required: true, message: '請輸入金額', trigger: 'blur' }],
}

// ─── Sync-to-asset (Stock / Insurance / Estate) ───────────────────────────
// The user triggers this implicitly by picking an "其他資產" sub-category
// under Transfer (legacy 轉帳→股票 semantics). When triggered, the form
// expands to capture the holding + type, then submits via the matching
// composite endpoint so Journal + <Asset>_Detail land atomically.
type SyncAssetType = 'stock' | 'insurance' | 'estate'

const originalActionSub = ref<string | null>(null) // captured on dialog open
const syncHoldingId = ref('') // selected stock_id / insurance_id / estate_id

// Which composite flow the current sub-category maps to (null = plain journal).
const syncAssetType = computed<SyncAssetType | null>(() => {
  switch (formData.value.action_sub_table) {
    case 'Stock_Detail':
      return 'stock'
    case 'Insurance_Journal':
      return 'insurance'
    case 'Estate_Journal':
      return 'estate'
    default:
      return null
  }
})

const stockSelectionGroups = ref<SelectionGroup[]>([])
const estateSelectionGroups = ref<SelectionGroup[]>([])
// Insurance reuses `insuranceGroups` (already loaded for the 保險 main category).

const currentSyncSelectionGroups = computed<SelectionGroup[]>(() => {
  switch (syncAssetType.value) {
    case 'stock':
      return stockSelectionGroups.value
    case 'insurance':
      return insuranceGroups.value
    case 'estate':
      return estateSelectionGroups.value
    default:
      return []
  }
})

const SYNC_HOLDING_LABEL: Record<SyncAssetType, string> = {
  stock: '持股',
  insurance: '保單',
  estate: '房產',
}
const SYNC_HOLDING_EMPTY_HINT: Record<SyncAssetType, string> = {
  stock: '尚無持股，請先到「資產負債管理 → 股票」建立',
  insurance: '尚無保單，請先到「資產負債管理 → 保險」建立',
  estate: '尚無房產，請先到「資產負債管理 → 房產」建立',
}
const syncHoldingLabel = computed(() =>
  syncAssetType.value ? SYNC_HOLDING_LABEL[syncAssetType.value] : '',
)
const syncHoldingEmptyHint = computed(() =>
  syncAssetType.value ? SYNC_HOLDING_EMPTY_HINT[syncAssetType.value] : '',
)

function emptyStockSyncDetail(): StockDetailFormState {
  return {
    stock_id: '',
    excute_type: 'buy',
    excute_amount: 0,
    excute_price: 0,
    excute_date: '',
    account_id: '',
    account_name: '',
    memo: null,
  }
}
const syncStockDetail = ref<StockDetailFormState>(emptyStockSyncDetail())

function emptyInsuranceSyncDetail(): InsuranceDetailFormState {
  return {
    insurance_id: '',
    insurance_excute_type: 'pay',
    excute_price: 0,
    excute_date: '',
    memo: null,
  }
}
const syncInsuranceDetail = ref<InsuranceDetailFormState>(emptyInsuranceSyncDetail())

function emptyEstateSyncDetail(): EstateDetailFormState {
  return {
    estate_id: '',
    estate_excute_type: 'tax',
    excute_price: 0,
    excute_date: '',
    memo: null,
  }
}
const syncEstateDetail = ref<EstateDetailFormState>(emptyEstateSyncDetail())

// Noun used in the success toast ("已同步到<noun>明細").
const SYNC_ASSET_NOUN: Record<SyncAssetType, string> = {
  stock: '股票',
  insurance: '保險',
  estate: '房地產',
}

// Composite detail payloads. Each type only carries the user-chosen fields;
// the backend fills excute_price (= journal.spending, sign preserved), date
// and memo from the journal.
function stockDetailBody() {
  return {
    stock_id: syncHoldingId.value,
    excute_type: syncStockDetail.value.excute_type as 'buy' | 'sell' | 'stock' | 'cash',
    excute_amount: Number(syncStockDetail.value.excute_amount ?? 0),
  }
}
function insuranceDetailBody() {
  return {
    insurance_id: syncHoldingId.value,
    insurance_excute_type: syncInsuranceDetail.value.insurance_excute_type as
      | 'pay' | 'cash' | 'return' | 'expect',
  }
}
function estateDetailBody() {
  return {
    estate_id: syncHoldingId.value,
    estate_excute_type: syncEstateDetail.value.estate_excute_type as
      | 'tax' | 'fee' | 'insurance' | 'fix' | 'rent' | 'deposit',
  }
}

async function loadStockSelections() {
  if (stockSelectionGroups.value.length > 0) return
  try {
    stockSelectionGroups.value = await getStockSelections()
  } catch {
    stockSelectionGroups.value = []
  }
}

async function loadEstateSelections() {
  if (estateSelectionGroups.value.length > 0) return
  try {
    estateSelectionGroups.value = await getEstateSelections()
  } catch {
    estateSelectionGroups.value = []
  }
}

// Lazy-load the selection list for whichever asset type the sync panel needs.
function loadSyncSelections(type: SyncAssetType) {
  if (type === 'stock') void loadStockSelections()
  else if (type === 'insurance') void loadInsuranceSelections()
  else if (type === 'estate') void loadEstateSelections()
}

async function loadOtherAssetTypes() {
  if (otherAssetDbTypes.value.size > 0) return
  try {
    const groups = await getOtherAssetTypeSelections()
    // Normalize to lowercase: legacy data has mixed casing ("Stock" vs "stock"),
    // dispatch map keys are lowercase for consistency.
    const values = groups[0]?.options.map((o) => o.value.toLowerCase()) ?? []
    otherAssetDbTypes.value = new Set(values)
  } catch {
    otherAssetDbTypes.value = new Set()
  }
}

function resetSyncState() {
  syncHoldingId.value = ''
  syncStockDetail.value = emptyStockSyncDetail()
  syncInsuranceDetail.value = emptyInsuranceSyncDetail()
  syncEstateDetail.value = emptyEstateSyncDetail()
}

// Sync panel opens when the user has picked an "其他資產" sub-category and
// the edit-mode guard allows it. Edit-mode guard: only when the original
// sub was empty — protects existing detail rows from being silently doubled.
const shouldShowAssetSync = computed<boolean>(() => {
  const table = formData.value.action_sub_table
  if (!table || !OTHER_ASSET_SUB_TABLES.has(table)) return false
  if (formMode.value === 'create') return true
  return !originalActionSub.value
})

// Lazy-load the holding dropdown whenever the sync panel is visible and the
// asset type changes (e.g. switching the sub-category from 股票 to 保險). Reset
// the picked holding so a stale id from another type can't leak through.
watch([shouldShowAssetSync, syncAssetType], ([visible, type], [, prevType]) => {
  if (type !== prevType) syncHoldingId.value = ''
  if (visible && type) loadSyncSelections(type)
})

function findCodeType(groups: SelectionGroup[], value: string): string {
  for (const group of groups) {
    if (group.options.some((opt) => opt.value === value)) return group.label
  }
  return ''
}

function onSpendWayTypeChange(value: string | number | boolean | undefined) {
  const v = String(value)
  formData.value.spend_way = ''
  formData.value.spend_way_table = v === 'credit_card' ? 'Credit_Card' : 'Account'
}

async function onActionMainChange(value: string | number | boolean | undefined) {
  const v = value ? String(value) : ''
  formData.value.action_sub = null
  formData.value.action_sub_type = null
  formData.value.action_sub_table = null
  const behavior = FINANCIAL_BEHAVIORS.find((b) => b.key === v)
  if (behavior) {
    formData.value.action_main_type = behavior.key
    formData.value.action_main_table = behavior.table
    subCodeGroups.value = []
    if (behavior.table === 'Loan') await loadLoanSelections()
    if (behavior.table === 'Insurance') await loadInsuranceSelections()
  } else {
    formData.value.action_main_type = findCodeType(codeGroups.value, v)
    formData.value.action_main_table = 'Code_Data'
    await loadSubCodeSelections(v)
  }
}

function onActionSubChange(value: string | number | boolean | undefined) {
  const v = value ? String(value) : ''
  if (!v) {
    formData.value.action_sub = null
    formData.value.action_sub_type = null
    formData.value.action_sub_table = null
    return
  }
  formData.value.action_sub = v
  const behavior = FINANCIAL_BEHAVIORS.find((b) => b.key === formData.value.action_main)
  // Transfer → Other_Asset (Stock / Insurance / Estate): dispatch matches the
  // legacy account-book-view convention so existing rows keep rendering.
  const otherAssetEntry = Object.values(OTHER_ASSET_DISPATCH).find((m) => m.subKey === v)
  if (behavior?.table === 'Account' && otherAssetEntry) {
    formData.value.action_sub_table = otherAssetEntry.subTable
    formData.value.action_sub_type = 'Asset'
    return
  }
  if (behavior) {
    formData.value.action_sub_table = behavior.table
    formData.value.action_sub_type = findCodeType(subSelectionGroups.value, v)
  } else {
    formData.value.action_sub_table = 'Code_Data'
    formData.value.action_sub_type = findCodeType(subCodeGroups.value, v)
  }
}

async function openCreateJournal() {
  formMode.value = 'create'
  formData.value = emptyForm()
  subCodeGroups.value = []
  originalActionSub.value = null
  resetSyncState()
  journalDialogVisible.value = true
  await Promise.all([
    loadSpendWaySelections(),
    loadCodeSelections(),
    loadOtherAssetTypes(),
  ])
}

async function editJournal(row: Journal) {
  formMode.value = 'edit'
  formData.value = {
    distinct_number: row.distinct_number,
    vesting_month: row.vesting_month,
    spend_date: row.spend_date,
    spend_way: row.spend_way,
    spend_way_type: row.spend_way_type,
    spend_way_table: row.spend_way_table,
    action_main: row.action_main,
    action_main_type: row.action_main_type,
    action_main_table: row.action_main_table,
    action_sub: row.action_sub ?? null,
    action_sub_type: row.action_sub_type ?? null,
    action_sub_table: row.action_sub_table ?? null,
    spending: row.spending,
    invoice_number: row.invoice_number ?? null,
    note: row.note ?? null,
  }
  originalActionSub.value = row.action_sub ?? null
  resetSyncState()
  journalDialogVisible.value = true
  await Promise.all([
    loadSpendWaySelections(),
    loadCodeSelections(),
    loadOtherAssetTypes(),
  ])
  const behavior = FINANCIAL_BEHAVIORS.find((b) => b.key === row.action_main)
  if (behavior) {
    if (behavior.table === 'Loan') await loadLoanSelections()
    if (behavior.table === 'Insurance') await loadInsuranceSelections()
  } else if (row.action_main) {
    await loadSubCodeSelections(row.action_main)
  }
}

async function submitJournal() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const payload: JournalCreate = {
      vesting_month: formData.value.vesting_month,
      spend_date: formData.value.spend_date,
      spend_way: formData.value.spend_way,
      spend_way_type: formData.value.spend_way_type,
      spend_way_table: formData.value.spend_way_table,
      action_main: formData.value.action_main,
      action_main_type: formData.value.action_main_type,
      action_main_table: formData.value.action_main_table,
      action_sub: formData.value.action_sub ?? null,
      action_sub_type: formData.value.action_sub_type ?? null,
      action_sub_table: formData.value.action_sub_table ?? null,
      spending: Number(formData.value.spending ?? 0),
      invoice_number: formData.value.invoice_number || null,
      note: formData.value.note || null,
    }
    const syncType = shouldShowAssetSync.value ? syncAssetType.value : null
    if (syncType && !syncHoldingId.value) {
      ElMessage.error(`請選擇${syncHoldingLabel.value}`)
      return
    }

    if (formMode.value === 'create') {
      switch (syncType) {
        case 'stock':
          await createJournalWithStockTransaction({ journal: payload, stock_detail: stockDetailBody() })
          break
        case 'insurance':
          await createJournalWithInsuranceTransaction({ journal: payload, insurance_detail: insuranceDetailBody() })
          break
        case 'estate':
          await createJournalWithEstateTransaction({ journal: payload, estate_detail: estateDetailBody() })
          break
        default:
          await createJournal(payload)
      }
      ElMessage.success(syncType ? `新增成功（已同步到${SYNC_ASSET_NOUN[syncType]}明細）` : '新增成功')
    } else if (formData.value.distinct_number !== undefined) {
      const id = formData.value.distinct_number
      switch (syncType) {
        case 'stock':
          await updateJournalWithStockTransaction(id, { journal: payload, stock_detail: stockDetailBody() })
          break
        case 'insurance':
          await updateJournalWithInsuranceTransaction(id, { journal: payload, insurance_detail: insuranceDetailBody() })
          break
        case 'estate':
          await updateJournalWithEstateTransaction(id, { journal: payload, estate_detail: estateDetailBody() })
          break
        default:
          await updateJournal(id, payload)
      }
      ElMessage.success(syncType ? `更新成功（已同步到${SYNC_ASSET_NOUN[syncType]}明細）` : '更新成功')
    }
    journalDialogVisible.value = false
    await store.fetchJournals()
  } finally {
    submitting.value = false
  }
}

async function handleDeleteJournal(id: number) {
  await deleteJournal(id)
  ElMessage.success('已刪除')
  await store.fetchJournals()
}

// ─── Settle ────────────────────────────────────────────────────────────────
const settling = ref(false)

async function confirmSettle() {
  try {
    await ElMessageBox.confirm(
      `將執行 ${store.selectedMonth} 月結,會覆蓋既有快照,確定?`,
      '確認月結',
      { type: 'warning', confirmButtonText: '執行', cancelButtonText: '取消' },
    )
  } catch {
    return
  }
  settling.value = true
  try {
    const result = await settleMonth(store.selectedMonth)
    ElMessage.success(`月結完成 (帳戶 ${result.account_rows} / 信用卡 ${result.credit_card_rows})`)
    await store.fetchJournals()
    loadedTabs.value.clear()
    void loadChartTab(activeChartTab.value)
  } finally {
    settling.value = false
  }
}

// ─── Stock prices ──────────────────────────────────────────────────────────
const stockPriceSnapshotVisible = ref(false)
const stockPriceDialogVisible = ref(false)

function openStockPriceSnapshot() {
  stockPriceSnapshotVisible.value = true
}
const stockPriceSubmitting = ref(false)
const stockPriceFormRef = ref<FormInstance>()

interface StockPriceFormState {
  stock_code: string
  fetch_date: string
  open_price: number
  highest_price: number
  lowest_price: number
  close_price: number
  trigger_yfinance: boolean
}

function emptyStockPriceForm(): StockPriceFormState {
  return {
    stock_code: '',
    fetch_date: dayjs().format('YYYYMMDD'),
    open_price: 0,
    highest_price: 0,
    lowest_price: 0,
    close_price: 0,
    trigger_yfinance: false,
  }
}

const stockPriceForm = ref<StockPriceFormState>(emptyStockPriceForm())

const stockPriceFormDate = computed<Date | null>({
  get: () =>
    stockPriceForm.value.fetch_date
      ? dayjs(stockPriceForm.value.fetch_date, 'YYYYMMDD').toDate()
      : null,
  set: (date) => {
    stockPriceForm.value.fetch_date = date ? dayjs(date).format('YYYYMMDD') : ''
  },
})

const stockPriceRules: FormRules = {
  stock_code: [{ required: true, message: '請輸入代號', trigger: 'blur' }],
  fetch_date: [{ required: true, message: '請選擇日期', trigger: 'change' }],
  open_price: [{ required: true, message: '請輸入開盤價', trigger: 'blur' }],
  highest_price: [{ required: true, message: '請輸入最高價', trigger: 'blur' }],
  lowest_price: [{ required: true, message: '請輸入最低價', trigger: 'blur' }],
  close_price: [{ required: true, message: '請輸入收盤價', trigger: 'blur' }],
}

function openStockPriceDialog() {
  stockPriceForm.value = emptyStockPriceForm()
  stockPriceDialogVisible.value = true
}

async function submitStockPrice() {
  if (!stockPriceFormRef.value) return
  const valid = await stockPriceFormRef.value.validate().catch(() => false)
  if (!valid) return
  stockPriceSubmitting.value = true
  try {
    await uploadStockPrices({ ...stockPriceForm.value })
    ElMessage.success('股價已新增')
    stockPriceDialogVisible.value = false
    await store.fetchStockPrices()
  } finally {
    stockPriceSubmitting.value = false
  }
}

watch(
  () => store.selectedMonth,
  () => {
    void store.fetchStockPrices()
  },
)

onMounted(() => {
  store.fetchJournals()
  store.fetchStockPrices()
  void loadSpendWaySelections()
  void loadCodeTree()
  void loadChartTab(activeChartTab.value)
})
</script>
