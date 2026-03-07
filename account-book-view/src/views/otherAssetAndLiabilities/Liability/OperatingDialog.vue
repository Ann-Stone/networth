<template>
  <el-dialog :visible="showDialog" :show-close="false" title="貸款">
    <el-form label-width="130px">
      <el-form-item label="名稱">
        <el-input
          v-model="form.loan_name"
          autocomplete="off"
          class="input-medium"
        />
      </el-form-item>
      <el-form-item label="類別">
        <el-select v-model="form.loan_type" placeholder="選擇類別">
          <el-option
            v-for="item in loanType"
            :key="item.key"
            :label="item.value"
            :value="item.key"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="扣款帳戶">
        <el-select
          v-model="form.account_id"
          placeholder="選擇帳戶"
          @change="getAccountName"
        >
          <el-option
            v-for="item in accountSelectList"
            :key="item.key"
            :label="item.value"
            :value="item.key"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="利率">
        <el-input
          v-model="form.interest_rate"
          autocomplete="off"
          placeholder="ex:1.31"
          class="input-small"
        />
      </el-form-item>
      <el-form-item label="年限">
        <el-input
          v-model="form.period"
          class="input-medium"
          autocomplete="off"
        />
      </el-form-item>
      <el-form-item label="貸款起始日期">
        <el-date-picker
          v-model="form.apply_date"
          type="date"
          placeholder="選擇日期"
        />
      </el-form-item>
      <el-form-item label="寬限到期日期">
        <el-date-picker
          v-model="form.grace_expire_date"
          type="date"
          placeholder="選擇日期"
        />
      </el-form-item>
      <el-form-item label="繳費日期">
        <el-input
          v-model="form.pay_day"
          autocomplete="off"
          placeholder="每月幾號"
        />
      </el-form-item>
      <el-form-item label="借款金額">
        <el-input
          v-model="form.amount"
          class="input-medium"
          autocomplete="off"
        />
      </el-form-item>
      <el-form-item label="是否清償">
        <el-radio-group v-model="form.repayed">
          <el-radio v-for="item in yesNo" :key="item.key" :label="item.key">{{
            item.value
          }}</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="排序">
        <el-input
          v-model.number="form.loan_index"
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
import moment from 'moment'
import { mapState } from 'vuex'

import { yesNo } from '@/assets/commonData/global'
import { loanType } from '@/assets/commonData/liability'

export default {
  props: {
    showDialog: {
      type: Boolean,
      default: false
    },
    loanId: {
      type: Number,
      default: null
    }
  },
  data() {
    return {
      loanType,
      yesNo,
      form: {
        loan_index: null
      }
    }
  },
  computed: {
    ...mapState({
      accountSelectList: state => state.setting.menu.account.accountSelectList
    })
  },
  // watch: {
  //   rawData(newData) {
  //     this.form = JSON.parse(JSON.stringify(newData))
  //   }
  // },
  created() {
    if (this.loanId) {
      this.$store.dispatch('GetLiabilityById', this.loanId).then(response => {
        this.form = response.data
        this.form.apply_date = moment(this.form.apply_date)
        this.form.grace_expire_date = moment(this.form.grace_expire_date)
      })
    }
  },
  methods: {
    hideDialog() {
      this.$emit('hideDialog')
    },
    submitForm() {
      let result = null
      if (this.loanId) {
        result = this.$store.dispatch('UpdateLiabilityData', this.form)
      } else result = this.$store.dispatch('AddLiabilityData', this.form)

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
