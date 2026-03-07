<template>
  <el-dialog
    :visible="showDialog"
    :title="parentData.name + ' 子選單'"
    width="80%"
    @close="hideDialog"
  >
    <el-table :data="queryList" stripe header-cell-class-name="table-header">
      <el-table-column label="名稱" prop="name"/>
      <el-table-column :formatter="mappingYesNo" label="是否啟用" prop="in_use" align="center"/>
      <el-table-column label="排序" prop="code_index" align="center"/>
      <el-table-column fixed="right" label="操作" width="150" align="center">
        <template slot-scope="scope">
          <el-button type="success" size="small" @click="openMaintainSubCodeDialog(scope.row)">编辑</el-button>
          <el-button type="danger" size="small" @click="deleteSubCode(scope.row.code_id)">刪除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div slot="footer" class="dialog-footer">
      <el-button type="primary" @click="openMaintainSubCodeDialog()">新增</el-button>
    </div>

    <operating-dialog
      :show-dialog="showMaintainDialog"
      :parent-data="parentData"
      :raw-data="selectedData"
      @hideDialog="showMaintainDialog = false"
    />
  </el-dialog>
</template>

<script>
import OperatingDialog from './SubCodeOperatingDialog'
import { getMappingName } from '@/utils/codeMapping'
import { mapState } from 'vuex'

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
      queryList: state => state.setting.menu.cashFlow.subDataList
    })
  },
  watch: {
    parentData(newData) {
      if (newData.code_id) {
        this.$store.dispatch('GetSubCodeList', newData.code_id)
      }
    }
  },
  methods: {
    mappingYesNo(row, column, cellValue) {
      return getMappingName('yes_no', cellValue)
    },
    hideDialog() {
      this.$emit('hideDialog')
    },
    openMaintainSubCodeDialog(inputData) {
      this.showMaintainDialog = true
      this.selectedData = inputData || {}
    },
    deleteSubCode(id) {
      this.$confirm('確定要刪除嗎？', '', {
        confirmButtonText: '確定',
        cancelButtonText: '取消'
      })
        .then(() => {
          this.$store.dispatch('DeleteSubCodeData', id)
        })
        .catch(() => {})
    }
  }
}
</script>
