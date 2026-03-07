<template>
  <el-dialog
    :visible="showDialog"
    :show-close="false"
    append-to-body
    title="紀錄"
  >
    <el-form label-width="130px">
      <el-form-item label="日期">
        <el-date-picker
          v-model="form.excute_date"
          type="date"
          placeholder="選擇日期"
        />
      </el-form-item>
      <el-form-item label="類型">
        <el-select v-model="form.estate_excute_type" placeholder="選擇類型">
          <el-option
            v-for="item in estateExcuteType"
            :key="item.key"
            :label="item.value"
            :value="item.key"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="金額">
        <el-input
          v-model="form.excute_price"
          autocomplete="off"
          class="input-medium"
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
    </el-form>
    <div slot="footer" class="dialog-footer">
      <el-button @click="hideDialog">取消</el-button>
      <el-button type="primary" @click="submitForm">確定</el-button>
    </div>
  </el-dialog>
</template>

<script>
import moment from 'moment'

import { estateExcuteType } from '@/assets/commonData/otherAssets'

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
      estateExcuteType
    }
  },
  watch: {
    rawData(newData) {
      this.form = JSON.parse(JSON.stringify(newData))
      if (this.form.excute_date) {
        this.form.excute_date = moment(`${this.form.excute_date} UTC`)
      }
    }
  },
  methods: {
    hideDialog(isRefresh = false) {
      this.$emit('hideDialog', isRefresh)
    },
    submitForm() {
      let result = null
      if (this.rawData.distinct_number) {
        result = this.$store.dispatch('UpdateEstateDetailData', this.form)
      } else result = this.$store.dispatch('AddEstateDetailData', this.form)

      result.then((data) => {
        this.hideDialog(true)
      })
    }
  }
}
</script>
