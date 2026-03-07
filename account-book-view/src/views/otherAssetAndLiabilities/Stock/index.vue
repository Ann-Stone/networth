<template>
  <div>
    <div>
      <el-button type="primary" @click="openDialog()">新增</el-button>
    </div>
    <el-table :data="queryList" stripe header-cell-class-name="table-header">
      <el-table-column label="代號" align="center">
        <template slot-scope="scope">
          <el-button type="text" @click="openDetailDialog(scope.row)">{{
            scope.row.stock_code
          }}</el-button>
        </template>
      </el-table-column>
      <el-table-column label="名稱" prop="stock_name" align="right" />
      <el-table-column
        label="預計投入金額"
        prop="expected_spend"
        align="right"
      />
      <el-table-column label="現價" prop="now_price" align="right" />
      <el-table-column label="持有股數" prop="hold_amount" align="right" />
      <!-- <el-table-column label="賣出股數" prop="sold_amount" align="right" /> -->
      <el-table-column label="買均價" prop="actual_buy_price" align="right" />
      <el-table-column label="買均價(含息)" prop="buy_price" align="right" />
      <el-table-column label="賣均價" prop="sold_price" align="right" />
      <el-table-column
        :formatter="formatDateTime"
        label="最初買入時間"
        prop="buy_date"
        align="center"
        width="110"
      />
      <el-table-column
        :formatter="formatDateTime"
        label="最後賣出時間"
        prop="sold_date"
        align="center"
        width="110"
      />
      <el-table-column label="損益" prop="gain_lose" align="right" />
      <el-table-column label="報酬率" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.ROI ? `${scope.row.ROI}%` : '' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="目前殖利率" align="center">
        <template slot-scope="scope">
          <span>{{
            scope.row.dividend_yield ? `${scope.row.dividend_yield}%` : ''
          }}</span>
        </template>
      </el-table-column>
      <el-table-column fixed="right" label="操作" width="150" align="center">
        <template slot-scope="scope">
          <el-button type="success" size="small" @click="openDialog(scope.row)">
            编辑
          </el-button>
          <el-button
            type="danger"
            size="small"
            @click="deleteStockAsset(scope.row.stock_id)"
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
      queryList: (state) => state.otherAssets.stockAsset.stockContentList
    })
  },
  watch: {
    assetId: {
      immediate: true,
      handler(val) {
        this.$store.dispatch('GetStockAssetList', val)
      }
    }
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
      this.selectedData = inputData || { asset_id: this.assetId }
    },
    openDetailDialog(inputData) {
      this.showDetailDialog = true
      this.selectedDetailData = inputData
    },
    deleteStockAsset(id) {
      this.$confirm('確定要刪除嗎？', '', {
        confirmButtonText: '確定',
        cancelButtonText: '取消'
      })
        .then(() => {
          this.$store.dispatch('DeleteStockAssetData', id)
        })
        .catch(() => {})
    }
  }
}
</script>
