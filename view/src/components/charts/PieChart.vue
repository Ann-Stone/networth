<template>
  <v-chart class="chart" :option="option" :style="{ height }" autoresize />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart as EchartsPieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, EchartsPieChart, TooltipComponent, LegendComponent])

const props = withDefaults(
  defineProps<{
    data: Array<{ name: string; value: number }>
    height?: string
  }>(),
  { height: '300px' },
)

const option = computed(() => ({
  color: ['#8fa79b', '#b58d8d', '#a8a29e', '#6b8e82', '#c4967a'],
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  series: [
    {
      type: 'pie',
      radius: '60%',
      center: ['50%', '45%'],
      data: props.data,
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.3)',
        },
      },
    },
  ],
}))
</script>
