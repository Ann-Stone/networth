<template>
  <div class="account-setting">
    <search-area>
      <el-form slot="content">
        <el-form-item label="帳戶名稱">
          <el-input v-model="conditions.name" class="input-medium" />
        </el-form-item>
        <el-form-item label="帳戶類別">
          <el-select
            v-model="conditions.account_type"
            placeholder="選擇帳戶類別"
          >
            <el-option
              v-for="item in accountType"
              :key="item.key"
              :label="item.value"
              :value="item.key"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="是否啟用">
          <el-radio-group v-model="conditions.in_use">
            <el-radio v-for="item in yesNo" :key="item.key" :label="item.key">{{
              item.value
            }}</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item class="last">
          <el-button type="primary" class="btn-medium" @click="search">
            搜尋
          </el-button>
          <el-button type="primary" class="btn-medium" @click="openDialog()">
            新增
          </el-button>
        </el-form-item>
      </el-form>
    </search-area>
    <el-table
      v-show="showList"
      :data="queryList"
      stripe
      header-cell-class-name="table-header"
    >
      <el-table-column label="帳號" prop="account_id" />
      <el-table-column label="帳戶名稱" prop="name" />
      <el-table-column
        :formatter="mappingName"
        label="帳戶類別"
        prop="account_type"
        align="center"
      />
      <el-table-column
        :formatter="mappingName"
        label="幣別"
        prop="fx_code"
        align="center"
      />
      <el-table-column
        :formatter="mappingYesNo"
        label="是否列入總資產"
        prop="is_calculate"
        align="center"
      />
      <el-table-column
        :formatter="mappingYesNo"
        label="是否啟用"
        prop="in_use"
        align="center"
      />
      <el-table-column label="手續費折數" prop="discount" align="center" />
      <el-table-column label="備註" prop="memo" />
      <el-table-column label="排序" prop="account_index" align="center" />
      <el-table-column fixed="right" label="操作" width="150" align="center">
        <template slot-scope="scope">
          <el-button type="success" size="small" @click="openDialog(scope.row)">
            编辑
          </el-button>
          <el-button
            type="danger"
            size="small"
            @click="deleteAccount(scope.row.id)"
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
import { accountType } from '@/assets/commonData/accountData'
import { yesNo } from '@/assets/commonData/global'
import SearchArea from '@/components/SearchArea'
import OperatingDialog from './OperatingDialog'
import { getMappingName } from '@/utils/codeMapping'
import { mapState } from 'vuex'

export default {
  name: 'AccountSetting',
  components: { OperatingDialog, SearchArea },
  data() {
    return {
      showDialog: false,
      showList: false,
      conditions: {
        name: '',
        account_type: '',
        in_use: ''
      },
      selectedData: {},
      accountType,
      yesNo
    }
  },
  computed: {
    ...mapState({
      queryList: state => state.setting.menu.account.dataList
    })
  },
  methods: {
    mappingName(row, column, cellValue) {
      return getMappingName(column.property, cellValue)
    },
    mappingYesNo(row, column, cellValue) {
      return getMappingName('yes_no', cellValue)
    },
    search() {
      this.$store
        .dispatch('GetAccountList', this.conditions)
        .then(() => {
          this.showList = true
        })
        .catch(() => {
          this.showList = false
        })
    },
    deleteAccount(id) {
      this.$confirm('確定要刪除嗎？', '', {
        confirmButtonText: '確定',
        cancelButtonText: '取消'
      })
        .then(() => {
          this.$store.dispatch('DeleteAccountData', id)
        })
        .catch(() => {})
    },
    openDialog(rawData) {
      this.showDialog = true
      this.selectedData = rawData || { discount: null, account_index: null }
    }
  }
}
</script>
