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
} from 'echarts/components'
import VChart from 'vue-echarts'

use([
  CanvasRenderer,
  EchartsLineChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
])

const props = withDefaults(
  defineProps<{
    xData: string[]
    series: Array<{ name: string; data: number[] }>
    height?: string
  }>(),
  { height: '300px' },
)

const option = computed(() => ({
  color: ['#8fa79b', '#b58d8d', '#a8a29e', '#6b8e82', '#c4967a'],
  tooltip: { trigger: 'axis' },
  legend: { data: props.series.map((s) => s.name) },
  grid: { left: 40, right: 20, top: 40, bottom: 30, containLabel: true },
  xAxis: { type: 'category', data: props.xData, boundaryGap: false },
  yAxis: { type: 'value' },
  series: props.series.map((s) => ({
    name: s.name,
    type: 'line',
    smooth: true,
    data: s.data,
  })),
}))
</script>
