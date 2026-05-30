<template>
  <div class="flex flex-col gap-8">
    <PageHeader title="資產概覽" :subtitle="`${store.selectedYear} 年`">
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

    <el-skeleton v-if="store.assetsLoading" :rows="6" animated />
    <EmptyState
      v-else-if="!store.assetsReport || store.assetsReport.items.length === 0"
      message="暫無資產資料"
    />
    <template v-else>
      <MetricCard label="總資產" :amount="store.assetsReport.total" />

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <section class="flex flex-col gap-4">
          <SectionHeader title="資產組成" />
          <DonutChart :data="donutData" :center-text="centerText" height="360px" />
        </section>

        <section class="flex flex-col gap-4">
          <SectionHeader title="明細" />
          <div class="rounded-xl border border-outline-variant bg-surface-container p-4">
            <el-table :data="store.assetsReport.items" stripe border style="width: 100%">
              <el-table-column prop="type" label="類別" min-width="140">
                <template #default="{ row }">
                  <span>{{ TYPE_LABEL[row.type] ?? row.type }}</span>
                </template>
              </el-table-column>
              <el-table-column label="金額" width="180" align="right">
                <template #default="{ row }">
                  <MoneyDisplay :amount="row.amount" :positive="true" size="sm" />
                </template>
              </el-table-column>
              <el-table-column label="占比" width="120" align="right">
                <template #default="{ row }">
                  <span class="text-on-surface tabular-nums">{{ row.share.toFixed(1) }}%</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </section>
      </div>

      <section v-if="hasStockAllocation" class="flex flex-col gap-4">
        <SectionHeader title="股票分類配置" />
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <DonutChart :data="stockDonutData" :center-text="stockCenterText" height="320px" />
          <div class="rounded-xl border border-outline-variant bg-surface-container p-4">
            <el-table :data="store.stockAllocation!.items" stripe border style="width: 100%">
              <el-table-column prop="category_name" label="分類" min-width="140" />
              <el-table-column label="金額" width="180" align="right">
                <template #default="{ row }">
                  <MoneyDisplay :amount="row.amount" :positive="true" size="sm" />
                </template>
              </el-table-column>
              <el-table-column label="占比" width="120" align="right">
                <template #default="{ row }">
                  <span class="text-on-surface tabular-nums">{{ row.share.toFixed(1) }}%</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
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
import DonutChart from '@/components/charts/DonutChart.vue'
import { useYearReportStore } from '@/stores/yearReport'

const store = useYearReportStore()

const TYPE_LABEL: Record<string, string> = {
  accounts: '帳戶',
  stocks: '股票',
  estates: '不動產',
  insurances: '保險',
  other_assets: '其他資產',
}

const selectedYearDate = ref<Date>(new Date(store.selectedYear, 0, 1))

watch(selectedYearDate, (date) => {
  if (!date) return
  const year = date.getFullYear()
  if (year !== store.selectedYear) {
    void store.fetchAssetsReport(year)
  }
})

onMounted(() => {
  void store.fetchAssetsReport(store.selectedYear)
  void store.fetchStockAllocation()
})

const donutData = computed(() =>
  store.assetsReport
    ? store.assetsReport.items.map((i) => ({
        name: TYPE_LABEL[i.type] ?? i.type,
        value: i.amount,
      }))
    : [],
)

const centerText = computed(() => {
  if (!store.assetsReport) return ''
  const total = new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 0,
  }).format(store.assetsReport.total)
  return `總額 ${total}`
})

const hasStockAllocation = computed(
  () => !!store.stockAllocation && store.stockAllocation.items.length > 0,
)

const stockDonutData = computed(() =>
  store.stockAllocation
    ? store.stockAllocation.items.map((i) => ({ name: i.category_name, value: i.amount }))
    : [],
)

const stockCenterText = computed(() => {
  if (!store.stockAllocation) return ''
  const total = new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 0,
  }).format(store.stockAllocation.total)
  return `股票 ${total}`
})
</script>
