<template>
  <div :style="{ height: height, width: width }" />
</template>

<script>
import echarts from 'echarts'
require('echarts/theme/macarons') // echarts theme
import { debounce } from '@/utils'

const animationDuration = 6000

export default {
  name: 'MutiBarChart',
  props: {
    width: {
      type: String,
      default: '100%'
    },
    height: {
      type: String,
      default: '400px'
    },
    inputList: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      chart: null
    }
  },
  watch: {
    inputList: {
      deep: true,
      handler() {
        this.setChartContent()
      }
    }
  },
  mounted() {
    this.initChart()
    this.setChartContent()
    this.__resizeHandler = debounce(() => {
      if (this.chart) {
        this.chart.resize()
      }
    }, 100)
    window.addEventListener('resize', this.__resizeHandler)
  },
  beforeDestroy() {
    if (!this.chart) {
      return
    }
    window.removeEventListener('resize', this.__resizeHandler)
    this.chart.dispose()
    this.chart = null
  },
  methods: {
    initChart() {
      this.chart = echarts.init(this.$el, 'dark')

      this.chart.setOption({
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            // 坐标轴指示器，坐标轴触发有效
            type: 'shadow' // 默认为直线，可选为：'line' | 'shadow'
          }
        },
        grid: {
          top: 10,
          left: '2%',
          right: '2%',
          bottom: '3%',
          containLabel: true
        },
        dataset: {
          source: [[]]
        },
        xAxis: [
          {
            type: 'category',
            data: [],
            axisTick: {
              alignWithLabel: true
            }
          }
        ],
        yAxis: [
          {
            type: 'value',
            axisTick: {
              show: false
            }
          }
        ],
        series: []
      })
    },
    setChartContent() {
      const nameList = [...new Set(this.inputList.map((item) => item.name))]
      const typeList = new Set(this.inputList.map((item) => item.type))

      const source = [['type'].concat([...typeList])]
      nameList.forEach((item) => {
        const temp = [item]
        for (const type of [...typeList]) {
          const rows = this.inputList.find(
            (y) => y.name === item && y.type === type
          )
          if (rows) {
            temp.push(rows.value)
          }
        }

        if (temp.length > 1) source.push(temp)
      })

      const series = []
      typeList.forEach(() => {
        series.push({
          type: 'bar',
          animationDuration,
          itemStyle: {
            color: '#8dc1a9'
          }
        })
      })

      this.chart.setOption({
        dataset: {
          source: source
        },
        xAxis: [{ data: nameList }],
        series: series
      })
    }
  }
}
</script>
