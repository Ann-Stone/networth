<template>
  <el-dialog :visible="showDialog" :show-close="false" title="保險資產">
    <el-form label-width="130px">
      <el-form-item label="名稱">
        <el-input
          v-model="form.insurance_name"
          :disabled="!!form.insurance_id"
          autocomplete="off"
          class="input-medium"
        />
      </el-form-item>
      <el-form-item label="購買日期">
        <el-date-picker
          v-model="form.start_date"
          :disabled="!!form.insurance_id"
          type="date"
          placeholder="選擇日期"
        />
      </el-form-item>
      <el-form-item label="繳別">
        <el-select v-model="form.pay_type" placeholder="選擇繳別">
          <el-option
            v-for="item in insurancePayType"
            :key="item.key"
            :label="item.value"
            :value="item.key"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="繳費日期">
        <el-input
          v-model="form.pay_day"
          autocomplete="off"
          placeholder="月:dd/ 季:mm/dd,mm/dd.../ 年:mm/dd/ 躉:免填"
        />
      </el-form-item>
      <el-form-item label="預計到期日">
        <el-date-picker
          v-model="form.expected_end_date"
          :disabled="!!form.insurance_id"
          type="date"
          placeholder="選擇日期"
        />
      </el-form-item>
      <el-form-item label="預計投入總額">
        <el-input
          v-model="form.expected_spend"
          :disabled="!!form.insurance_id"
          class="input-medium"
          autocomplete="off"
        />
      </el-form-item>
      <el-form-item label="入金帳戶">
        <el-select
          v-model="form.in_account_id"
          placeholder="選擇帳戶類別"
          @change="value => getAccountName(value, 'in')"
        >
          <el-option
            v-for="item in accountSelectList"
            :key="item.key"
            :label="item.value"
            :value="item.key"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="出金帳戶">
        <el-select
          v-model="form.out_account_id"
          placeholder="選擇帳戶類別"
          @change="value => getAccountName(value, 'out')"
        >
          <el-option
            v-for="item in accountSelectList"
            :key="item.key"
            :label="item.value"
            :value="item.key"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="是否結束">
        <el-radio-group v-model="form.has_closed">
          <el-radio v-for="item in yesNo" :key="item.key" :label="item.key">{{
            item.value
          }}</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>
    <div slot="footer" class="dialog-footer">
      <el-button @click="hideDialog">取消</el-button>
      <el-button type="primary" @click="submitForm">確定</el-button>
    </div>
  </el-dialog>
</template>

<script>
import { yesNo } from '@/assets/commonData/global'
import { insurancePayType } from '@/assets/commonData/otherAssets'
import { mapState } from 'vuex'

export default {
  props: {
    showDialog: {
      type: Boolean,
      default: false
    },
    rawData: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      insurancePayType,
      yesNo,
      form: { asset_id: null, out_account_id: null }
    }
  },
  computed: {
    ...mapState({
      accountSelectList: state => state.setting.menu.account.accountSelectList
    })
  },
  watch: {
    rawData(newData) {
      this.form = JSON.parse(JSON.stringify(newData))
    }
  },
  methods: {
    hideDialog() {
      this.$emit('hideDialog')
    },
    submitForm() {
      let result = null
      if (this.form.insurance_id) {
        result = this.$store.dispatch('UpdateInsuranceAssetData', this.form)
      } else result = this.$store.dispatch('AddInsuranceAssetData', this.form)

      result.then(data => {
        this.hideDialog()
      })
    },
    getAccountName(value, type) {
      const account_name = this.accountSelectList.find(
        item => item.key === value
      ).value

      if (type === 'in') {
        this.form.in_account_name = account_name

        this.form.out_account_id = value
        this.form.out_account_name = account_name
      } else {
        this.form.out_account_name = account_name
      }
    }
  }
}
</script>
