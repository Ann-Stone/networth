<template>
  <div class="flex flex-col gap-6">
    <PageHeader title="預算設定" subtitle="逐月編輯類別預算">
      <template #actions>
        <el-select
          v-model="selectedYear"
          placeholder="選擇年度"
          style="width: 140px"
          @change="reload"
        >
          <el-option
            v-for="y in store.budgetYears"
            :key="y"
            :label="y"
            :value="y"
          />
        </el-select>
        <el-button :loading="copying" @click="handleCopyPrevious">
          複製去年
        </el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          儲存
        </el-button>
      </template>
    </PageHeader>

    <DataListCard :title="`${selectedYear} 年預算 (TWD)`">
      <div class="p-4">
        <el-table
          :data="store.budgets"
          v-loading="store.budgetsLoading"
          border
          stripe
          empty-text="尚無預算資料"
          max-height="640"
        >
          <el-table-column
            prop="category_name"
            label="類別"
            width="180"
            fixed="left"
          >
            <template #default="{ row }">
              <div class="flex flex-col">
                <span class="font-semibold text-on-surface">{{ row.category_name }}</span>
                <span class="text-xs text-on-surface-muted">{{ row.category_code }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column
            v-for="m in MONTH_KEYS"
            :key="m.key"
            :label="m.label"
            min-width="120"
          >
            <template #default="{ row }">
              <el-input-number
                v-model="row[m.key]"
                :min="0"
                :step="1000"
                :precision="0"
                :controls="false"
                size="small"
                style="width: 100%"
              />
            </template>
          </el-table-column>
        </el-table>
      </div>
    </DataListCard>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/ui/PageHeader.vue'
import DataListCard from '@/components/ui/DataListCard.vue'
import { useSettingStore } from '@/stores/setting'
import { copyBudgetFromPrevious, updateBudgets } from '@/api/setting'

const MONTH_KEYS = [
  { key: 'expected01', label: '1 月' },
  { key: 'expected02', label: '2 月' },
  { key: 'expected03', label: '3 月' },
  { key: 'expected04', label: '4 月' },
  { key: 'expected05', label: '5 月' },
  { key: 'expected06', label: '6 月' },
  { key: 'expected07', label: '7 月' },
  { key: 'expected08', label: '8 月' },
  { key: 'expected09', label: '9 月' },
  { key: 'expected10', label: '10 月' },
  { key: 'expected11', label: '11 月' },
  { key: 'expected12', label: '12 月' },
] as const

const store = useSettingStore()
const selectedYear = ref<string>(String(new Date().getFullYear()))
const saving = ref(false)
const copying = ref(false)

onMounted(async () => {
  await store.fetchBudgetYears()
  const first = store.budgetYears[0]
  if (first && !store.budgetYears.includes(selectedYear.value)) {
    selectedYear.value = first
  }
  await reload()
})

async function reload() {
  await store.fetchBudgets(Number(selectedYear.value))
}

async function handleSave() {
  saving.value = true
  try {
    await updateBudgets(store.budgets)
    ElMessage.success('儲存成功')
  } finally {
    saving.value = false
  }
}

async function handleCopyPrevious() {
  copying.value = true
  try {
    await copyBudgetFromPrevious(Number(selectedYear.value))
    await reload()
    ElMessage.success('已複製去年預算')
  } finally {
    copying.value = false
  }
}
</script>
