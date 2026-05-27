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
        <el-button :loading="suggesting" @click="handleSuggest">
          智慧產生
        </el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          儲存
        </el-button>
      </template>
    </PageHeader>

    <el-alert
      v-if="previewDirty"
      type="info"
      :closable="false"
      show-icon
      title="目前顯示的是建議值,尚未儲存。請確認各月份(特別是年度事件的全年額度)後按「儲存」。"
    />

    <DataListCard :title="`${selectedYear} 年預算 (TWD)`">
      <div class="p-4">
        <el-table
          :data="ordinaryBudgets"
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

    <DataListCard
      v-if="eventBudgets.length"
      :title="`${selectedYear} 年度事件信封 (全年一筆)`"
    >
      <div class="p-4">
        <el-table :data="eventBudgets" border stripe max-height="400">
          <el-table-column prop="category_name" label="類別" min-width="180">
            <template #default="{ row }">
              <div class="flex flex-col">
                <span class="font-semibold text-on-surface">{{ row.category_name }}</span>
                <span class="text-xs text-on-surface-muted">{{ row.category_code }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="全年額度" min-width="220">
            <template #default="{ row }">
              <el-input-number
                v-model="row.annual_amount"
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
        <p class="mt-2 text-xs text-on-surface-muted">
          年度事件以全年一筆額度管理,不分攤到各月。儀表板以「年初至今 vs 全年額度」呈現,因此不會影響每月超支判讀。
        </p>
      </div>
    </DataListCard>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/ui/PageHeader.vue'
import DataListCard from '@/components/ui/DataListCard.vue'
import { useSettingStore } from '@/stores/setting'
import { applyBudget, getCodes, suggestBudget } from '@/api/setting'

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
const suggesting = ref(false)
const previewDirty = ref(false)
const eventCodeIds = ref<Set<string>>(new Set())

const ordinaryBudgets = computed(() =>
  store.budgets.filter((b) => !eventCodeIds.value.has(b.category_code)),
)
const eventBudgets = computed(() =>
  store.budgets.filter((b) => eventCodeIds.value.has(b.category_code)),
)

onMounted(async () => {
  await store.fetchBudgetYears()
  const first = store.budgetYears[0]
  if (first && !store.budgetYears.includes(selectedYear.value)) {
    selectedYear.value = first
  }
  await reload()
})

async function reload() {
  previewDirty.value = false
  const [, codes] = await Promise.all([
    store.fetchBudgets(Number(selectedYear.value)),
    getCodes(),
  ])
  eventCodeIds.value = new Set(
    codes.filter((c) => c.is_annual_event).map((c) => c.code_id),
  )
}

async function handleSuggest() {
  suggesting.value = true
  try {
    store.budgets = await suggestBudget(Number(selectedYear.value))
    previewDirty.value = true
    ElMessage.success('已套用建議值,確認後請按儲存')
  } finally {
    suggesting.value = false
  }
}

async function handleSave() {
  saving.value = true
  try {
    await applyBudget(Number(selectedYear.value), store.budgets)
    ElMessage.success('儲存成功')
    await reload()
  } finally {
    saving.value = false
  }
}
</script>
