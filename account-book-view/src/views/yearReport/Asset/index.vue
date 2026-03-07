<template>
  <div class="page spending-report">
    <div class="main-content">
      <div class="up-side">
        <!-- 點擊第一個PIE，跑第二個PIE -->
        <PieChart
          v-if="chartCategory.length > 0"
          :content="assetPieContent"
          pie-name="資產占比"
          width="50%"
          @clickPie="getDetailPie"
        />
        <div v-else class="no-data">尚無消費行為</div>
        <PieChart
          v-if="detailPie.length > 0"
          :content="detailPie"
          pie-name="各類資產明細占比"
          width="50%"
        />
        <div v-else class="no-data">尚無資產異動行為</div>
      </div>
      <div class="down-area">
        <!-- 這裡改跑回圈產表格，依所持有的資產種類跑 -->
        <div v-for="(item, index) in chartCategory" :key="index">
          {{ item }}
          <el-table
            :data="getTableContent(item)"
            :summary-method="getSummaries"
            header-cell-class-name="table-header"
            show-summary
          >
            <el-table-column
              label="名稱"
              prop="name"
              header-align="center"
              align="right"
            />
            <el-table-column label="金額" header-align="center" align="right">
              <template slot-scope="scope">
                <span>
                  {{ scope.row.amount | toThousandFilter(2) }}
                </span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import moment from 'moment'

import PieChart from '@/components/Charts/PieChart'
import { getSummaries } from '@/utils/index'

export default {
  name: 'AssetReport',
  components: { PieChart },
  data() {
    return {
      periodType: 'month',
      dateFormat: 'yyyyMM',
      dateType: 'month',
      dateValue: null,
      sourceList: [],
      chartCategory: [],
      detailPie: [],
      type: 'all'
    }
  },
  computed: {
    assetPieContent() {
      const result = []
      this.chartCategory.forEach((item) => {
        if (item === '股票') {
          const detailList = this.getGroupedData(item)

          Object.keys(detailList).forEach((key) => {
            result.push({
              name: key,
              value: detailList[key]
            })
          })
        } else {
          result.push({
            name: item,
            value: this.getTableContent(item).reduce(
              (sum, detail) => sum + detail.amount,
              0
            )
          })
        }
      })

      if (this.detailPie.length === 0) this.getDetailPie()

      return result
    }
  },
  created() {
    this.dateValue = moment().format('YYYYMM')
    this.fetchData()
  },
  methods: {
    getSummaries,
    fetchData() {
      this.$store.dispatch('GetAssetList').then((response) => {
        this.sourceList = response.data
        this.chartCategory = [
          ...new Set(response.data.map((item) => item.assetType))
        ]
      })
    },
    changePeriod(value) {
      this.type = 'all'

      if (value === 'year') {
        this.dateValue = moment().format('YYYY')
      } else {
        this.dateValue = moment().format('YYYYMM')
      }

      this.fetchData()
    },
    getTableContent(type) {
      return this.sourceList.filter((item) => item.assetType === type)
    },
    getDetailPie(response = { name: '現金' }) {
      if (this.sourceList.some((item) => item.assetType === response.name)) {
        this.detailPie = []
        const detailList = this.getGroupedData(response.name)

        Object.keys(detailList).forEach((key) => {
          this.detailPie.push({
            name: key,
            value: detailList[key]
          })
        })
      } else {
        this.detailPie = this.sourceList
          .filter((item) => item.detailType === response.name)
          .map((item) => {
            return {
              name: item.name,
              value: item.amount
            }
          })
      }
    },
    getGroupedData(name) {
      return this.getTableContent(name).reduce(function(groups, item) {
        const val = item['detailType']
        groups[val] = groups[val] || 0
        groups[val] += item.amount
        return groups
      }, {})
    }
  }
}
</script>

<style lang="scss" scoped>
.spending-report {
  .main-content {
    .up-side {
      min-height: 100px;
      display: flex;
      padding-top: 10px;

      .no-data {
        width: 50%;
        height: 100%;
        text-align: center;
        margin: auto;
      }
    }
    .down-area {
      width: 100%;
      display: flex;
      margin-top: 10px;

      & > div {
        width: 25%;

        &:not(:last-child) {
          padding-right: 10px;
        }

        /deep/.el-button {
          font-size: 18px;
        }
      }
    }
  }
}
</style>
