<template>
  <el-table
    :data="listData"
    stripe
    header-cell-class-name="table-header"
  >
    <el-table-column
      fixed="left"
      label="項目"
      prop="category_name"
      width="100"
    />
    <el-table-column
      label="月份"
      align="center"
    >
      <el-table-column
        label="1"
        align="center"
      >
        <template slot-scope="scope">
          <span v-if="!isEditMode">{{ scope.row.expected1 }}</span>
          <el-input
            v-else
            v-model="scope.row.expected1"
            autocomplete="off"
          />
        </template>
      </el-table-column>
      <el-table-column
        label="2"
        align="center"
      >
        <template slot-scope="scope">
          <span v-if="!isEditMode">{{ scope.row.expected2 }}</span>
          <el-input
            v-else
            v-model="scope.row.expected2"
            autocomplete="off"
          />
        </template>
      </el-table-column>
      <el-table-column
        label="3"
        align="center"
      >
        <template slot-scope="scope">
          <span v-if="!isEditMode">{{ scope.row.expected3 }}</span>
          <el-input
            v-else
            v-model="scope.row.expected3"
            autocomplete="off"
          />
        </template>
      </el-table-column>
      <el-table-column
        label="4"
        align="center"
      >
        <template slot-scope="scope">
          <span v-if="!isEditMode">{{ scope.row.expected4 }}</span>
          <el-input
            v-else
            v-model="scope.row.expected4"
            autocomplete="off"
          />
        </template>
      </el-table-column>
      <el-table-column
        label="5"
        align="center"
      >
        <template slot-scope="scope">
          <span v-if="!isEditMode">{{ scope.row.expected5 }}</span>
          <el-input
            v-else
            v-model="scope.row.expected5"
            autocomplete="off"
          />
        </template>
      </el-table-column>
      <el-table-column
        label="6"
        align="center"
      >
        <template slot-scope="scope">
          <span v-if="!isEditMode">{{ scope.row.expected6 }}</span>
          <el-input
            v-else
            v-model="scope.row.expected6"
            autocomplete="off"
          />
        </template>
      </el-table-column>
      <el-table-column
        label="7"
        align="center"
      >
        <template slot-scope="scope">
          <span v-if="!isEditMode">{{ scope.row.expected7 }}</span>
          <el-input
            v-else
            v-model="scope.row.expected7"
            autocomplete="off"
          />
        </template>
      </el-table-column>
      <el-table-column
        label="8"
        align="center"
      >
        <template slot-scope="scope">
          <span v-if="!isEditMode">{{ scope.row.expected8 }}</span>
          <el-input
            v-else
            v-model="scope.row.expected8"
            autocomplete="off"
          />
        </template>
      </el-table-column>
      <el-table-column
        label="9"
        align="center"
      >
        <template slot-scope="scope">
          <span v-if="!isEditMode">{{ scope.row.expected9 }}</span>
          <el-input
            v-else
            v-model="scope.row.expected9"
            autocomplete="off"
          />
        </template>
      </el-table-column>
      <el-table-column
        label="10"
        align="center"
      >
        <template slot-scope="scope">
          <span v-if="!isEditMode">{{ scope.row.expected10 }}</span>
          <el-input
            v-else
            v-model="scope.row.expected10"
            autocomplete="off"
          />
        </template>
      </el-table-column>
      <el-table-column
        label="11"
        align="center"
      >
        <template slot-scope="scope">
          <span v-if="!isEditMode">{{ scope.row.expected11 }}</span>
          <el-input
            v-else
            v-model="scope.row.expected11"
            autocomplete="off"
          />
        </template>
      </el-table-column>
      <el-table-column
        label="12"
        align="center"
      >
        <template slot-scope="scope">
          <span v-if="!isEditMode">{{ scope.row.expected12 }}</span>
          <el-input
            v-else
            v-model="scope.row.expected12"
            autocomplete="off"
          />
        </template>
      </el-table-column>
    </el-table-column>
  </el-table>
</template>

<script>
export default {
  props: {
    isEditMode: {
      type: Boolean,
      default: false
    },
    rawData: {
      type: Array,
      default: null
    }
  },
  data() {
    return {
      listData: []
    }
  },
  watch: {
    rawData(newData) {
      this.listData = JSON.parse(JSON.stringify(newData))
    },
    isEditMode(newData) {
      if (
        !newData &&
        JSON.stringify(this.rawData) !== JSON.stringify(this.listData)
      ) {
        this.$store.dispatch('UpdateBudgetData', this.listData).catch(() => {
          this.listData = JSON.parse(JSON.stringify(this.rawData))
          return
        })
      }
    }
  }
}
</script>
