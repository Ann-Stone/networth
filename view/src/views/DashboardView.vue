<template>
  <div class="flex flex-col gap-8">
    <PageHeader title="儀表板" :subtitle="today" />

    <section class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <template v-for="card in summaryCards" :key="card.type">
        <el-skeleton v-if="store.summariesLoading[card.type]" :rows="3" animated />
        <MetricCard
          v-else-if="card.format === 'currency'"
          :label="card.label"
          :amount="card.value"
          :delta-percent="card.deltaPercent"
          :delta-label="card.deltaLabel"
        />
        <div
          v-else
          class="flex flex-col gap-3 rounded-xl p-8 bg-white dark:bg-surface-dark border border-slate-200 dark:border-primary/5 shadow-sm"
        >
          <p class="text-slate-500 dark:text-muted-text text-sm font-semibold uppercase tracking-wider">
            {{ card.label }}
          </p>
          <span class="tabular-nums text-3xl font-bold text-neutral text-slate-900 dark:text-cream">
            {{ formatPercent(card.value) }}
          </span>
          <div v-if="card.deltaPercent !== undefined" class="flex items-center gap-1.5 mt-2">
            <TrendBadge :value="card.deltaPercent" />
            <span v-if="card.deltaLabel" class="text-slate-400 dark:text-muted-text text-xs">
              {{ card.deltaLabel }}
            </span>
          </div>
        </div>
      </template>
    </section>

    <section class="flex flex-col gap-4">
      <SectionHeader title="近期提醒" />
      <el-skeleton v-if="store.alarmsLoading" :rows="3" animated />
      <EmptyState v-else-if="store.alarms.length === 0" message="近半年沒有待辦提醒" />
      <DataListCard v-else title="未來 6 個月提醒">
        <div
          v-for="(alarm, idx) in store.alarms"
          :key="`${alarm.date}-${idx}`"
          class="flex items-center justify-between px-6 py-4"
        >
          <div class="flex items-center gap-4">
            <span
              class="inline-flex items-center justify-center min-w-[64px] px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-semibold"
            >
              {{ alarm.date }}
            </span>
            <p class="text-slate-800 dark:text-cream text-sm">{{ alarm.content }}</p>
          </div>
        </div>
      </DataListCard>
    </section>

    <section class="flex flex-col gap-4">
      <SectionHeader title="年度目標">
        <template #actions>
          <el-button type="primary" :icon="Plus" size="small" @click="openTargetCreate">
            新增目標
          </el-button>
        </template>
      </SectionHeader>
      <el-skeleton v-if="store.targetsLoading" :rows="3" animated />
      <EmptyState v-else-if="store.targets.length === 0" message="尚未設定年度目標" />
      <DataListCard v-else title="目標清單">
        <div
          v-for="t in store.targets"
          :key="t.distinct_number"
          class="flex items-center justify-between px-6 py-4"
        >
          <div class="flex flex-col gap-1">
            <p class="text-slate-800 dark:text-cream text-sm font-semibold">
              {{ t.distinct_number }} · {{ t.target_year }}
            </p>
            <MoneyDisplay :amount="t.setting_value" size="sm" />
          </div>
          <div class="flex items-center gap-2">
            <StatusBadge
              :value="t.is_done === 'Y' ? '已完成' : '進行中'"
              :type="t.is_done === 'Y' ? 'success' : 'info'"
            />
            <el-button :icon="Edit" size="small" text @click="openTargetEdit(t)" />
            <el-popconfirm
              title="確定刪除?"
              confirm-button-text="刪除"
              cancel-button-text="取消"
              @confirm="handleDeleteTarget(t.distinct_number)"
            >
              <template #reference>
                <el-button :icon="Delete" size="small" text type="danger" />
              </template>
            </el-popconfirm>
          </div>
        </div>
      </DataListCard>

      <FormDialog
        v-model="targetDialogVisible"
        :title="editingTarget ? '編輯目標' : '新增目標'"
        :loading="targetSubmitting"
        @submit="submitTarget"
      >
        <el-form ref="targetFormRef" :model="targetForm" :rules="targetRules" label-width="100px">
          <el-form-item label="編號" prop="distinct_number">
            <el-input v-model="targetForm.distinct_number" :disabled="!!editingTarget" placeholder="例如 T-2026-01" />
          </el-form-item>
          <el-form-item label="年度" prop="target_year">
            <el-input v-model="targetForm.target_year" placeholder="YYYY" maxlength="4" />
          </el-form-item>
          <el-form-item label="目標金額" prop="setting_value">
            <el-input-number v-model="targetForm.setting_value" :min="0" :step="10000" controls-position="right" class="!w-full" />
          </el-form-item>
          <el-form-item label="完成狀態">
            <el-switch v-model="targetForm.is_done" active-value="Y" inactive-value="N" />
          </el-form-item>
        </el-form>
      </FormDialog>
    </section>

    <section class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="flex flex-col gap-4">
        <SectionHeader :title="`本月預算 (${currentMonth})`" />
        <el-skeleton v-if="store.budgetLoading" :rows="6" animated />
        <EmptyState
          v-else-if="!store.budget || store.budget.lines.length === 0"
          message="本月尚無預算資料"
        />
        <div v-else class="flex flex-col gap-4">
          <div
            class="rounded-xl bg-white dark:bg-surface-dark border border-slate-200 dark:border-primary/5 p-4"
          >
            <BarChart
              :x-data="budgetXData"
              :series="budgetSeries"
              height="240px"
            />
          </div>
          <el-table :data="store.budget.lines" size="small" stripe>
            <el-table-column prop="category" label="類別" />
            <el-table-column label="預算" align="right">
              <template #default="{ row }">
                <MoneyDisplay :amount="row.planned" size="sm" />
              </template>
            </el-table-column>
            <el-table-column label="實際" align="right">
              <template #default="{ row }">
                <MoneyDisplay :amount="row.actual" size="sm" />
              </template>
            </el-table-column>
            <el-table-column prop="usage_pct" label="使用率" align="right" width="100">
              <template #default="{ row }">
                {{ row.usage_pct.toFixed(1) }}%
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <div class="flex flex-col gap-4">
        <SectionHeader :title="`本年贈與 (${currentYear})`" />
        <el-skeleton v-if="store.giftsLoading" :rows="4" animated />
        <EmptyState v-else-if="store.gifts.length === 0" message="本年尚無贈與紀錄" />
        <el-table v-else :data="store.gifts" size="small" stripe>
          <el-table-column prop="owner" label="對象" />
          <el-table-column label="金額" align="right">
            <template #default="{ row }">
              <MoneyDisplay :amount="row.amount" size="sm" />
            </template>
          </el-table-column>
          <el-table-column prop="rate" label="額度比例" align="right" width="120">
            <template #default="{ row }">
              {{ row.rate.toFixed(2) }}%
            </template>
          </el-table-column>
        </el-table>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import dayjs from 'dayjs'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import MetricCard from '@/components/ui/MetricCard.vue'
