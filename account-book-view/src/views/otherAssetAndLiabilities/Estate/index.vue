<template>
  <div>
    <div>
      <el-button type="primary" @click="openDialog()">新增</el-button>
    </div>
    <el-table :data="queryList" stripe header-cell-class-name="table-header">
      <el-table-column label="名稱" align="right">
        <template slot-scope="scope">
          <el-button type="text" @click="openDetailDialog(scope.row)">{{
            scope.row.estate_name
          }}</el-button>
        </template>
      </el-table-column>
      <el-table-column
        :formatter="formatDateTime"
        label="取得日期"
        prop="obtain_date"
        align="center"
      />
      <el-table-column
        :formatter="mappingName"
        label="類型"
        prop="estate_type"
        align="center"
      />
      <el-table-column label="地址" prop="estate_address" align="right" />
      <el-table-column label="貸款" prop="loan_name" align="right" />
      <!-- <el-table-column label="初始本金" prop="down_payment" align="right" /> -->
      <el-table-column label="目前總花費" prop="cost" align="right" />
      <el-table-column label="平均月現金流" prop="profit" align="right" />
      <el-table-column
        :formatter="mappingName"
        label="狀態"
        prop="estate_status"
        align="center"
      />
      <el-table-column fixed="right" label="操作" width="150" align="center">
        <template slot-scope="scope">
          <el-button type="success" size="small" @click="openDialog(scope.row)">
            编辑
          </el-button>
          <el-button
            type="danger"
            size="small"
            @click="deleteEstateAsset(scope.row.estate_id)"
          >
            刪除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <operating-dialog
      :show-dialog="showDialog"
      :raw-data="selectedData"
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
  props: {
    assetId: {
      type: Number,
      default: 0
    }
  },
  data() {
    return {
      showDialog: false,
      showDetailDialog: false,
      selectedDetailData: {},
      selectedData: {}
    }
  },
  computed: {
    ...mapState({
      queryList: state => state.otherAssets.estateAsset.estateContentList
    })
  },
  watch: {
    assetId: {
      immediate: true,
      handler(val) {
        this.$store.dispatch('GetEstateAssetList', val)
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
    openDialog(inputData) {
      this.showDialog = true
      this.selectedData = inputData || {
        asset_id: this.assetId,
        pay_day: null,
        memo: null
      }
    },
    openDetailDialog(inputData) {
      this.showDetailDialog = true
      this.selectedDetailData = inputData
    },
    deleteEstateAsset(id) {
      this.$confirm('確定要刪除嗎？', '', {
        confirmButtonText: '確定',
        cancelButtonText: '取消'
      })
        .then(() => {
          this.$store.dispatch('DeleteEstateAssetData', id)
        })
        .catch(() => {})
    }
  }
}
</script>
