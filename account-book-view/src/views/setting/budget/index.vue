<template>
  <div class="page budget-setting">
    <div>
      <el-button
        type="primary"
        class="btn-medium"
        @click="isEditMode = !isEditMode"
      >{{ getEditButtonText }}</el-button
      >
      <el-button type="danger" class="btn-large" @click="createNextYearBudget"
      >建立下一年度預算</el-button
      >
      <span class="fr">
        年度：
        <el-input-number
          v-model="thisYear"
          :min="yearRange.min"
          :max="yearRange.max"
          @change="search"
        />
      </span>
    </div>
    <p>浮動支出：</p>
    <list-table :is-edit-mode="isEditMode" :raw-data="floatingList" />
    <p>固定支出：</p>
    <list-table :is-edit-mode="isEditMode" :raw-data="stableList" />
  </div>
</template>

<script>
import { mapState } from 'vuex'
import ListTable from './ListTableComponent'
import SearchArea from '@/components/SearchArea'

export default {
  name: 'BudgetSetting',
  components: { ListTable, SearchArea },
  data() {
    return {
      isEditMode: false,
      thisYear: 0
    }
  },
  computed: {
    ...mapState({
      yearRange: (state) => state.setting.budget.yearRange,
      floatingList: (state) => state.setting.budget.dataList.floatingList,
      stableList: (state) => state.setting.budget.dataList.stableList
    }),
    getEditButtonText() {
      return this.isEditMode ? '送出' : '編輯'
    }
  },
  created() {
    this.$store.dispatch('GetBudgetRange').then(() => {
      this.thisYear = this.yearRange.max
      this.search()
    })
  },
  methods: {
    search() {
      this.$store.dispatch('GetBudgetList', this.thisYear)
    },
    createNextYearBudget() {
      this.$confirm(
        '將建立資料庫最大年度下一年的預算，確定要執行此操作？',
        '',
        {
          confirmButtonText: '確定',
          cancelButtonText: '取消'
        }
      )
        .then(() => {
          this.$store.dispatch('BulkInsertBudget', this.thisYear + 1)
        })
        .catch(() => {})
    }
  }
}
</script>