import TrendBadge from '@/components/ui/TrendBadge.vue'
import SectionHeader from '@/components/ui/SectionHeader.vue'
import DataListCard from '@/components/ui/DataListCard.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import FormDialog from '@/components/ui/FormDialog.vue'
import BarChart from '@/components/charts/BarChart.vue'
import { useDashboardStore, type SummaryType } from '@/stores/dashboard'
import { createTarget, updateTarget, deleteTarget } from '@/api/dashboard'
import type { DashboardSummary, TargetSetting } from '@/types/models'

const store = useDashboardStore()

const today = dayjs().format('YYYY-MM-DD')

const period = (() => {
  const end = dayjs()
  const start = end.subtract(11, 'month')
  return `${start.format('YYYYMM')}-${end.format('YYYYMM')}`
})()

const summaryTypes: SummaryType[] = ['asset_debt_trend', 'spending', 'freedom_ratio']

const labelMap: Record<SummaryType, string> = {
  asset_debt_trend: '資產淨值',
  spending: '本期支出',
  freedom_ratio: '財務自由度',
}

const formatMap: Record<SummaryType, 'currency' | 'percent'> = {
  asset_debt_trend: 'currency',
  spending: 'currency',
  freedom_ratio: 'percent',
}

function latestValue(summary: DashboardSummary | null): number {
  if (!summary || summary.points.length === 0) return 0
  return summary.points[summary.points.length - 1]!.value
}

