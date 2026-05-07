<template>
  <div class="flex flex-col gap-8">
    <PageHeader title="資產負債表" :subtitle="`${store.selectedYear} 年`">
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

    <el-skeleton v-if="store.balanceLoading" :rows="6" animated />
    <EmptyState v-else-if="!store.balanceReport" message="尚無資產負債資料" />
    <template v-else>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <MetricCard label="總資產" :amount="totalAssets" />
        <MetricCard
          label="淨資產"
          :amount="store.balanceReport.net_worth"
          :tone="store.balanceReport.net_worth < 0 ? 'rose' : 'primary'"
        />
      </div>

      <section class="flex flex-col gap-4">
        <SectionHeader title="類別總覽" />
        <BarChart :x-data="categoryChart.xData" :series="categoryChart.series" height="320px" />
      </section>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <section class="flex flex-col gap-4">
          <SectionHeader title="資產明細" />
          <div class="rounded-xl border border-outline-variant bg-surface-container p-4">
            <el-table :data="assetRows" stripe border style="width: 100%">
              <el-table-column prop="category" label="類別" width="110" />
              <el-table-column prop="name" label="名稱" min-width="160" />
              <el-table-column label="金額" width="180" align="right">
                <template #default="{ row }">
                  <MoneyDisplay :amount="row.amount" :currency="row.currency" :positive="true" size="sm" />
                </template>
              </el-table-column>
            </el-table>
          </div>
        </section>

        <section class="flex flex-col gap-4">
          <SectionHeader title="負債明細" />
          <div class="rounded-xl border border-outline-variant bg-surface-container p-4">
            <el-table :data="liabilityRows" stripe border style="width: 100%">
              <el-table-column prop="category" label="類別" width="110" />
              <el-table-column prop="name" label="名稱" min-width="160" />
              <el-table-column label="金額" width="180" align="right">
                <template #default="{ row }">
                  <MoneyDisplay :amount="row.amount" :currency="row.currency" :positive="false" size="sm" />
                </template>
              </el-table-column>
            </el-table>
          </div>
        </section>
      </div>
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
import { useYearReportStore } from '@/stores/yearReport'
import type { BalanceReportLine } from '@/types/models'

const store = useYearReportStore()

const selectedYearDate = ref<Date>(new Date(store.selectedYear, 0, 1))

watch(selectedYearDate, (date) => {
  if (!date) return
  const year = date.getFullYear()
  if (year !== store.selectedYear) {
    void store.fetchBalanceReport(year)
  }
})

onMounted(() => {
  void store.fetchBalanceReport(store.selectedYear)
})

interface FlatRow {
  category: string
  name: string
  amount: number
  currency: string
}

const ASSET_CATEGORY_LABEL: Record<string, string> = {
  accounts: '帳戶',
  estates: '不動產',
  insurances: '保險',
  stocks: '股票',
}

const LIABILITY_CATEGORY_LABEL: Record<string, string> = {
  credit_cards: '信用卡',
  loans: '貸款',
}

function flatten(
  groups: Record<string, BalanceReportLine[]>,
  labels: Record<string, string>,
): FlatRow[] {
  const rows: FlatRow[] = []
  for (const [key, lines] of Object.entries(groups)) {
    for (const line of lines) {
      rows.push({
        category: labels[key] ?? key,
        name: line.name,
        amount: line.amount,
        currency: line.currency ?? 'TWD',
      })
    }
  }
  return rows
}

const assetRows = computed<FlatRow[]>(() =>
  store.balanceReport
    ? flatten(
        store.balanceReport.assets as unknown as Record<string, BalanceReportLine[]>,
        ASSET_CATEGORY_LABEL,
      )
    : [],
)

const liabilityRows = computed<FlatRow[]>(() =>
  store.balanceReport
    ? flatten(
        store.balanceReport.liabilities as unknown as Record<string, BalanceReportLine[]>,
        LIABILITY_CATEGORY_LABEL,
      )
    : [],
)

const totalAssets = computed(() =>
  assetRows.value.reduce((sum, row) => sum + row.amount, 0),
)

const categoryChart = computed(() => {
  const report = store.balanceReport
  if (!report) return { xData: [], series: [] }
  const assetEntries = Object.entries(report.assets) as Array<
    [string, BalanceReportLine[]]
  >
  const liabilityEntries = Object.entries(report.liabilities) as Array<
    [string, BalanceReportLine[]]
  >
  const xData = [
    ...assetEntries.map(([k]) => ASSET_CATEGORY_LABEL[k] ?? k),
    ...liabilityEntries.map(([k]) => LIABILITY_CATEGORY_LABEL[k] ?? k),
  ]
  const sums = [
    ...assetEntries.map(([, lines]) =>
      lines.reduce((s, l) => s + l.amount, 0),
    ),
    ...liabilityEntries.map(([, lines]) =>
      lines.reduce((s, l) => s + Math.abs(l.amount), 0),
    ),
  ]
  return {
    xData,
    series: [{ name: '金額', data: sums }],
  }
})
</script>
