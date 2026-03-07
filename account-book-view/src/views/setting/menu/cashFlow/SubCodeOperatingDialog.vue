<template>
  <el-dialog :visible="showDialog" :show-close="false" append-to-body class="page">
    <div slot="title">
      <span>子選單</span>
      <span class="hint">(因未擋重複名稱與排序，新增時建議先查詢確認)</span>
    </div>
    <el-form label-width="80px">
      <el-form-item label="名稱">
        <el-input v-model="form.name" class="input-medium"/>
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
import { yesNo } from '@/assets/commonData/global'

export default {
  props: {
    showDialog: {
      type: Boolean,
      default: false
    },
    parentData: {
      type: Object,
      default: null
    },
    rawData: {
      type: Object,
      default: () => {}
    }
  },
  data() {
    return {
      form: {},
      yesNo
    }
  },
  watch: {
    rawData(newData) {
      this.form =
        newData.code_id > 0
          ? JSON.parse(JSON.stringify(newData))
          : {
              in_use: 'Y',
              code_index: ''
            }

      this.form.code_group = this.parentData.code_id
      this.form.code_group_name = this.parentData.name
      this.form.code_type = this.parentData.code_type
    }
  },
  methods: {
    hideDialog() {
      this.$emit('hideDialog')
    },
    submitForm() {
      let result = null
      if (this.form.code_id) {
        result = this.$store.dispatch('UpdateSubCodeData', this.form)
      } else result = this.$store.dispatch('AddSubCodeData', this.form)

      result.then(data => {
        this.hideDialog()
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.hint {
  display: block;
  color: red;
  margin-top: 10px;
  font-size: 14px;
}
</style>
