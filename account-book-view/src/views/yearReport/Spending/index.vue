<template>
  <div class="page spending-report">
    <div class="conditon position-right">
      <el-date-picker
        v-if="periodType === 'month'"
        v-model="dateValue"
        type="month"
        value-format="yyyyMM"
        placeholder="請選擇"
        @change="fetchData"
      />
      <el-date-picker
        v-else
        v-model="dateValue"
        type="year"
        value-format="yyyy"
        placeholder="請選擇"
        @change="fetchData"
      />
      <el-radio-group v-model="periodType" @change="changePeriod">
        <el-radio-button label="year">年</el-radio-button>
        <el-radio-button label="month">月</el-radio-button>
      </el-radio-group>
    </div>
    <BarChart
      v-if="chartContent.length > 0"
      :show-percentage="type === 'all'"
      :x-bar="chartCategory"
      :content="chartContent"
    />
    <div class="down-area">
      <div>
        <el-button type="text" @click="changeChart('income')">收入</el-button>
        <el-table
          :data="incomes"
          :summary-method="getSummaries"
          header-cell-class-name="table-header"
          show-summary
        >
          <el-table-column
            label="分類"
            prop="type"
            header-align="center"
            align="center"
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
      <div>
        <el-button type="text" @click="changeChart('spending')">支出</el-button>
        <el-table
          :data="spendings"
          :summary-method="getSummaries"
          header-cell-class-name="table-header"
          show-summary
        >
          <el-table-column
            label="分類"
            prop="type"
            header-align="center"
            align="center"
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
</template>

<script>
import moment from 'moment'

import BarChart from '@/components/Charts/BarChart'
import { getMappingName } from '@/utils/codeMapping'
import { getSummaries } from '@/utils/index'

export default {
  name: 'SpendingReport',
  components: { BarChart },
  data() {
    return {
      periodType: 'month',
      dateFormat: 'yyyyMM',
      dateType: 'month',
      dateValue: null,
      sourceList: [],
      chartCategory: null,
      chartContent: [],
      type: 'all'
    }
  },
  computed: {
    incomes() {
      return this.getIncomeByInput(this.dateValue)
    },
    spendings() {
      return this.getSpendingByInput(this.dateValue)
    }
  },
  created() {
    this.dateValue = moment().format('YYYYMM')
    this.fetchData()
  },
  methods: {
    getSummaries,
    fetchData() {
      this.$store
        .dispatch('GetSpendingList', {
          type: this.periodType,
          dateValue: this.dateValue
        })
        .then((response) => {
          this.sourceList = response.data
          this.chartCategory = [
            ...new Set(response.data.map((item) => item.dateString))
          ].sort()

          // if (this.chartCategory.indexOf(this.dateValue) === -1) {
          //   this.dateValue = moment(
          //     Math.max.apply(null, this.chartCategory) +
          //       (this.dateType === 'month' ? '01' : '0101')
          //   ).format(this.dateType === 'month' ? 'YYYYMM' : 'YYYY')
          // }

          this.generateChartContent()
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
    getSum(dateString, type) {
      const result = this.sourceList.filter(
        (item) => item.dateString === dateString && item.type === type
      )

      return result.reduce((sum, item) => sum + item.amount, 0)
    },
    getIncomeByInput(input) {
      return [
        {
          type: getMappingName('code_type', 'Income'),
          amount: this.getSum(input, 'Income')
        },
        {
          type: getMappingName('code_type', 'Passive'),
          amount: this.getSum(input, 'Passive')
        }
      ]
    },
    getSpendingByInput(input) {
      return [
        {
          type: getMappingName('code_type', 'Floating'),
          amount: this.getSum(input, 'Floating')
        },
        {
          type: getMappingName('code_type', 'Fixed'),
          amount: this.getSum(input, 'Fixed')
        },
        {
          type: '貸款支出',
          amount: this.getSum(input, 'Loan') * -1 // 因為利息與償還本金不同性質
        }
      ]
    },
    changeChart(type) {
      this.type = type
      this.generateChartContent()
    },
    generateChartContent() {
      const incomeList = []
      const passiveList = []
      const incomeAmountList = []
      const floatingList = []
      const fixedList = []
      const loanList = []
      const spendingAmountList = []
      const spendingRateList = []

      this.chartCategory.forEach((time) => {
        let incomeAmount = 0
        let spendingAmount = 0

        // 查收入或全部，需產出收入資料
        if (this.type === 'income' || this.type === 'all') {
          const incomes = this.getIncomeByInput(time)

          incomes.forEach((item) => {
            if (item.type === '主動收入') incomeList.push(item.amount)
            else passiveList.push(item.amount)
          })

          incomeAmount = incomes.reduce((sum, item) => sum + item.amount, 0)
          if (this.type === 'income') incomeAmountList.push(incomeAmount)
        }

        // 查支出或全部，需產出支出資料
        if (this.type === 'spending' || this.type === 'all') {
          const spendings = this.getSpendingByInput(time)

          spendings.forEach((item) => {
            if (item.type === '浮動支出') floatingList.push(item.amount)
            else if (item.type === '固定支出') fixedList.push(item.amount)
            else loanList.push(item.amount)
          })

          spendingAmount = spendings.reduce((sum, item) => sum + item.amount, 0)
          if (this.type === 'spending') spendingAmountList.push(spendingAmount)
        }

        if (this.type === 'all') {
          spendingRateList.push(
            incomeAmount
              ? (Math.abs(spendingAmount) / incomeAmount).toFixed(2) * 100
              : spendingAmount
          )
        }
      })

      let result = null
      if (this.type === 'income') {
        result = [
          { name: '主動收入', type: 'bar', stack: 'Income', data: incomeList },
          { name: '被動收入', type: 'bar', stack: 'Income', data: passiveList },
          { name: '總收入', type: 'line', data: incomeAmountList }
        ]
      } else if (this.type === 'spending') {
        result = [
          {
            name: '浮動支出',
            type: 'bar',
            stack: 'Spending',
            data: floatingList
          },
          { name: '固定支出', type: 'bar', stack: 'Spending', data: fixedList },
          { name: '貸款支出', type: 'bar', stack: 'Spending', data: loanList },
          { name: '總支出', type: 'line', data: spendingAmountList }
        ]
      } else {
        result = [
          { name: '主動收入', type: 'bar', stack: 'Income', data: incomeList },
          { name: '被動收入', type: 'bar', stack: 'Income', data: passiveList },
          {
            name: '浮動支出',
            type: 'bar',
            stack: 'Spending',
            data: floatingList
          },
          { name: '固定支出', type: 'bar', stack: 'Spending', data: fixedList },
          { name: '貸款支出', type: 'bar', stack: 'Spending', data: loanList },
          {
            name: '收支比',
            type: 'line',
            yAxisIndex: 1,
            data: spendingRateList
          }
        ]
      }

      this.chartContent = result
    }
  }
}
</script>

<style lang="scss" scoped>
.spending-report {
  .conditon {
    margin-bottom: 10px;
  }

  .down-area {
    width: 100%;
    display: flex;
    margin-top: 10px;

    & > div {
      width: 50%;

      &:first-child {
        padding-right: 10px;
      }

      /deep/.el-button {
        font-size: 18px;
      }
    }
  }
}
</style>
