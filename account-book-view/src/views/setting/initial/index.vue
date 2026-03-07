<template>
  <div class="page initial-setting">
    <search-area>
      <el-form slot="content">
        <el-form-item label="類別">
          <el-select
            v-model="conditions.initial_type"
            placeholder="選擇類別"
          >
            <el-option
              v-for="item in assetType"
              :key="item.key"
              :label="item.value"
              :value="item.key"
            />
          </el-select>
        </el-form-item>
        <el-form-item class="last">
          <el-button
            type="primary"
            class="btn-medium"
            @click="search"
          >搜尋</el-button>
          <el-button
            type="primary"
            class="btn-medium"
            @click="showDialog = true"
          >新增</el-button>
          <el-button
            v-show="showList"
            type="primary"
            class="btn-medium"
            @click="doAction"
          >{{ getEditButtonText }}</el-button>
        </el-form-item>
      </el-form>
    </search-area>
    <el-table
      v-show="showList"
      :data="listData"
      stripe
      header-cell-class-name="table-header"
    >
      <el-table-column
        label="名稱"
        prop="code_name"
        width="100"
      />
      <el-table-column
        :formatter="mappingName"
        label="類別"
        prop="initial_type"
        align="center"
      />
      <el-table-column label="初始值">
        <template slot-scope="scope">
          <span v-if="!isEditMode">{{ scope.row.setting_value }}</span>
          <el-input
            v-else
            v-model="scope.row.setting_value"
            autocomplete="off"
          />
        </template>
      </el-table-column>
      <el-table-column
        fixed="right"
        label="操作"
        width="150"
        align="center"
      >
        <template slot-scope="scope">
          <el-button
            type="danger"
            size="small"
            @click="deleteInitial(scope.row)"
          >刪除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <operating-dialog
      :show-dialog="showDialog"
      @hideDialog="showDialog = false"
    />
  </div>
</template>

<script>
import { assetType } from '@/assets/commonData/global'
import { getMappingName } from '@/utils/codeMapping'
import { mapState } from 'vuex'
import OperatingDialog from './OperatingDialog'
import SearchArea from '@/components/SearchArea'

export default {
  name: 'InitialSetting',
  components: { OperatingDialog, SearchArea },
  data() {
    return {
      showDialog: false,
      showList: false,
      isEditMode: false,
      conditions: {
        initial_type: ''
      },
      listData: [],
      assetType
    }
  },
  computed: {
    ...mapState({
      queryList: state => state.setting.initial.dataList
    }),
    getEditButtonText() {
      return this.isEditMode ? '送出' : '編輯'
    }
  },
  watch: {
    queryList(newValue) {
      this.listData = JSON.parse(JSON.stringify(newValue))
    }
  },
  methods: {
    mappingName(row, column, cellValue) {
      return getMappingName(column.property, cellValue)
    },
    search() {
      this.$store
        .dispatch('GetInitialList', this.conditions)
        .then(() => {
          this.showList = true
        })
        .catch(() => {
          this.showList = false
        })
    },
    deleteInitial(id) {
      this.$confirm('確定要刪除嗎？', '', {
        confirmButtonText: '確定',
        cancelButtonText: '取消'
      })
        .then(() => {
          this.$store.dispatch('DeleteInitialData', id)
        })
        .catch(() => {})
    },
    doAction() {
      if (
        this.isEditMode &&
        JSON.stringify(this.listData) !== JSON.stringify(this.queryList)
      ) {
        this.$store.dispatch('UpdateInitialData', this.listData).catch(() => {
          this.listData = JSON.parse(JSON.stringify(this.queryList))
          return
        })
      }
      this.isEditMode = !this.isEditMode
    }
  }
}
</script>

