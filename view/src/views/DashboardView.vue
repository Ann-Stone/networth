<template>
  <div class="flex flex-col gap-8">
    <PageHeader title="儀表板" :subtitle="today" />

    <section class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <template v-for="card in summaryCards" :key="card.type">
        <el-skeleton v-if="store.summariesLoading[card.type]" :rows="3" animated />
        <MetricCard
          v-else-if="card.format === 'currency'"
          :label="card.label"
          :amount="card.value"
          :delta-percent="card.deltaPercent"
          :delta-label="card.deltaLabel"
        />
        <div
          v-else
          class="flex flex-col gap-3 rounded-xl p-8 bg-white dark:bg-surface-dark border border-slate-200 dark:border-primary/5 shadow-sm"
        >
          <p class="text-slate-500 dark:text-muted-text text-sm font-semibold uppercase tracking-wider">
            {{ card.label }}
          </p>
          <span class="tabular-nums text-3xl font-bold text-neutral text-slate-900 dark:text-cream">
            {{ formatPercent(card.value) }}
          </span>
          <div v-if="card.deltaPercent !== undefined" class="flex items-center gap-1.5 mt-2">
            <TrendBadge :value="card.deltaPercent" />
            <span v-if="card.deltaLabel" class="text-slate-400 dark:text-muted-text text-xs">
              {{ card.deltaLabel }}
            </span>
          </div>
        </div>
      </template>
    </section>

    <section class="flex flex-col gap-4">
      <SectionHeader title="近期提醒" />
      <el-skeleton v-if="store.alarmsLoading" :rows="3" animated />
      <EmptyState v-else-if="store.alarms.length === 0" message="近半年沒有待辦提醒" />
      <DataListCard v-else title="未來 6 個月提醒">
        <div
          v-for="(alarm, idx) in store.alarms"
          :key="`${alarm.date}-${idx}`"
          class="flex items-center justify-between px-6 py-4"
        >
          <div class="flex items-center gap-4">
            <span
              class="inline-flex items-center justify-center min-w-[64px] px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-semibold"
            >
              {{ alarm.date }}
            </span>
            <p class="text-slate-800 dark:text-cream text-sm">{{ alarm.content }}</p>
          </div>
        </div>
      </DataListCard>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import dayjs from 'dayjs'
import PageHeader from '@/components/ui/PageHeader.vue'
import MetricCard from '@/components/ui/MetricCard.vue'
import TrendBadge from '@/components/ui/TrendBadge.vue'
import SectionHeader from '@/components/ui/SectionHeader.vue'
import DataListCard from '@/components/ui/DataListCard.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import { useDashboardStore, type SummaryType } from '@/stores/dashboard'
import type { DashboardSummary } from '@/types/models'

const store = useDashboardStore()

const today = dayjs().format('YYYY-MM-DD')

const period = (() => {
  const end = dayjs()
  const start = end.subtract(11, 'month')
  return `${start.format('YYYYMM')}-${end.format('YYYYMM')}`
})()

const summaryTypes: SummaryType[] = ['asset_debt_trend', 'spending', 'freedom_ratio']

const labelMap: Record<SummaryType, string> = {
  asset_debt_trend: '資產淨值',
  spending: '本期支出',
  freedom_ratio: '財務自由度',
}

const formatMap: Record<SummaryType, 'currency' | 'percent'> = {
  asset_debt_trend: 'currency',
  spending: 'currency',
  freedom_ratio: 'percent',
}

function latestValue(summary: DashboardSummary | null): number {
  if (!summary || summary.points.length === 0) return 0
  return summary.points[summary.points.length - 1]!.value
}

function previousValue(summary: DashboardSummary | null): number | null {
  if (!summary || summary.points.length < 2) return null
  return summary.points[summary.points.length - 2]!.value
}

function deltaPercent(summary: DashboardSummary | null): number | undefined {
  const prev = previousValue(summary)
  if (prev === null || prev === 0) return undefined
  const curr = latestValue(summary)
  return ((curr - prev) / Math.abs(prev)) * 100
}

function deltaLabel(summary: DashboardSummary | null): string | undefined {
  if (!summary || summary.points.length < 2) return undefined
  return '較上期'
}

function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`
}

const summaryCards = computed(() =>
  summaryTypes.map((type) => {
    const summary = store.summaries[type]
    return {
      type,
      label: labelMap[type],
      format: formatMap[type],
      value: latestValue(summary),
      deltaPercent: deltaPercent(summary),
      deltaLabel: deltaLabel(summary),
    }
  }),
)

onMounted(() => {
  for (const type of summaryTypes) {
    store.fetchSummary({ type, period })
  }
  store.fetchAlarms()
})
</script>
