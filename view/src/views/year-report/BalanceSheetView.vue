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
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard label="總資產" :amount="totalAssets" />
        <MetricCard label="總負債" :amount="totalLiabilities" tone="rose" />
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
            <el-table
              :data="assetTree"
              row-key="key"
              :tree-props="{ children: 'children' }"
              border
              style="width: 100%"
            >
              <el-table-column prop="label" label="項目" min-width="200" />
              <el-table-column label="金額" width="160" align="right">
                <template #default="{ row }">
                  <MoneyDisplay :amount="row.amount" currency="TWD" :positive="true" size="sm" />
                </template>
              </el-table-column>
              <el-table-column label="原幣" width="140" align="right">
                <template #default="{ row }">
                  <MoneyDisplay
                    v-if="row.originalCurrency && row.originalCurrency !== 'TWD'"
                    :amount="row.originalAmount"
                    :currency="row.originalCurrency"
                    size="sm"
                  />
                  <span v-else class="text-on-surface-variant/40">—</span>
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
        </section>

        <section class="flex flex-col gap-4">
          <SectionHeader title="負債明細" />
          <div class="rounded-xl border border-outline-variant bg-surface-container p-4">
            <el-table
              :data="liabilityTree"
              row-key="key"
              :tree-props="{ children: 'children' }"
              border
              style="width: 100%"
            >
              <el-table-column prop="label" label="項目" min-width="200" />
              <el-table-column label="金額" width="160" align="right">
                <template #default="{ row }">
                  <MoneyDisplay
                    :amount="Math.abs(row.amount)"
                    currency="TWD"
                    :positive="false"
                    size="sm"
                  />
                </template>
              </el-table-column>
              <el-table-column label="原幣" width="140" align="right">
                <template #default="{ row }">
                  <MoneyDisplay
                    v-if="row.originalCurrency && row.originalCurrency !== 'TWD'"
                    :amount="Math.abs(row.originalAmount)"
                    :currency="row.originalCurrency"
                    :positive="false"
                    size="sm"
                  />
                  <span v-else class="text-on-surface-variant/40">—</span>
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
import {
  buildAssetTree,
  buildLiabilityTree,
  totalAssets as sumAssets,
  totalLiabilities as sumLiabilities,
} from './balanceTree'

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

const assetTree = computed(() =>
  store.balanceReport ? buildAssetTree(store.balanceReport) : [],
)

const liabilityTree = computed(() =>
  store.balanceReport ? buildLiabilityTree(store.balanceReport) : [],
)

const totalAssets = computed(() =>
  store.balanceReport ? sumAssets(store.balanceReport) : 0,
)

const totalLiabilities = computed(() =>
  store.balanceReport ? sumLiabilities(store.balanceReport) : 0,
)

const categoryChart = computed(() => {
  const xData = [
    ...assetTree.value.map((n) => n.label),
    ...liabilityTree.value.map((n) => n.label),
  ]
  const data = [
    ...assetTree.value.map((n) => n.amount),
    ...liabilityTree.value.map((n) => Math.abs(n.amount)),
  ]
  return { xData, series: [{ name: '金額', data }] }
})
</script>
