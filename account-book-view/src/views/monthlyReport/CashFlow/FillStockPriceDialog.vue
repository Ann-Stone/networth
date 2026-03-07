<template>
  <el-dialog
    :visible="showDialog"
    :title="`手動補 ${thisMonth} 股票資料`"
    width="80%"
    @close="hideDialog"
  >
    <el-table :data="queryList" stripe header-cell-class-name="table-header">
      <el-table-column :formatter="formatDateTime" label="日期" align="center">
        <template slot-scope="scope">
          <span v-if="!scope.row.editable">
            {{ scope.row.fetch_date | formatDate }}
          </span>
          <el-date-picker
            v-else
            v-model="scope.row.fetch_date"
            :picker-options="pickerOptions"
            :default-value="defaultDate"
            value-format="yyyy-MM-dd 00:00:00"
            type="date"
            placeholder="選擇日期"
            class="input-medium"
        /> </template
      ></el-table-column>
      <el-table-column label="名稱" prop="stock_code" align="center" />
      <el-table-column label="開" align="right">
        <template slot-scope="scope">
          <span v-if="!scope.row.editable">
            {{ scope.row.open_price }}
          </span>
          <el-input
            v-else
            v-model.number="scope.row.open_price"
            autocomplete="off"
          />
        </template>
      </el-table-column>
      <el-table-column label="高" align="right">
        <template slot-scope="scope">
          <span v-if="!scope.row.editable">
            {{ scope.row.highest_price }}
          </span>
          <el-input
            v-else
            v-model.number="scope.row.highest_price"
            autocomplete="off"
          />
        </template>
      </el-table-column>
      <el-table-column label="低" align="right">
        <template slot-scope="scope">
          <span v-if="!scope.row.editable">
            {{ scope.row.lowest_price }}
          </span>
          <el-input
            v-else
            v-model.number="scope.row.lowest_price"
            autocomplete="off"
          />
        </template>
      </el-table-column>
      <el-table-column label="收" align="right">
        <template slot-scope="scope">
          <span v-if="!scope.row.editable">
            {{ scope.row.close_price }}
          </span>
          <el-input
            v-else
            v-model.number="scope.row.close_price"
            autocomplete="off"
          />
        </template>
      </el-table-column>
      <el-table-column fixed="right" label="操作" width="150" align="center">
        <template slot-scope="scope">
          <el-button
            v-if="scope.row.editable"
            type="success"
            size="small"
            @click="addStockPrice(scope.row)"
          >
            新增
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <div slot="footer" class="dialog-footer">
      <el-button type="primary" @click="checkLastStockPrice">
        線上取得股價
      </el-button>
    </div>
  </el-dialog>
</template>

<script>
import moment from 'moment'

import { formatDateTimeSlash } from '@/utils/dateProcess'

export default {
  props: {
    showDialog: {
      type: Boolean,
      default: false
    },
    thisMonth: {
      type: String,
      default: ''
    },
    defaultDate: {
      type: Date,
      default: new Date()
    }
  },
  data() {
    return {
      showMaintainDialog: false,
      pickerOptions: {
        disabledDate: this.disabledDate
      },
      selectedData: {},
      queryList: []
    }
  },
  watch: {
    thisMonth: {
      immediate: true,
      handler(newData) {
        if (newData) {
          this.$store
            .dispatch('GetStockPriceList', newData)
            .then((response) => {
              this.queryList = response.data
            })
        }
      }
    }
  },
  methods: {
    disabledDate(time) {
      return (
        moment(time).format('YYYYMM') < this.thisMonth ||
        moment(time).format('YYYYMM') > this.thisMonth
      )
    },
    formatDateTime(row, column, cellValue) {
      return formatDateTimeSlash(cellValue)
    },
    hideDialog() {
      this.$emit('hideDialog')
    },
    addStockPrice(data) {
      this.$store.dispatch('AddStockPrice', data).then((response) => {
        if (response) data.editable = false
      })
    },
    checkLastStockPrice() {
      this.$store.dispatch('CheckData', {
        type: 'stock',
        data: { period: this.thisMonth }
      })
    }
  }
}
</script>
