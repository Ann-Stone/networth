<template>
  <v-chart class="chart" :option="option" :style="{ height }" autoresize />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart as EchartsPieChart } from 'echarts/charts'
import {
  TooltipComponent,
  LegendComponent,
  GraphicComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'

use([
  CanvasRenderer,
  EchartsPieChart,
  TooltipComponent,
  LegendComponent,
  GraphicComponent,
])

const props = withDefaults(
  defineProps<{
    data: Array<{ name: string; value: number }>
    centerText?: string
    height?: string
  }>(),
  { height: '300px' },
)

const option = computed(() => {
  const graphic = props.centerText
    ? [
        {
          type: 'text',
          left: 'center',
          top: 'middle',
          style: {
            text: props.centerText,
            fill: '#8fa79b',
            fontSize: 18,
            fontWeight: 600,
          },
        },
      ]
    : undefined

  return {
    color: ['#8fa79b', '#b58d8d', '#a8a29e', '#6b8e82', '#c4967a'],
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    graphic,
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: true,
        label: { show: false },
        data: props.data,
      },
    ],
  }
})
</script>
