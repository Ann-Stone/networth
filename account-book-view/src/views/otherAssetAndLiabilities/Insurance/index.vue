<template>
  <div>
    <div>
      <el-button type="primary" @click="openDialog()">新增</el-button>
    </div>
    <el-table :data="queryList" stripe header-cell-class-name="table-header">
      <el-table-column label="名稱" align="right">
        <template slot-scope="scope">
          <el-button type="text" @click="openDetailDialog(scope.row)">{{
            scope.row.insurance_name
          }}</el-button>
        </template>
      </el-table-column>
      <el-table-column
        :formatter="formatDateTime"
        label="購買日期"
        prop="start_date"
        align="center"
      />
      <el-table-column
        :formatter="formatDateTime"
        label="預計到期日"
        prop="expected_end_date"
        align="center"
      />
      <el-table-column
        :formatter="mappingYesNo"
        label="是否贖回"
        prop="has_closed"
        align="center"
      />
      <el-table-column
        label="預計投入金額"
        prop="expected_spend"
        align="right"
      />
      <el-table-column label="實際投入金額" prop="actual_spend" align="right" />
      <el-table-column label="報酬率" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.ROI ? `${scope.row.ROI}%` : '' }}</span>
        </template>
      </el-table-column>
      <!-- <el-table-column label="年化內部報酬率" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.IRR ? `${scope.row.IRR}%` : '' }}</span>
        </template>
      </el-table-column> -->
      <el-table-column label="損益" prop="gain_lose" align="right" />
      <el-table-column fixed="right" label="操作" width="150" align="center">
        <template slot-scope="scope">
          <el-button type="success" size="small" @click="openDialog(scope.row)">
            编辑
          </el-button>
          <el-button
            type="danger"
            size="small"
            @click="deleteInsuranceAsset(scope.row.insurance_id)"
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
      queryList: state => state.otherAssets.insuranceAsset.insuranceContentList
    })
  },
  watch: {
    assetId: {
      immediate: true,
      handler(val) {
        this.$store.dispatch('GetInsurenceAssetList', val)
      }
    }
  },
  methods: {
    formatDateTime(row, column, cellValue) {
      return formatDateTimeSlash(cellValue)
    },
    mappingYesNo(row, column, cellValue) {
      return getMappingName('yes_no', cellValue)
    },
    hideDialog() {
      this.$emit('hideDialog')
    },
    openDialog(inputData) {
      this.showDialog = true
      this.selectedData = inputData || {
        asset_id: this.assetId,
        pay_day: null,
        out_account_id: null
      }
    },
    openDetailDialog(inputData) {
      this.showDetailDialog = true
      this.selectedDetailData = inputData
    },
    deleteInsuranceAsset(id) {
      this.$confirm('確定要刪除嗎？', '', {
        confirmButtonText: '確定',
        cancelButtonText: '取消'
      })
        .then(() => {
          this.$store.dispatch('DeleteInsuranceAssetData', id)
        })
        .catch(() => {})
    }
  }
}
</script>
