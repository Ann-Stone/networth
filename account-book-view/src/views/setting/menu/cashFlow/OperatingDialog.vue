<template>
  <el-dialog :visible="showDialog" :show-close="false">
    <div slot="title">
      <span>主選單</span>
      <span class="hint">(因未擋重複名稱與排序，新增時建議先查詢確認)</span>
    </div>
    <el-form label-width="80px">
      <el-form-item label="代碼類別">
        <span v-if="form.code_type === 'A'">{{ getMappingName('code_type', form.code_type) }}</span>
        <el-select v-else v-model="form.code_type" placeholder="選擇代碼類別">
          <el-option
            v-for="item in codeType.filter(x => x.addable)"
            :key="item.key"
            :label="item.value"
            :value="item.key"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="名稱">
        <el-input :disabled="!!rawData.code_id" v-model="form.name" class="input-medium"/>
      </el-form-item>
      <el-form-item label="是否啟用">
        <el-radio-group v-model="form.in_use">
          <el-radio v-for="item in yesNo" :key="item.key" :label="item.key">{{ item.value }}</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="排序">
        <el-input
          v-model="form.code_index"
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
import { codeType } from '@/assets/commonData/codeData'
import { yesNo } from '@/assets/commonData/global'
import { getMappingName } from '@/utils/codeMapping'

export default {
  props: {
    showDialog: {
      type: Boolean,
      default: false
    },
    rawData: {
      type: Object,
      default: () => {}
    }
  },
  data() {
    return {
      form: {},
      codeType,
      yesNo
    }
  },
  watch: {
    rawData(newData) {
      this.form =
        newData.code_id > 0
          ? JSON.parse(JSON.stringify(newData))
          : { in_use: 'Y', code_index: '' }
    }
  },
  methods: {
    getMappingName,
    hideDialog() {
      this.$emit('hideDialog')
    },
    submitForm() {
      let result = null
      if (this.form.code_id) {
        result = this.$store.dispatch('UpdateMainCodeData', this.form)
      } else result = this.$store.dispatch('AddMainCodeData', this.form)

      result.then(data => {
        this.hideDialog()
      })
    }
  }
}
</script>
