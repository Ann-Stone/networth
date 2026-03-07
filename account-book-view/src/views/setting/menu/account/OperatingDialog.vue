<template>
  <el-dialog :visible="showDialog" :show-close="false" title="帳戶">
    <el-form label-width="130px">
      <el-form-item label="帳號">
        <el-input
          v-model="form.account_id"
          class="input-medium"
          autocomplete="off"
        />
      </el-form-item>
      <el-form-item label="帳戶名稱">
        <el-input v-model="form.name" class="input-medium" autocomplete="off" />
      </el-form-item>
      <el-form-item label="帳戶類別">
        <el-select v-model="form.account_type" placeholder="選擇帳戶類別">
          <el-option
            v-for="item in accountType"
            :key="item.key"
            :label="item.value"
            :value="item.key"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="幣別">
        <el-select v-model="form.fx_code" placeholder="選擇幣別">
          <el-option
            v-for="item in fxCode"
            :key="item.key"
            :label="item.value"
            :value="item.key"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="持有人">
        <el-input
          v-model="form.owner"
          class="input-medium"
          autocomplete="off"
        />
      </el-form-item>
      <el-form-item label="電子發票載具號碼">
        <el-input
          v-model="form.carrier_no"
          class="input-medium"
          autocomplete="off"
        />
      </el-form-item>
      <el-form-item label="是否列入總資產">
        <el-radio-group v-model="form.is_calculate">
          <el-radio v-for="item in yesNo" :key="item.key" :label="item.key">{{
            item.value
          }}</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="是否啟用">
        <el-radio-group v-model="form.in_use">
          <el-radio v-for="item in yesNo" :key="item.key" :label="item.key">{{
            item.value
          }}</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="手續費折數">
        <el-input
          v-model="form.discount"
          autocomplete="off"
          placeholder="ex:0.6"
          class="input-small"
        />
      </el-form-item>
      <el-form-item label="備註">
        <el-input
          v-model="form.memo"
          :rows="3"
          autocomplete="off"
          type="textarea"
        />
      </el-form-item>
      <el-form-item label="排序">
        <el-input
          v-model="form.account_index"
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
import { accountType } from '@/assets/commonData/accountData'
import { feedbackWay } from '@/assets/commonData/creditCardData'
import { fxCode } from '@/assets/commonData/fxData'
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
      accountType,
      feedbackWay,
      fxCode: fxCode.filter((x) => x.inUse),
      yesNo
    }
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
      if (this.rawData.id) {
        result = this.$store.dispatch('UpdateAccountData', this.form)
      } else result = this.$store.dispatch('AddAccountData', this.form)

      result.then((data) => {
        this.$store.dispatch('GetAccountSelection')
        this.hideDialog()
      })
    }
  }
}
</script>
