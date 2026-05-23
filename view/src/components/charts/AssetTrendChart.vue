<template>
  <v-chart
    class="chart"
    :option="option"
    :update-options="{ notMerge: true }"
    :style="{ height }"
    autoresize
  />
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
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

type ChartMode = 'stack' | 'line'
const chartMode = ref<ChartMode>('stack')

type YAxisType = 'value' | 'log'
const yAxisType = ref<YAxisType>('value')

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

  const isLog = yAxisType.value === 'log'
  const isStack = chartMode.value === 'stack' && !isLog // disable stacking on log scale to prevent mathematical distortion
  
  const stackedSeries = CATEGORIES.map((cat) => ({
    name: cat.label,
    type: 'line' as const,
    ...(isStack ? { stack: 'asset', areaStyle: {} } : {}),
    smooth: false,
    symbol: 'none' as const,
    data: props.points.map((p) => {
      const val = p.breakdown?.[cat.key] ?? 0
      if (isLog && val <= 0) return null // map 0 or negative values to null on log scale to prevent crashes
      return val
    }),
  }))

  const netWorthSeries = {
    name: NET_WORTH_LABEL,
    type: 'line' as const,
    symbol: 'none' as const,
    lineStyle: { width: 2, color: netWorthLineColor() },
    itemStyle: { color: netWorthLineColor() },
    data: props.points.map((p) => {
      const val = p.value
      if (isLog && val <= 0) return null // map 0 or negative values to null on log scale to prevent crashes
      return val
    }),
  }

  const isDark = appStore.theme === 'dark'
  const textColor = isDark ? '#c2c8c3' : '#404944' // matches --ds-on-surface-variant
  const lineColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)' // subtle grid lines
  const axisLineColor = isDark ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.12)'

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
      textStyle: { color: textColor },
      bottom: 0,
    },
    toolbox: {
      feature: {
        myStack: {
          show: !isLog, // only show stack option when not on log scale
          title: '切換為堆疊面積圖',
          icon: 'path://M432 928H160c-17.7 0-32-14.3-32-32V160c0-17.7 14.3-32 32-32h272c17.7 0 32 14.3 32 32v736c0 17.7-14.3 32-32 32zm224 0H544c-17.7 0-32-14.3-32-32V416c0-17.7 14.3-32 32-32h112c17.7 0 32 14.3 32 32v480c0 17.7-14.3 32-32 32zm208 0H768c-17.7 0-32-14.3-32-32V608c0-17.7 14.3-32 32-32h96c17.7 0 32 14.3 32 32v288c0 17.7-14.3 32-32 32z',
          iconStyle: {
            borderColor: chartMode.value === 'stack' ? '#5470c6' : '#666',
          },
          onclick: () => {
            chartMode.value = 'stack'
          },
        },
        myLine: {
          show: true,
          title: '切換為折線圖',
          icon: 'path://M880 144H144c-17.7 0-32 14.3-32 32v672c0 17.7 14.3 32 32 32h736c17.7 0 32-14.3 32-32V176c0-17.7-14.3-32-32-32zM208 832V272l192 320 224-256 256 352V832H208z',
          iconStyle: {
            borderColor: chartMode.value === 'line' ? '#5470c6' : '#666',
          },
          onclick: () => {
            chartMode.value = 'line'
          },
        },
        myLinear: {
          show: true,
          title: '切換為線性軸 (等差級距)',
          icon: 'path://M100 200h800v50H100zm0 200h800v50H100zm0 200h800v50H100zm0 200h800v50H100z',
          iconStyle: {
            borderColor: yAxisType.value === 'value' ? '#5470c6' : '#666',
          },
          onclick: () => {
            yAxisType.value = 'value'
          },
        },
        myLog: {
          show: true,
          title: '切換為對數軸 (等比級距)',
          icon: 'path://M100 100h800v50H100zm0 150h800v50H100zm0 250h800v50H100zm0 380h800v50H100z',
          iconStyle: {
            borderColor: yAxisType.value === 'log' ? '#5470c6' : '#666',
          },
          onclick: () => {
            yAxisType.value = 'log'
            chartMode.value = 'line' // force line mode
          },
        },
      },
    },
    grid: { left: 50, right: 20, top: 40, bottom: 56, containLabel: true },
    xAxis: {
      type: 'category',
      data: xData,
      boundaryGap: false,
      axisLabel: { color: textColor },
      axisLine: { lineStyle: { color: axisLineColor } },
    },
    yAxis: {
      type: yAxisType.value,
      axisLabel: {
        color: textColor,
        formatter: (value: number) => moneyFormatter.format(value),
      },
      splitLine: { lineStyle: { color: lineColor } },
    },
    series: [...stackedSeries, netWorthSeries],
  }
})

defineExpose({ option })
</script>
