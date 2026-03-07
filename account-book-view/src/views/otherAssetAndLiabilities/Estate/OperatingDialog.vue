<template>
  <el-dialog :visible="showDialog" :show-close="false" title="不動產">
    <el-form label-width="130px">
      <el-form-item label="名稱">
        <el-input
          v-model="form.estate_name"
          autocomplete="off"
          class="input-medium"
        />
      </el-form-item>
      <el-form-item label="類別">
        <el-select v-model="form.estate_type" placeholder="選擇類別">
          <el-option
            v-for="item in estateType"
            :key="item.key"
            :label="item.value"
            :value="item.key"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="地址">
        <el-input v-model="form.estate_address" autocomplete="off" />
      </el-form-item>
      <el-form-item label="獲得日期">
        <el-date-picker
          v-model="form.obtain_date"
          type="date"
          placeholder="選擇日期"
        />
      </el-form-item>
      <!-- <el-form-item label="頭期款">
        <el-input
          v-model="form.down_payment"
          class="input-medium"
          autocomplete="off"
        />
      </el-form-item> -->
      <el-form-item label="貸款">
        <el-select v-model="form.loan_id" placeholder="選擇對應貸款">
          <el-option
            v-for="item in loanSelectList"
            :key="item.key"
            :label="item.value"
            :value="item.key"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="狀態">
        <el-select v-model="form.estate_status" placeholder="選擇狀態">
          <el-option
            v-for="item in estateStatus"
            :key="item.key"
            :label="item.value"
            :value="item.key"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="備註">
        <el-input
          v-model="form.memo"
          :rows="3"
          autocomplete="off"
          type="textarea"
          placeholder="記錄坪數/建造日/總樓高/有什麼車位/格局/有無管理"
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

import { estateType, estateStatus } from '@/assets/commonData/otherAssets'
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
      estateType,
      estateStatus,
      form: {}
    }
  },
  computed: {
    ...mapState({
      loanSelectList: state => state.otherAssets.liability.loanSelectList
    })
  },
  watch: {
    rawData(newData) {
      if (newData) {
        this.form = JSON.parse(JSON.stringify(newData))
        if (this.form.obtain_date) {
          this.form.obtain_date = moment(`${this.form.obtain_date} UTC`)
        }
      }
    }
  },
  created() {
    this.$store.dispatch('GetLoanSelection')
  },
  methods: {
    hideDialog() {
      this.$emit('hideDialog')
    },
    submitForm() {
      let result = null
      if (this.form.estate_id) {
        result = this.$store.dispatch('UpdateEstateAssetData', this.form)
      } else result = this.$store.dispatch('AddEstateAssetData', this.form)

      result.then(data => {
        this.$store.dispatch('GetEstateAssetList', this.rawData.asset_id)
        this.hideDialog()
      })
    }
  }
}
</script>
