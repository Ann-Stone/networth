<template>
  <div class="credit-card-setting">
    <search-area>
      <el-form slot="content">
        <el-form-item label="信用卡名稱">
          <el-input v-model="conditions.card_name" class="input-medium" />
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
      <el-table-column label="信用卡名稱" prop="card_name" />
      <el-table-column
        label="後四碼"
        prop="card_no"
        header-align="center"
        align="right"
      />
      <el-table-column label="結帳日" prop="last_day" align="center" />
      <el-table-column label="扣款日" prop="charge_day" align="center" />
      <el-table-column
        :formatter="formatDateTime"
        label="到期日"
        prop="limit_date"
        align="center"
      />
      <el-table-column
        :formatter="mappingName"
        label="回饋方式"
        prop="feedback_way"
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
        label="是否啟用"
        prop="in_use"
        align="center"
      />
      <el-table-column label="排序" prop="credit_card_index" align="center" />
      <el-table-column label="備註" prop="note" width="300px" />
      <el-table-column fixed="right" label="操作" width="150" align="center">
        <template slot-scope="scope">
          <el-button type="success" size="small" @click="openDialog(scope.row)">
            编辑
          </el-button>
          <el-button
            type="danger"
            size="small"
            @click="deleteCreditCard(scope.row.credit_card_id)"
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
import { yesNo } from '@/assets/commonData/global'
import SearchArea from '@/components/SearchArea'
import OperatingDialog from './OperatingDialog'
import { getMappingName } from '@/utils/codeMapping'
import { formatDateTimeSlash } from '@/utils/dateProcess'
import { mapState } from 'vuex'

export default {
  name: 'CreditCardSetting',
  components: { OperatingDialog, SearchArea },
  data() {
    return {
      showDialog: false,
      showList: false,
      conditions: {
        card_name: '',
        in_use: ''
      },
      selectedData: {},
      yesNo
    }
  },
  computed: {
    ...mapState({
      queryList: (state) => state.setting.menu.creditCard.dataList
    })
  },
  methods: {
    formatDateTime(row, column, cellValue) {
      return formatDateTimeSlash(cellValue)
    },
    mappingName(row, column, cellValue) {
      return getMappingName(column.property, cellValue)
    },
    mappingYesNo(row, column, cellValue) {
      return getMappingName('yes_no', cellValue)
    },
    search() {
      this.$store
        .dispatch('GetCreditCardList', this.conditions)
        .then(() => {
          this.showList = true
        })
        .catch(() => {
          this.showList = false
        })
    },
    deleteCreditCard(id) {
      this.$confirm('確定要刪除嗎？', '', {
        confirmButtonText: '確定',
        cancelButtonText: '取消'
      })
        .then(() => {
          this.$store.dispatch('DeleteCreditCardData', id)
        })
        .catch(() => {})
    },
    openDialog(rawData) {
      this.showDialog = true
      this.selectedData = rawData || null
    }
  }
}
</script>
