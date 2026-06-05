<template>
  <div class="flex flex-col gap-8">
    <PageHeader title="現金流量表" :subtitle="`${store.selectedYear} 年 · 生活 / 投資 / 債務`">
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

    <el-skeleton v-if="store.cashFlowLoading" :rows="6" animated />
    <EmptyState v-else-if="!hasData" message="暫無現金流資料" />
    <template v-else>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="生活淨額"
          :amount="nets.operating"
          :tone="nets.operating < 0 ? 'rose' : 'primary'"
          tooltip="收入 − 生活支出 − 貸款利息"
        />
        <MetricCard
          label="投資淨額"
          :amount="nets.investing"
          :tone="nets.investing < 0 ? 'rose' : 'primary'"
          tooltip="投資買賣淨額（買入為負、賣出為正）"
        />
        <MetricCard
          label="債務淨額"
          :amount="nets.financing"
          :tone="nets.financing < 0 ? 'rose' : 'primary'"
          tooltip="新增借款 − 償還本金"
        />
        <MetricCard
          label="現金淨變動"
          :amount="summary.net_change"
          :tone="summary.net_change < 0 ? 'rose' : 'primary'"
          tooltip="生活 ＋ 投資 ＋ 債務"
        />
      </div>

      <section class="flex flex-col gap-4">
        <SectionHeader title="現金流構成（生活 → 投資 → 債務）" />
        <div class="rounded-xl border border-outline-variant bg-surface-container p-4">
          <WaterfallChart :items="waterfallItems" total-label="現金淨變動" height="320px" />
        </div>
      </section>

      <section class="flex flex-col gap-4">
        <SectionHeader title="逐期現金流" />
        <BarChart :x-data="chart.xData" :series="chart.series" height="360px" />
      </section>

      <section class="flex flex-col gap-4">
        <SectionHeader title="現金流明細" />
        <p class="text-on-surface-variant/70 text-sm -mt-2">
          自轉帳已排除；信用卡支出於消費當月計入一次。投資買賣與債務本金屬現金流量，與「損益表」的損益口徑刻意不同——並非錯誤。
        </p>
        <div class="rounded-xl border border-outline-variant bg-surface-container p-4">
          <el-table
            :data="breakdownTree"
            row-key="key"
            :tree-props="{ children: 'children' }"
            default-expand-all
            border
            style="width: 100%"
          >
            <el-table-column prop="label" label="項目" min-width="220" />
            <el-table-column label="金額" width="200" align="right">
              <template #default="{ row }">
                <MoneyDisplay
                  :amount="row.amount"
                  currency="TWD"
                  :positive="row.amount >= 0"
                  size="sm"
                />
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

const store = useYearReportStore()

const activeType = ref<'monthly' | 'yearly'>('monthly')
const selectedYearDate = ref<Date>(new Date(store.selectedYear, 0, 1))

function reload() {
  void store.fetchCashFlow(activeType.value, store.selectedYear)
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
  () => !!store.cashFlowReport && store.cashFlowReport.points.length > 0,
)

const summary = computed(
  () => store.cashFlowReport?.summary ?? { activities: [], net_change: 0 },
)

// Signed net per activity, keyed by 'operating' | 'investing' | 'financing'.
const nets = computed(() => {
  const m = { operating: 0, investing: 0, financing: 0 } as Record<string, number>
  for (const a of summary.value.activities) m[a.key] = a.net
  return m
})

const chart = computed(() => {
  const report = store.cashFlowReport
  if (!report) return { xData: [] as string[], series: [] }
  return {
    xData: report.points.map((p) => p.period),
    series: [
      // 生活 / 投資 / 債務 stack into 現金淨變動; the line traces the total.
      { name: '生活', data: report.points.map((p) => p.operating), stack: 'cf' },
      { name: '投資', data: report.points.map((p) => p.investing), stack: 'cf' },
      { name: '債務', data: report.points.map((p) => p.financing), stack: 'cf' },
      {
        name: '現金淨變動',
        data: report.points.map((p) => p.net_change),
        type: 'line' as const,
      },
    ],
  }
})

const waterfallItems = computed(() => [
  { name: '生活', value: nets.value.operating },
  { name: '投資', value: nets.value.investing },
  { name: '債務', value: nets.value.financing },
])

const breakdownTree = computed(() => {
  const s = summary.value
  return [
    ...s.activities.map((a) => ({
      key: a.key,
      label: a.label,
      amount: a.net,
      children: a.items.map((it, i) => ({
        key: `${a.key}-${i}`,
        label: it.label,
        amount: it.amount,
      })),
    })),
    { key: 'net_change', label: '現金淨變動', amount: s.net_change },
  ]
})
</script>
