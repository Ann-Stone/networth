<template>
  <div :style="{ height: height, width: width }" />
</template>

<script>
import echarts from 'echarts'
require('echarts/theme/macarons') // echarts theme
import { debounce } from '@/utils'

export default {
  props: {
    width: {
      type: String,
      default: '100%'
    },
    height: {
      type: String,
      default: '400px'
    },
    defaultInnerTitle: { type: String, default: '' },
    defaultOuterTitle: { type: String, default: '' },
    innerPie: {
      type: Array,
      default: null
    },
    outerPie: {
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
    innerPie: {
      deep: true,
      handler() {
        this.updateChart()
      }
    }
  },
  mounted() {
    this.initChart()
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
      const _this = this
      this.chart.on('click', function(event) {
        if (!event.data.type) {
          _this.chart.setOption({
            series: {
              id: 'detail',
              name: event.name,
              data: _this.outerPie.filter((x) => x.type === event.name)
            }
          })
        }
      })
      this.updateChart()
    },
    updateChart() {
      this.chart.setOption({
        tooltip: {},
        legend: {
          data: this.innerPie.map((item) => item.name),
          show: false
        },
        series: [
          {
            name: this.defaultInnerTitle,
            type: 'pie',
            selectedMode: 'single',
            radius: [0, '30%'],
            label: {
              formatter: '{b}\n\n{d}%',
              position: 'inner',
              fontSize: 14
            },
            labelLine: {
              show: false
            },
            data: this.innerPie
          },
          {
            id: 'detail',
            name: this.defaultOuterTitle,
            type: 'pie',
            radius: ['45%', '60%'],
            labelLine: {
              length: 30
            },
            label: {
              formatter: ' {b|{b}：}{c|{c}}  {per|{d}%}  ',
              backgroundColor: '#F6F8FC',
              borderColor: '#8C8D8E',
              borderWidth: 1,
              borderRadius: 4,

              rich: {
                b: {
                  color: '#4C5058',
                  fontSize: 14,
                  fontWeight: 'bold',
                  lineHeight: 33
                },
                c: {
                  color: '#4C5058',
                  fontSize: 14,
                  fontWeight: 'bold'
                },
                per: {
                  color: '#fff',
                  backgroundColor: '#4C5058',
                  padding: [3, 4],
                  borderRadius: 4
                }
              }
            },
            data: this.outerPie.filter((x) => x.type === this.defaultOuterTitle)
          }
        ]
      })
    }
  }
}
</script>
