<template>
  <div>
    <div>
      <el-button type="primary" @click="openDialog()">新增</el-button>
    </div>
    <el-table :data="queryList" stripe header-cell-class-name="table-header">
      <el-table-column label="名稱" align="right">
        <template slot-scope="scope">
          <el-button type="text" @click="openDetailDialog(scope.row)">{{
            scope.row.loan_name
          }}</el-button>
        </template>
      </el-table-column>
      <el-table-column
        :formatter="formatDateTime"
        label="貸款日期"
        prop="apply_date"
        align="center"
      />
      <el-table-column
        :formatter="formatDateTime"
        label="寬限到期日期"
        prop="grace_expire_date"
        align="center"
      />
      <el-table-column
        :formatter="mappingName"
        label="類型"
        prop="loan_type"
        align="center"
      />
      <el-table-column label="貸款總金額" prop="amount" align="right" />
      <el-table-column label="剩餘金額" prop="remaining" align="right" />
      <el-table-column label="總花費金額" prop="total_payed" align="right" />
      <el-table-column
        :formatter="mappingYesNo"
        label="是否清償"
        prop="repayed"
        align="center"
      />
      <el-table-column fixed="right" label="操作" width="150" align="center">
        <template slot-scope="scope">
          <el-button
            type="success"
            size="small"
            @click="openDialog(scope.row.loan_id)"
          >
            编辑
          </el-button>
          <el-button
            type="danger"
            size="small"
            @click="deleteLiability(scope.row.loan_id)"
          >
            刪除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <operating-dialog
      v-if="showDialog"
      :show-dialog="showDialog"
      :loan-id="selectedId"
      @hideDialog="showDialog = false"
    />

    <detail-dialog
      :show-dialog="showDetailDialog"
      :parent-data="selectedDetailData"
      @hideDialog="showDetailDialog = false"
    />
  </div>
</template>

<script>
import { mapState } from 'vuex'

import { getMappingName } from '@/utils/codeMapping'
import { formatDateTimeSlash } from '@/utils/dateProcess'

import DetailDialog from './DetailDialog'
import OperatingDialog from './OperatingDialog'

export default {
  components: { DetailDialog, OperatingDialog },
  data() {
    return {
      showDialog: false,
      showDetailDialog: false,
      selectedId: null,
      selectedDetailData: {}
      // selectedData: {}
    }
  },
  computed: {
    ...mapState({
      queryList: (state) => state.otherAssets.liability.liabilityContentList
    })
  },
  mounted() {
    this.$store.dispatch('GetLiabilityList')
  },
  methods: {
    formatDateTime(row, column, cellValue) {
      return formatDateTimeSlash(cellValue)
    },
    mappingYesNo(row, column, cellValue) {
      return getMappingName('yes_no', cellValue)
    },
    mappingName(row, column, cellValue) {
      return getMappingName(column.property, cellValue)
    },
    hideDialog() {
      this.$emit('hideDialog')
    },
    openDialog(loan_id) {
      this.selectedId = loan_id
      this.showDialog = true
      // this.selectedData = inputData || {
      //   grace_expire_date: null,
      //   loan_index: null
      // }
    },
    openDetailDialog(inputData) {
      this.showDetailDialog = true
      this.selectedDetailData = inputData
    },
    deleteLiability(id) {
      this.$confirm('確定要刪除嗎？', '', {
        confirmButtonText: '確定',
        cancelButtonText: '取消'
      })
        .then(() => {
          this.$store.dispatch('DeleteLiabilityData', id)
        })
        .then(() => {
          this.$store.dispatch('GetLiabilityList')
        })
        .catch(() => {})
    }
  }
}
</script>
