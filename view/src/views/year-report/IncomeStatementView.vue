<template>
  <div class="flex flex-col gap-8">
    <PageHeader title="損益表" :subtitle="`${store.selectedYear} 年 · 本業 / 投資 / 綜合`">
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

    <el-skeleton v-if="store.incomeStatementLoading" :rows="6" animated />
    <EmptyState v-else-if="!hasData" message="暫無損益資料" />
    <template v-else>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard
          label="本業淨額"
          :amount="summary.operating_net"
          :tone="summary.operating_net < 0 ? 'rose' : 'primary'"
          tooltip="本業收入（薪資等）− 生活支出（固定＋變動）"
        />
        <MetricCard
          label="投資損益"
          :amount="summary.investment_net"
          :tone="summary.investment_net < 0 ? 'rose' : 'primary'"
          tooltip="孳息（股息/利息）＋ 已實現資本利得 ＋ 未實現市值變動"
        />
        <MetricCard
          label="綜合損益"
          :amount="summary.comprehensive_net"
          :tone="summary.comprehensive_net < 0 ? 'rose' : 'primary'"
          tooltip="本業淨額 ＋ 投資損益"
        />
      </div>

      <section class="flex flex-col gap-4">
        <SectionHeader title="損益構成（本業 → 投資 → 綜合）" />
        <div class="rounded-xl border border-outline-variant bg-surface-container p-4">
          <WaterfallChart :items="waterfallItems" total-label="綜合損益" height="320px" />
        </div>
      </section>

      <section class="flex flex-col gap-4">
        <SectionHeader title="逐期損益" />
        <BarChart :x-data="chart.xData" :series="chart.series" height="360px" />
      </section>

      <section class="flex flex-col gap-4">
        <SectionHeader title="損益明細" />
        <p class="text-on-surface-variant/70 text-sm -mt-2">
          孳息（被動收入）歸於「投資損益」，與「年度支出」頁將其計入收入的口徑不同——兩者刻意分流，並非錯誤。
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
  void store.fetchIncomeStatement(activeType.value, store.selectedYear)
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
  () => !!store.incomeStatementReport && store.incomeStatementReport.points.length > 0,
)

const summary = computed(
  () =>
    store.incomeStatementReport?.summary ?? {
      active_income: 0,
      fixed: 0,
      floating: 0,
      operating_net: 0,
      dividend: 0,
      realized: 0,
      unrealized: 0,
      investment_net: 0,
      comprehensive_net: 0,
    },
)

const chart = computed(() => {
  const report = store.incomeStatementReport
  if (!report) return { xData: [], series: [] }
  return {
    xData: report.points.map((p) => p.period),
    series: [
      // 本業淨額 and 投資損益 stack into 綜合損益; the line traces the total.
      { name: '本業淨額', data: report.points.map((p) => p.operating_net), stack: 'pnl' },
      { name: '投資損益', data: report.points.map((p) => p.investment_net), stack: 'pnl' },
      {
        name: '綜合損益',
        data: report.points.map((p) => p.comprehensive_net),
        type: 'line' as const,
      },
    ],
  }
})

const waterfallItems = computed(() => [
  { name: '本業淨額', value: summary.value.operating_net },
  { name: '投資損益', value: summary.value.investment_net },
])

const breakdownTree = computed(() => {
  const s = summary.value
  return [
    {
      key: 'operating',
      label: '本業損益',
      amount: s.operating_net,
      children: [
        { key: 'active', label: '本業收入', amount: s.active_income },
        { key: 'fixed', label: '固定支出', amount: -s.fixed },
        { key: 'floating', label: '變動支出', amount: -s.floating },
      ],
    },
    {
      key: 'investment',
      label: '投資損益',
      amount: s.investment_net,
      children: [
        { key: 'dividend', label: '孳息（股息/利息）', amount: s.dividend },
        { key: 'realized', label: '已實現資本利得', amount: s.realized },
        { key: 'unrealized', label: '未實現市值變動', amount: s.unrealized },
      ],
    },
    { key: 'comprehensive', label: '綜合損益', amount: s.comprehensive_net },
  ]
})
</script>
