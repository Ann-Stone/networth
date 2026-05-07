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

    <section class="flex flex-col gap-4">
      <el-tabs v-model="activeType" @tab-change="handleTypeChange">
        <el-tab-pane label="月度" name="monthly" />
        <el-tab-pane label="年度" name="yearly" />
      </el-tabs>

      <el-skeleton v-if="store.expenditureLoading" :rows="4" animated />
      <EmptyState
        v-else-if="!store.expenditureReport || store.expenditureReport.points.length === 0"
        message="暫無支出資料"
      />
      <BarChart
        v-else
        :x-data="chart.xData"
        :series="chart.series"
        height="360px"
      />
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import BarChart from '@/components/charts/BarChart.vue'
import { useYearReportStore } from '@/stores/yearReport'

const store = useYearReportStore()

const activeType = ref<'monthly' | 'yearly'>('monthly')
const selectedYearDate = ref<Date>(new Date(store.selectedYear, 0, 1))

function reload() {
  void store.fetchExpenditureReport(activeType.value, store.selectedYear)
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

const chart = computed(() => {
  const report = store.expenditureReport
  if (!report) return { xData: [], series: [] }
  return {
    xData: report.points.map((p) => p.period),
    series: [
      { name: '支出', data: report.points.map((p) => p.amount) },
    ],
  }
})
</script>
