<template>
  <div class="page remind-setting">
    <search-area>
      <el-form slot="content">
        <el-form-item label="提醒日期">
          <el-input
            v-model="conditions.date"
            placeholder="mm/dd 或 dd"
            class="input-medium"
          />
        </el-form-item>
        <el-form-item class="last">
          <el-button type="primary" class="btn-medium" @click="search"
          >搜尋</el-button
          >
          <el-button type="primary" class="btn-medium" @click="openDialog()"
          >新增</el-button
          >
        </el-form-item>
      </el-form>
    </search-area>
    <el-table
      v-show="showList"
      :data="queryList"
      stripe
      header-cell-class-name="table-header"
    >
      <el-table-column
        label="日期"
        prop="alarm_date"
        width="60"
        align="center"
      />
      <el-table-column label="內容" prop="content" />
      <el-table-column
        :formatter="formatDateTime"
        label="到期日"
        prop="due_date"
        align="center"
      />
      <el-table-column fixed="right" label="操作" width="150" align="center">
        <template slot-scope="scope">
          <el-button type="success" size="small" @click="openDialog(scope.row)"
          >编辑</el-button
          >
          <el-button
            type="danger"
            size="small"
            @click="deleteAlarm(scope.row.alarm_id)"
          >刪除</el-button
          >
        </template>
      </el-table-column>
    </el-table>

    <operating-dialog
      v-if="showDialog"
      :show-dialog="showDialog"
      :raw-data="selectedData"
      @hideDialog="showDialog = false"
    />
  </div>
</template>

<script>
import { mapState } from 'vuex'

import SearchArea from '@/components/SearchArea'
import { formatDateTimeSlash } from '@/utils/dateProcess'

import OperatingDialog from './OperatingDialog'

export default {
  name: 'RemindSetting',
  components: { OperatingDialog, SearchArea },
  data() {
    return {
      showDialog: false,
      showList: false,
      conditions: {
        date: ''
      },
      selectedData: {}
    }
  },
  computed: {
    ...mapState({
      queryList: (state) => state.setting.alarm.dataList
    })
  },
  methods: {
    formatDateTime(row, column, cellValue) {
      return formatDateTimeSlash(cellValue)
    },
    search() {
      this.$store
        .dispatch('GetAlarmList', this.conditions)
        .then(() => {
          this.showList = true
        })
        .catch(() => {
          this.showList = false
        })
    },
    deleteAlarm(id) {
      this.$confirm('確定要刪除嗎？', '', {
        confirmButtonText: '確定',
        cancelButtonText: '取消'
      })
        .then(() => {
          this.$store.dispatch('DeleteAlarmData', id)
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

