<template>
  <div>
    <div>
      <el-button type="primary" @click="openDialog()">新增</el-button>
    </div>
    <el-table :data="queryList" stripe header-cell-class-name="table-header">
      <el-table-column label="名稱" prop="loan_name"/>
      <el-table-column label="關聯帳戶" prop="account_name"/>
      <el-table-column label="利率" prop="interest_rate"/>
      <el-table-column :formatter="formatDateTime" label="申請日期" prop="apply_date" align="center"/>
      <el-table-column label="每月扣款日" prop="pay_day" align="center"/>
      <el-table-column label="排序" prop="loan_index" align="center"/>
      <el-table-column fixed="right" label="操作" width="150" align="center">
        <template slot-scope="scope">
          <el-button type="success" size="small" @click="openDialog(scope.row)">编辑</el-button>
          <el-button type="danger" size="small" @click="deleteLoan(scope.row.loan_id)">刪除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <operating-dialog
      v-if="showDialog"
      :show-dialog="showDialog"
      :raw-data="selectedData"
      @hideDialog="showDialog = false"
    />
  </div>
</template>

<script>
import { mapState } from 'vuex'

import { formatDateTimeSlash } from '@/utils/dateProcess'

import OperatingDialog from './OperatingDialog'

export default {
  components: { OperatingDialog },
  data() {
    return {
      showDialog: false,
      selectedData: {}
    }
  },
  computed: {
    ...mapState({
      queryList: state => state.setting.menu.loan.dataList
    })
  },
  created() {
    this.$store.dispatch('GetLoanList')
  },
  methods: {
    formatDateTime(row, column, cellValue) {
      return formatDateTimeSlash(cellValue)
    },
    hideDialog() {
      this.$emit('hideDialog')
    },
    openDialog(inputData) {
      this.showDialog = true
      this.selectedData = inputData || null
    },
    deleteLoan(id) {
      this.$store.dispatch('DeleteLoanData', id)
    }
  }
}
</script>
