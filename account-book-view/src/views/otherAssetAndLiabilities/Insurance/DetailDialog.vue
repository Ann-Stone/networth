<template>
  <el-dialog
    :visible="showDialog"
    :title="parentData.insurance_name + ' 歷史紀錄'"
    width="80%"
    @close="hideDialog"
  >
    <el-table :data="queryList" stripe header-cell-class-name="table-header">
      <el-table-column
        :formatter="formatDateTime"
        label="日期"
        prop="excute_date"
        align="center"
      />
      <el-table-column
        :formatter="mappingName"
        label="類型"
        prop="insurance_excute_type"
        align="center"
      />
      <el-table-column label="金額" prop="excute_price" align="right" />
      <el-table-column label="備註" prop="memo" align="left" />
      <el-table-column fixed="right" label="操作" width="150" align="center">
        <template slot-scope="scope">
          <el-button
            type="success"
            size="small"
            @click="openMaintainDetailDialog(scope.row)"
          >编辑</el-button
          >
          <el-button
            type="danger"
            size="small"
            @click="deleteDetail(scope.row.distinct_number)"
          >刪除</el-button
          >
        </template>
      </el-table-column>
    </el-table>
    <div slot="footer" class="dialog-footer">
      <el-button type="primary" @click="openMaintainDetailDialog()"
      >新增</el-button
      >
    </div>

    <operating-dialog
      :show-dialog="showMaintainDialog"
      :raw-data="selectedData"
      @hideDialog="closeMaintainDialog"
    />
  </el-dialog>
</template>

<script>
import { mapState } from 'vuex'

import { getMappingName } from '@/utils/codeMapping'
import { formatDateTimeSlash } from '@/utils/dateProcess'

import OperatingDialog from './DetailOperatingDialog'

export default {
  components: { OperatingDialog },
  props: {
    showDialog: {
      type: Boolean,
      default: false
    },
    parentData: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      showMaintainDialog: false,
      selectedData: {}
    }
  },
  computed: {
    ...mapState({
      queryList: (state) => state.otherAssets.insuranceAsset.insuranceDetailList
    })
  },
  watch: {
    parentData: {
      immediate: true,
      deep: true,
      handler(newData) {
        if (newData.insurance_id) {
          this.$store.dispatch('GetInsuranceDetailList', newData.insurance_id)
        }
      }
    }
  },
  methods: {
    formatDateTime(row, column, cellValue) {
      return formatDateTimeSlash(cellValue)
    },
    mappingName(row, column, cellValue) {
      return getMappingName(column.property, cellValue)
    },
    hideDialog() {
      this.$emit('hideDialog')
    },
    openMaintainDetailDialog(inputData) {
      this.showMaintainDialog = true
      this.selectedData = inputData || {
        insurance_id: this.parentData.insurance_id,
        excute_amount: '',
        excute_price: '',
        memo: ''
      }
    },
    closeMaintainDialog(isRefresh) {
      this.showMaintainDialog = false
      if (isRefresh) {
        this.$store.dispatch('GetInsuranceAssetList', this.parentData.asset_id)
      }
    },
    deleteDetail(id) {
      this.$confirm('確定要刪除嗎？', '', {
        confirmButtonText: '確定',
        cancelButtonText: '取消'
      })
        .then(() => {
          return this.$store.dispatch('DeleteInsuranceDetailData', id)
        })
        .then(() => {
          this.$store.dispatch(
            'GetInsuranceAssetList',
            this.parentData.asset_id
          )
        })
        .catch(() => {})
    }
  }
}
</script>
