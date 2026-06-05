<template>
  <div class="flex flex-col gap-8">
    <PageHeader title="年度支出" :subtitle="`${store.selectedYear} 年`">
      <template #actions>
        <el-date-picker
          v-model="selectedYearDate"
          type="year"
          placeholder="選擇年份"
          format="YYYY"
          :clearable="false"
        />
      </template>
    </PageHeader>

    <el-tabs v-model="activeType" @tab-change="handleTypeChange">
      <el-tab-pane label="月度" name="monthly" />
      <el-tab-pane label="年度" name="yearly" />
    </el-tabs>

    <el-skeleton v-if="store.incomeExpenseLoading" :rows="6" animated />
    <EmptyState v-else-if="!hasData" message="暫無收支資料" />
    <template v-else>
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        <MetricCard label="總收入" :amount="summary.total_income" />
        <MetricCard label="總支出" :amount="summary.total_expense" tone="rose" />
        <MetricCard
          label="淨結餘"
          :amount="summary.net"
          :tone="summary.net < 0 ? 'rose' : 'primary'"
        />
        <MetricCard
          label="儲蓄率"
          :amount="savingsRatePct"
          format="percent"
          signed
          :tone="summary.net < 0 ? 'rose' : 'primary'"
          tooltip="儲蓄率 = (收入 − 支出) / 收入"
        />
      </div>

      <section class="flex flex-col gap-4">
        <SectionHeader title="收支對比" />
        <BarChart :x-data="chart.xData" :series="chart.series" height="360px" />
      </section>

      <section class="flex flex-col gap-4">
        <SectionHeader title="支出結構" />
        <el-skeleton v-if="store.compositionLoading" :rows="5" animated />
        <EmptyState
          v-else-if="!composition || composition.categories.length === 0"
          message="暫無支出明細"
        />
        <template v-else>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <MetricCard
              label="固定支出（燒錢底線）"
              :amount="composition.fixed_total"
              :delta-label="`佔支出 ${fixedShare.toFixed(0)}%`"
              tooltip="每月幾乎跑不掉的底線：房租/房貸、保險、訂閱等"
            />
            <MetricCard
              label="變動支出"
              :amount="composition.floating_total"
              :delta-label="`佔支出 ${floatingShare.toFixed(0)}%`"
            />
            <MetricCard
              label="固定佔收入"
              :amount="fixedToIncomePct"
              format="percent"
              :tone="fixedToIncomePct > 50 ? 'rose' : 'primary'"
              tooltip="固定支出 ÷ 收入，你的「生存門檻」——越低代表收入掉了也越撐得住"
            />
          </div>
          <div class="rounded-xl border border-outline-variant bg-surface-container p-4">
            <el-table
              :data="expenditureTree"
              row-key="key"
              :tree-props="{ children: 'children' }"
              border
              style="width: 100%"
            >
              <el-table-column prop="label" label="項目" min-width="200">
                <template #default="{ row }">
                  <span>{{ row.label }}</span>
                  <el-tag
                    v-if="row.type"
                    :type="typeTagType(row.type)"
                    size="small"
                    effect="plain"
                    class="ml-2"
                  >
                    {{ typeLabel(row.type) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="金額" width="160" align="right">
                <template #default="{ row }">
                  <MoneyDisplay :amount="row.amount" currency="TWD" :positive="true" size="sm" />
                </template>
              </el-table-column>
              <el-table-column label="佔比" width="84" align="right">
                <template #default="{ row }">
                  <span
                    v-if="row.share != null"
                    class="tabular-nums text-sm text-on-surface-variant"
                  >
                    {{ row.share.toFixed(1) }}%
                  </span>
                  <span v-else class="text-on-surface-variant/40">—</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </template>
      </section>

      <section class="flex flex-col gap-4">
        <SectionHeader title="預算 vs 實際" />
        <el-skeleton v-if="store.budgetLoading" :rows="4" animated />
        <EmptyState
          v-else-if="!budget || budget.rows.length === 0"
          message="尚無預算資料"
        />
        <template v-else>
          <div class="flex flex-wrap items-center gap-x-8 gap-y-2 text-sm">
            <div class="flex items-center gap-2">
              <span class="text-on-surface-variant">年度預算</span>
              <MoneyDisplay :amount="budget.summary.total_expected" currency="TWD" size="sm" />
            </div>
            <div class="flex items-center gap-2">
              <span class="text-on-surface-variant">實際</span>
              <MoneyDisplay :amount="budget.summary.total_actual" currency="TWD" size="sm" />
              <span class="text-on-surface-variant/70 tabular-nums">
                {{ (budget.summary.usage_rate * 100).toFixed(0) }}%
              </span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-on-surface-variant">預估全年</span>
              <MoneyDisplay
                :amount="budget.summary.projected_total"
                currency="TWD"
                size="sm"
                :positive="budget.summary.projected_total <= budget.summary.total_expected"
              />
              <span
                v-if="budget.summary.elapsed_months > 0 && budget.summary.elapsed_months < 12"
                class="text-on-surface-variant/60 text-xs"
              >
                （依 {{ budget.summary.elapsed_months }} 個月進度推估）
              </span>
            </div>
          </div>
          <div class="rounded-xl border border-outline-variant bg-surface-container p-4">
            <el-table :data="budget.rows" row-key="code" border style="width: 100%">
              <el-table-column prop="name" label="類別" min-width="160">
                <template #default="{ row }">
                  <span>{{ row.name }}</span>
                  <el-tag
                    v-if="row.type"
                    :type="typeTagType(row.type)"
                    size="small"
                    effect="plain"
                    class="ml-2"
                  >
                    {{ typeLabel(row.type) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="預算" width="130" align="right">
                <template #default="{ row }">
                  <MoneyDisplay :amount="row.expected" currency="TWD" size="sm" />
                </template>
              </el-table-column>
              <el-table-column label="實際" width="130" align="right">
                <template #default="{ row }">
                  <MoneyDisplay :amount="row.actual" currency="TWD" size="sm" />
                </template>
              </el-table-column>
              <el-table-column label="差異" width="130" align="right">
                <template #default="{ row }">
                  <MoneyDisplay :amount="row.diff" currency="TWD" size="sm" :positive="row.diff <= 0" />
                </template>
              </el-table-column>
              <el-table-column label="達成率" min-width="170">
                <template #default="{ row }">
                  <div class="flex items-center gap-2">
                    <el-progress
                      :percentage="Math.min(Math.round(row.usage_rate * 100), 100)"
                      :status="usageStatus(row.usage_rate)"
                      :show-text="false"
                      :stroke-width="8"
                      class="flex-1"
                    />
                    <span
                      class="tabular-nums text-xs w-12 text-right"
                      :class="row.usage_rate > 1 ? 'text-secondary' : 'text-on-surface-variant'"
                    >
                      {{ (row.usage_rate * 100).toFixed(0) }}%
                    </span>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </template>
      </section>

      <section class="flex flex-col gap-4">
        <SectionHeader title="現金流量（生活／投資／債務）" />
        <el-skeleton v-if="store.cashFlowLoading" :rows="4" animated />
        <EmptyState v-else-if="!cashFlow" message="暫無現金流資料" />
        <template v-else>
          <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
            <MetricCard
              v-for="act in cashFlow.summary.activities"
              :key="act.key"
              :label="act.label"
              :amount="act.net"
              :tone="act.net < 0 ? 'rose' : 'primary'"
              :tooltip="cfTooltip(act)"
            />
            <MetricCard
              label="淨現金變化"
              :amount="cashFlow.summary.net_change"
              :tone="cashFlow.summary.net_change < 0 ? 'rose' : 'primary'"
            />
          </div>
          <div class="rounded-xl border border-outline-variant bg-surface-container p-4">
            <WaterfallChart :items="waterfallItems" total-label="淨變化" height="320px" />
          </div>
        </template>
      </section>

      <section class="flex flex-col gap-4">
        <SectionHeader title="年增率（YoY）" />
        <el-skeleton v-if="store.insightsLoading" :rows="3" animated />
        <EmptyState
          v-else-if="!insights || insights.yoy.length === 0"
          message="暫無年度比較資料"
        />
        <div v-else class="rounded-xl border border-outline-variant bg-surface-container p-4">
          <el-table :data="insights.yoy" row-key="code" border style="width: 100%">
            <el-table-column prop="name" label="類別" min-width="140">
              <template #default="{ row }">
                <span>{{ row.name }}</span>
                <el-tag
                  v-if="row.type"
                  :type="typeTagType(row.type)"
                  size="small"
                  effect="plain"
                  class="ml-2"
                >
                  {{ typeLabel(row.type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="今年" width="130" align="right">
              <template #default="{ row }">
                <MoneyDisplay :amount="row.current" currency="TWD" size="sm" />
              </template>
            </el-table-column>
            <el-table-column label="去年" width="130" align="right">
              <template #default="{ row }">
                <MoneyDisplay :amount="row.previous" currency="TWD" size="sm" />
              </template>
            </el-table-column>
            <el-table-column label="增減" width="130" align="right">
              <template #default="{ row }">
                <MoneyDisplay :amount="row.delta" currency="TWD" size="sm" :positive="row.delta <= 0" />
              </template>
            </el-table-column>
            <el-table-column label="年增率" width="100" align="right">
              <template #default="{ row }">
                <span class="tabular-nums text-sm" :class="yoyClass(row.delta)">
                  {{ yoyRateText(row) }}
                </span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </section>

      <section class="flex flex-col gap-4">
        <SectionHeader title="大額支出 Top 10" />
        <el-skeleton v-if="store.insightsLoading" :rows="3" animated />
        <EmptyState
          v-else-if="!insights || insights.largest.length === 0"
          message="暫無交易明細"
        />
        <div v-else class="rounded-xl border border-outline-variant bg-surface-container p-4">
          <el-table :data="insights.largest" border style="width: 100%">
            <el-table-column label="日期" width="120">
              <template #default="{ row }">{{ fmtDate(row.date) }}</template>
            </el-table-column>
            <el-table-column prop="category" label="類別" min-width="100" />
            <el-table-column label="金額" width="140" align="right">
              <template #default="{ row }">
                <MoneyDisplay :amount="row.amount" currency="TWD" size="sm" />
              </template>
            </el-table-column>
            <el-table-column prop="pay_way" label="支付方式" min-width="120" />
            <el-table-column label="備註" min-width="140">
              <template #default="{ row }">
                <span :class="row.note ? '' : 'text-on-surface-variant/40'">{{ row.note || '—' }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import SectionHeader from '@/components/ui/SectionHeader.vue'
import MetricCard from '@/components/ui/MetricCard.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import BarChart from '@/components/charts/BarChart.vue'
import WaterfallChart from '@/components/charts/WaterfallChart.vue'
import { useYearReportStore } from '@/stores/yearReport'
import { buildExpenditureTree } from './expenditureTree'
import type { CashFlowActivity } from '@/types/models'

const store = useYearReportStore()

const activeType = ref<'monthly' | 'yearly'>('monthly')
const selectedYearDate = ref<Date>(new Date(store.selectedYear, 0, 1))

function reload() {
  void store.fetchIncomeExpenseReport(activeType.value, store.selectedYear)
  void store.fetchExpenditureComposition(activeType.value, store.selectedYear)
  void store.fetchBudgetVariance(store.selectedYear)
  void store.fetchCashFlow(activeType.value, store.selectedYear)
  void store.fetchExpenseInsights(store.selectedYear)
}

function handleTypeChange() {
  reload()
}

watch(selectedYearDate, (date) => {
  if (!date) return
  const year = date.getFullYear()
  if (year !== store.selectedYear) {
    store.selectedYear = year
    reload()
  }
})

onMounted(reload)

const hasData = computed(
  () => !!store.incomeExpenseReport && store.incomeExpenseReport.points.length > 0,
)

const summary = computed(
  () =>
    store.incomeExpenseReport?.summary ?? {
      total_income: 0,
      total_expense: 0,
      net: 0,
      savings_rate: 0,
    },
)

const savingsRatePct = computed(() => summary.value.savings_rate * 100)

const chart = computed(() => {
  const report = store.incomeExpenseReport
  if (!report) return { xData: [], series: [] }
  return {
    xData: report.points.map((p) => p.period),
    series: [
      { name: '收入', data: report.points.map((p) => p.income) },
      // Fixed (the burn floor) at the bottom, variable stacked on top, so each
      // month's bar shows the locked-in floor vs the flexible part.
      { name: '固定支出', data: report.points.map((p) => p.fixed), stack: 'expense' },
      { name: '變動支出', data: report.points.map((p) => p.floating), stack: 'expense' },
      {
        name: '淨結餘',
        data: report.points.map((p) => p.net),
        type: 'line' as const,
      },
    ],
  }
})

const composition = computed(() => store.compositionReport)

const expenditureTree = computed(() =>
  store.compositionReport ? buildExpenditureTree(store.compositionReport) : [],
)

const fixedShare = computed(() => {
  const c = store.compositionReport
  return c && c.total ? (c.fixed_total / c.total) * 100 : 0
})

const floatingShare = computed(() => {
  const c = store.compositionReport
  return c && c.total ? (c.floating_total / c.total) * 100 : 0
})

// Burn-floor health: fixed expenses as a share of income — the "survival
// threshold". Fixed total comes from the composition report, income from the
// income-expense summary (both cover the same window).
const fixedToIncomePct = computed(() => {
  const income = store.incomeExpenseReport?.summary.total_income ?? 0
  const fixed = store.compositionReport?.fixed_total ?? 0
  return income ? (fixed / income) * 100 : 0
})

const budget = computed(() => store.budgetReport)

function usageStatus(rate: number): 'exception' | 'warning' | undefined {
  if (rate > 1) return 'exception'
  if (rate >= 0.9) return 'warning'
  return undefined
}

const cashFlow = computed(() => store.cashFlowReport)

const waterfallItems = computed(() =>
  (store.cashFlowReport?.summary.activities ?? []).map((a) => ({ name: a.label, value: a.net })),
)

function cfTooltip(act: CashFlowActivity): string {
  return act.items
    .map((i) => `${i.label}：${i.amount < 0 ? '−' : '+'}${Math.abs(i.amount).toLocaleString('en-US')}`)
    .join('<br/>')
}

const insights = computed(() => store.insightsReport)

function fmtDate(d: string): string {
  return d.length === 8 ? `${d.slice(0, 4)}/${d.slice(4, 6)}/${d.slice(6, 8)}` : d
}

function yoyRateText(row: { previous: number; yoy_rate: number }): string {
  if (!row.previous) return '—'
  const pct = row.yoy_rate * 100
  return `${pct >= 0 ? '+' : ''}${pct.toFixed(0)}%`
}

function yoyClass(delta: number): string {
  if (delta > 0) return 'text-secondary' // spending up — worth attention
  if (delta < 0) return 'text-positive' // spending down — good
  return 'text-on-surface-variant'
}

function typeLabel(t: string): string {
  return t.toLowerCase() === 'fixed' ? '固定' : '變動'
}

function typeTagType(t: string): 'info' | 'warning' {
  return t.toLowerCase() === 'fixed' ? 'info' : 'warning'
}
</script>
