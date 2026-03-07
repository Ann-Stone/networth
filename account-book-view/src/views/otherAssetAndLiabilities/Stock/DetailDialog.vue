<template>
  <el-dialog
    :visible="showDialog"
    :title="parentData.stock_name + ' 交易紀錄'"
    width="80%"
    @close="hideDialog"
  >
    <el-button class="right" type="primary" @click="openMaintainDetailDialog()">
      新增
    </el-button>
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
        prop="excute_type"
        align="center"
      />
      <el-table-column label="數量" prop="excute_amount" align="right" />
      <el-table-column label="價格" prop="excute_price" align="right" />
      <el-table-column label="關連帳戶" prop="account_name" align="right" />
      <el-table-column label="交易日誌" prop="memo" align="left" />
      <el-table-column fixed="right" label="操作" width="150" align="center">
        <template slot-scope="scope">
          <el-button
            type="success"
            size="small"
            @click="openMaintainDetailDialog(scope.row)"
          >
            编辑
          </el-button>
          <el-button
            type="danger"
            size="small"
            @click="deleteSubCode(scope.row.distinct_number)"
          >
            刪除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <div slot="footer" class="dialog-footer"/>

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
      queryList: state => state.otherAssets.stockAsset.stockDetailList
    })
  },
  watch: {
    parentData: {
      immediate: true,
      deep: true,
      handler(newData) {
        if (newData.stock_id) {
          this.$store.dispatch('GetStockDetailList', newData.stock_id)
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
        stock_id: this.parentData.stock_id,
        excute_amount: '',
        excute_price: '',
        memo: ''
      }
    },
    closeMaintainDialog(isRefresh) {
      this.showMaintainDialog = false
      if (isRefresh) {
        this.$store.dispatch('GetStockAssetList', this.parentData.asset_id)
      }
    },
    deleteSubCode(id) {
      this.$confirm('確定要刪除嗎？', '', {
        confirmButtonText: '確定',
        cancelButtonText: '取消'
      })
        .then(() => {
          return this.$store.dispatch('DeleteStockDetailData', id)
        })
        .then(() => {
          this.$store.dispatch('GetStockAssetList', this.parentData.asset_id)
        })
        .catch(() => {})
    }
  }
}
</script>

<style lang="scss" scoped>
.right{
  display: block;
  margin-left: auto;
}
</style>
