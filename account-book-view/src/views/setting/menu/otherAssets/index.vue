<template>
  <div>
    <div>
      <el-button type="primary" @click="openDialog()">新增</el-button>
    </div>
    <el-table :data="queryList" stripe header-cell-class-name="table-header">
      <el-table-column label="名稱" prop="asset_name" />
      <el-table-column
        :formatter="mappingName"
        label="資產類別"
        prop="asset_type"
      />
      <el-table-column
        label="預計投入總額"
        prop="expected_spend"
        align="center"
      />
      <el-table-column
        :formatter="mappingYesNo"
        label="是否啟用"
        prop="in_use"
        align="center"
      />
      <el-table-column label="排序" prop="asset_index" align="center" />
      <el-table-column fixed="right" label="操作" width="150" align="center">
        <template slot-scope="scope">
          <el-button type="success" size="small" @click="openDialog(scope.row)">
            编辑
          </el-button>
          <el-button
            type="danger"
            size="small"
            @click="deleteOtherAsset(scope.row.asset_id)"
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
  </div>
</template>

<script>
import OperatingDialog from './OperatingDialog'
import { getMappingName } from '@/utils/codeMapping'
import { mapState } from 'vuex'

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
      queryList: state => state.setting.menu.otherAssets.dataList
    })
  },
  created() {
    this.$store.dispatch('GetOtherAssetsList')
  },
  methods: {
    mappingName(row, column, cellValue) {
      return getMappingName(column.property, cellValue)
    },
    mappingYesNo(row, column, cellValue) {
      return getMappingName('yes_no', cellValue)
    },
    hideDialog() {
      this.$emit('hideDialog')
    },
    openDialog(inputData) {
      this.showDialog = true
      this.selectedData = inputData || { asset_index: '', expected_spend: '' }
    },
    deleteOtherAsset(id) {
      this.$confirm('確定要刪除嗎？', '', {
        confirmButtonText: '確定',
        cancelButtonText: '取消'
      })
        .then(() => {
          this.$store.dispatch('DeleteOtherAssetData', id)
        })
        .catch(() => {})
    }
  }
}
</script>
