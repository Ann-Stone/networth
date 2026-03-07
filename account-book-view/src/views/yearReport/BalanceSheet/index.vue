<template>
  <div class="page balance-sheet">
    <div class="up-area">
      <div>
        <p>資產</p>
        <el-table
          :data="assets"
          :span-method="processAssetTypeSpan"
          header-cell-class-name="table-header"
        >
          <el-table-column
            label="分類"
            prop="type"
            header-align="center"
            align="center"
          />
          <el-table-column
            label="項目"
            prop="name"
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
        <p>負債</p>
        <el-table :data="liabilities" header-cell-class-name="table-header">
          <el-table-column
            label="項目"
            prop="name"
            header-align="center"
            align="center"
          />
          <el-table-column label="金額" header-align="center" align="right">
            <template slot-scope="scope">
              <span>
                {{ scope.row.amount | toThousandFilter }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
    <div class="down-area">
      <div>
        <p>
          <span>總資產</span
          ><span
            :class="[
              totalAssetAmount - totalLiabilityAmount > 0
                ? 'positive'
                : 'negative'
            ]"
            class="money"
          >
            {{ totalAssetAmount | toThousandFilter(2) }}
          </span>
        </p>
      </div>
      <div>
        <p>
          <span>總負債</span
          ><span
            :class="[
              totalAssetAmount - totalLiabilityAmount > 0 ? 'negative' : ''
            ]"
            class="money"
          >
            {{ totalLiabilityAmount | toThousandFilter }}
          </span>
        </p>
        <p>
          <span>資產淨值</span
          ><span
            :class="[
              totalAssetAmount - totalLiabilityAmount >= 0
                ? 'positive'
                : 'negative'
            ]"
            class="money"
          >
            {{
              (totalAssetAmount - totalLiabilityAmount) | toThousandFilter(2)
            }}
          </span>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BalanceSheet',
  data() {
    return {
      assets: [],
      liabilities: []
    }
  },
  computed: {
    getAssetTypeNumber() {
      // 因目前只有兩種資產，所以找出第一種資產數量就可以
      return this.assets.filter((item) => item.type === this.assets[0].type)
        .length
    },
    totalAssetAmount() {
      return this.assets.reduce((sum, item) => sum + item.amount, 0)
    },
    totalLiabilityAmount() {
      return this.liabilities.reduce((sum, item) => sum + item.amount, 0)
    }
  },
  created() {
    this.$store.dispatch('GetBalanceList').then((response) => {
      this.assets = response.data.assets
      this.liabilities = response.data.debts
    })
  },
  methods: {
    processAssetTypeSpan({ row, column, rowIndex, columnIndex }) {
      if (columnIndex === 0) {
        if (rowIndex === 0) {
          return {
            rowspan: this.getAssetTypeNumber,
            colspan: 1
          }
        } else if (rowIndex === this.getAssetTypeNumber) {
          return {
            rowspan: this.assets.length - this.getAssetTypeNumber,
            colspan: 1
          }
        }
        return {
          rowspan: 0,
          colspan: 0
        }
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.balance-sheet {
  .up-area {
    width: 100%;
    display: flex;

    & > div {
      width: 50%;

      &:first-child {
        padding-right: 10px;
      }
    }
  }

  .down-area {
    border-top: 1px solid lightgray;
    display: flex;

    & > div {
      width: 50%;
      color: #606266;
      padding-top: 10px;

      &:first-child {
        padding-right: 10px;
      }

      & > p {
        width: 100%;
        padding-right: 10px;
        display: flex;

        span {
          width: 50%;
          text-align: right;
          letter-spacing: 3px;
        }
      }
    }
  }
}
</style>
