<template>
  <v-chart class="chart" :option="option" :style="{ height }" autoresize />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart as EchartsLineChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  ToolboxComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'
import { useAppStore } from '@/stores/app'
import { getChartColors } from '@/utils/chartTheme'
import type { DashboardSummaryPoint } from '@/types/models'

use([
  CanvasRenderer,
  EchartsLineChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  ToolboxComponent,
])

interface AssetCategory {
  key: string
  label: string
}

// Stacked-area order: positive assets first (top of legend), then liabilities.
const CATEGORIES: AssetCategory[] = [
  { key: 'insurances', label: '保險' },
  { key: 'estates', label: '不動產' },
  { key: 'stocks', label: '股票' },
  { key: 'accounts', label: '現金' },
  { key: 'cards', label: '信用卡' },
  { key: 'loans', label: '貸款' },
]
const NET_WORTH_LABEL = '淨值'

const props = withDefaults(
  defineProps<{
    points: DashboardSummaryPoint[]
    height?: string
  }>(),
  { height: '360px' },
)

const appStore = useAppStore()

function formatYYYYMM(period: string): string {
  if (period.length !== 6) return period
  return `${period.slice(0, 4)}/${period.slice(4)}`
}

const moneyFormatter = new Intl.NumberFormat('en-US', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
})

function netWorthLineColor(): string {
  if (typeof document === 'undefined') return '#000000'
  const v = getComputedStyle(document.documentElement)
    .getPropertyValue('--ds-on-surface')
    .trim()
  return v || '#000000'
}

const option = computed(() => {
  void appStore.theme // recompute on theme toggle so colors stay in sync

  const xData = props.points.map((p) => formatYYYYMM(p.period))

  const stackedSeries = CATEGORIES.map((cat) => ({
    name: cat.label,
    type: 'line' as const,
    stack: 'asset',
    areaStyle: {},
    smooth: false,
    symbol: 'none' as const,
    data: props.points.map((p) => p.breakdown?.[cat.key] ?? 0),
  }))

  const netWorthSeries = {
    name: NET_WORTH_LABEL,
    type: 'line' as const,
    symbol: 'none' as const,
    lineStyle: { width: 2, color: netWorthLineColor() },
    itemStyle: { color: netWorthLineColor() },
    data: props.points.map((p) => p.value),
  }

  return {
    color: getChartColors(),
    tooltip: {
      trigger: 'axis',
      formatter: (params: unknown) => {
        const arr = Array.isArray(params) ? params : [params]
        const first = arr[0] as { axisValueLabel?: string } | undefined
        const header = first?.axisValueLabel ?? ''
        const lines = arr
          .map((p) => {
            const { marker, seriesName, value } = p as {
              marker: string
              seriesName: string
              value: number
            }
            return `${marker}${seriesName}: ${moneyFormatter.format(value ?? 0)}`
          })
          .join('<br/>')
        return `${header}<br/>${lines}`
      },
    },
    legend: {
      data: [...CATEGORIES.map((c) => c.label), NET_WORTH_LABEL],
    },
    toolbox: {
      feature: {
        magicType: { type: ['stack', 'line'] },
      },
    },
    grid: { left: 50, right: 20, top: 60, bottom: 30, containLabel: true },
    xAxis: { type: 'category', data: xData, boundaryGap: false },
    yAxis: { type: 'value' },
    series: [...stackedSeries, netWorthSeries],
  }
})

defineExpose({ option })
</script>
