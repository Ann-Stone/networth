<template>
  <div :class="className" :style="{ height: height, width: width }" />
</template>

<script>
import echarts from 'echarts'
require('echarts/theme/macarons') // echarts theme
import { debounce } from '@/utils'

export default {
  props: {
    className: {
      type: String,
      default: 'chart'
    },
    width: {
      type: String,
      default: '100%'
    },
    height: {
      type: String,
      default: '350px'
    },
    autoResize: {
      type: Boolean,
      default: true
    },
    chartData: {
      type: Object,
      default: null
    },
    xBar: {
      type: Array,
      default: null
    },
    lineName: {
      type: Array,
      default: () => ['first', 'second']
    }
  },
  data() {
    return {
      chart: null,
      sidebarElm: null
    }
  },
  watch: {
    chartData: {
      deep: true,
      handler(val) {
        this.setOptions(val)
      }
    }
  },
  mounted() {
    this.initChart()
    if (this.autoResize) {
      this.__resizeHandler = debounce(() => {
        if (this.chart) {
          this.chart.resize()
        }
      }, 100)
      window.addEventListener('resize', this.__resizeHandler)
    }

    // 监听侧边栏的变化
    this.sidebarElm = document.getElementsByClassName('sidebar-container')[0]
    this.sidebarElm &&
      this.sidebarElm.addEventListener(
        'transitionend',
        this.sidebarResizeHandler
      )
  },
  beforeDestroy() {
    if (!this.chart) {
      return
    }
    if (this.autoResize) {
      window.removeEventListener('resize', this.__resizeHandler)
    }

    this.sidebarElm &&
      this.sidebarElm.removeEventListener(
        'transitionend',
        this.sidebarResizeHandler
      )

    this.chart.dispose()
    this.chart = null
  },
  methods: {
    sidebarResizeHandler(e) {
      if (e.propertyName === 'width') {
        this.__resizeHandler()
      }
    },
    setOptions({ firstData, secondData, thirdData, fourthData, fifthData } = {}) {
      this.chart.setOption({
        xAxis: {
          data: this.xBar,
          boundaryGap: false,
          axisTick: {
            show: false
          }
        },
        grid: {
          left: 10,
          right: 25,
          bottom: 20,
          top: 30,
          containLabel: true
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          },
          padding: [5, 10]
        },
        yAxis: {
          axisTick: {
            show: false
          }
        },
        legend: {
          data: this.lineName
        },
        series: [
          {
            name: this.lineName[4],
            smooth: true,
            type: 'line',
            itemStyle: {
              normal: {
                color: '#FF005A',
                lineStyle: {
                  color: '#FF005A',
                  width: 2
                },
                areaStyle: {
                  color: '#f3f8ff'
                }
              }
            },
            data: fifthData,
            animationDuration: 2800,
            animationEasing: 'quadraticOut'
          },
          {
            name: this.lineName[0],
            itemStyle: {
              normal: {
                color: '#3888FA',
                lineStyle: {
                  color: '#3888FA',
                  width: 2
                }
              }
            },
            smooth: true,
            type: 'line',
            data: firstData,
            animationDuration: 2800,
            animationEasing: 'cubicInOut'
          },
          {
            name: this.lineName[1],
            itemStyle: {
              normal: {
                color: 'brown',
                lineStyle: {
                  color: 'brown',
                  width: 2
                }
              }
            },
            smooth: true,
            type: 'line',
            data: secondData,
            animationDuration: 2800,
            animationEasing: 'cubicInOut'
          },
          {
            name: this.lineName[2],
            itemStyle: {
              normal: {
                color: 'green',
                lineStyle: {
                  color: 'green',
                  width: 2
                }
              }
            },
            smooth: true,
            type: 'line',
            data: thirdData,
            animationDuration: 2800,
            animationEasing: 'cubicInOut'
          },
          {
            name: this.lineName[3],
            itemStyle: {
              normal: {
                color: 'purple',
                lineStyle: {
                  color: 'purple',
                  width: 2
                }
              }
            },
            smooth: true,
            type: 'line',
            data: fourthData,
            animationDuration: 2800,
            animationEasing: 'cubicInOut'
          }
        ]
      })
    },
    initChart() {
      this.chart = echarts.init(this.$el, 'macarons')
      this.setOptions(this.chartData)
    }
  }
}
</script>
