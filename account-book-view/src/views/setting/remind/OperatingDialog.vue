<template>
  <el-dialog :visible="showDialog" :show-close="false" title="支出提醒">
    <el-form label-width="80px">
      <el-form-item label="日期">
        <el-input
          v-model="form.alarm_date"
          placeholder="mm/dd 或 dd"
          class="input-medium"
          autocomplete="off"
        />
      </el-form-item>
      <el-form-item label="提醒頻率">
        <el-radio-group v-model="form.alarm_type">
          <el-radio label="M">每月</el-radio>
          <el-radio label="Y">每年</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="內容">
        <el-input v-model="form.content" autocomplete="off" />
      </el-form-item>
      <el-form-item label="結束日期">
        <el-date-picker
          v-model="form.due_date"
          type="date"
          placeholder="選擇日期"
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
      form: { due_date: null }
    }
  },
  watch: {
    rawData: {
      immediate: true,
      handler(newData) {
        if (newData) {
          this.form = JSON.parse(JSON.stringify(newData))
          if (this.form.due_date) {
            this.form.due_date = moment(`${this.form.due_date} UTC`)
          }
        } else {
          this.form = { due_date: null }
        }
      }
    }
  },
  methods: {
    hideDialog() {
      this.$emit('hideDialog')
    },
    submitForm() {
      let result = null
      if (this.rawData) {
        result = this.$store.dispatch('UpdateAlarmData', this.form)
      } else result = this.$store.dispatch('AddAlarmData', this.form)

      result.then((data) => {
        this.hideDialog()
      })
    }
  }
}
</script>
