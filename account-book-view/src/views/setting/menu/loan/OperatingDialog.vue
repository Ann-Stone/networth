<template>
  <el-dialog :visible="showDialog" :show-close="false" title="貸款">
    <el-form label-width="130px">
      <el-form-item label="貸款名稱">
        <el-input v-model="form.loan_name" class="input-medium" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="連結帳戶">
        <el-select v-model="form.account_id" placeholder="選擇帳戶類別" @change="getAccountName">
          <el-option
            v-for="item in accountSelectList"
            :key="item.key"
            :label="item.value"
            :value="item.key"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="利率">
        <el-input v-model="form.interest_rate" class="input-medium" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="申請日期">
        <el-date-picker v-model="form.apply_date" type="date" placeholder="選擇日期"/>
      </el-form-item>
      <el-form-item label="每月付款日">
        <el-input v-model="form.pay_day" class="input-medium" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="排序">
        <el-input
          v-model="form.loan_index"
          autocomplete="off"
          placeholder="ex:1"
          class="input-small"
        />
      </el-form-item>
    </el-form>
    <div slot="footer" class="dialog-footer">
      <el-button @click="hideDialog">取消</el-button>
      <el-button type="primary" @click="submitForm">確定</el-button>
    </div>
  </el-dialog>
</template>

<script>
import { mapState } from 'vuex'
import moment from 'moment'

import { yesNo } from '@/assets/commonData/global'

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
      form: {},
      yesNo
    }
  },
  computed: {
    ...mapState({
      accountSelectList: state => state.setting.menu.account.accountSelectList
    })
  },
  created() {
    this.$store.dispatch('GetAccountSelection').then(() => {
      if (this.rawData) {
        this.form = JSON.parse(JSON.stringify(this.rawData))
        if (this.form.apply_date) {
          this.form.apply_date = moment(`${this.form.apply_date} UTC`)
        }
      } else {
        this.form = { loan_index: '' }
      }
    })
  },
  methods: {
    hideDialog() {
      this.$emit('hideDialog')
    },
    submitForm() {
      let result = null
      if (this.rawData) {
        result = this.$store.dispatch('UpdateLoanData', this.form)
      } else result = this.$store.dispatch('AddLoanData', this.form)

      result.then(data => {
        this.hideDialog()
      })
    },
    getAccountName(value) {
      this.form.account_name = this.accountSelectList.find(
        item => item.key === value
      ).value
    }
  }
}
</script>