function previousValue(summary: DashboardSummary | null): number | null {
  if (!summary || summary.points.length < 2) return null
  return summary.points[summary.points.length - 2]!.value
}

function deltaPercent(summary: DashboardSummary | null): number | undefined {
  const prev = previousValue(summary)
  if (prev === null || prev === 0) return undefined
  const curr = latestValue(summary)
  return ((curr - prev) / Math.abs(prev)) * 100
}

function deltaLabel(summary: DashboardSummary | null): string | undefined {
  if (!summary || summary.points.length < 2) return undefined
  return '較上期'
}

function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`
}

const summaryCards = computed(() =>
  summaryTypes.map((type) => {
    const summary = store.summaries[type]
    return {
      type,
      label: labelMap[type],
      format: formatMap[type],
      value: latestValue(summary),
      deltaPercent: deltaPercent(summary),
      deltaLabel: deltaLabel(summary),
    }
  }),
)

// Targets CRUD ----------------------------------------------------------------
const targetDialogVisible = ref(false)
const targetSubmitting = ref(false)
const editingTarget = ref<TargetSetting | null>(null)
const targetFormRef = ref<FormInstance | null>(null)
const targetForm = reactive({
  distinct_number: '',
  target_year: dayjs().format('YYYY'),
  setting_value: 0,
  is_done: 'N',
})
const targetRules: FormRules = {
  distinct_number: [{ required: true, message: '請輸入編號', trigger: 'blur' }],
  target_year: [{ required: true, pattern: /^\d{4}$/, message: '請輸入 YYYY', trigger: 'blur' }],
  setting_value: [{ required: true, type: 'number', message: '請輸入金額', trigger: 'blur' }],
}

function resetTargetForm() {
  targetForm.distinct_number = ''
  targetForm.target_year = dayjs().format('YYYY')
  targetForm.setting_value = 0
  targetForm.is_done = 'N'
}

function openTargetCreate() {
  editingTarget.value = null
  resetTargetForm()
  targetDialogVisible.value = true
}

function openTargetEdit(t: TargetSetting) {
  editingTarget.value = t
  targetForm.distinct_number = t.distinct_number
  targetForm.target_year = t.target_year
  targetForm.setting_value = t.setting_value
  targetForm.is_done = t.is_done
  targetDialogVisible.value = true
}

async function submitTarget() {
  if (!targetFormRef.value) return
  const ok = await targetFormRef.value.validate().catch(() => false)
  if (!ok) return
  targetSubmitting.value = true
  try {
    if (editingTarget.value) {
      await updateTarget(editingTarget.value.distinct_number, {
        target_year: targetForm.target_year,
        setting_value: targetForm.setting_value,
        is_done: targetForm.is_done,
      })
      ElMessage.success('已更新目標')
    } else {
      await createTarget({
        distinct_number: targetForm.distinct_number,
        target_year: targetForm.target_year,
        setting_value: targetForm.setting_value,
        is_done: targetForm.is_done,
      })
      ElMessage.success('已新增目標')
    }
    targetDialogVisible.value = false
    await store.fetchTargets()
  } finally {
    targetSubmitting.value = false
  }
}

async function handleDeleteTarget(targetId: string) {
  await deleteTarget(targetId)
  ElMessage.success('已刪除目標')
  await store.fetchTargets()
}

// Budget + Gifts --------------------------------------------------------------
const currentMonth = dayjs().format('YYYYMM')
const currentYear = dayjs().year()

const budgetXData = computed(() => store.budget?.lines.map((l) => l.category) ?? [])
const budgetSeries = computed(() => {
  const lines = store.budget?.lines ?? []
  return [
    { name: '預算', data: lines.map((l) => l.planned) },
    { name: '實際', data: lines.map((l) => l.actual) },
  ]
})

onMounted(() => {
  for (const type of summaryTypes) {
    store.fetchSummary({ type, period })
  }
  store.fetchAlarms()
  store.fetchTargets()
  store.fetchBudget({ type: 'monthly', period: currentMonth })
  store.fetchGifts(currentYear)
})
</script>
