<template>
  <div class="flex flex-col gap-8">
    <PageHeader title="月度現金流" :subtitle="store.selectedMonth">
      <template #actions>
        <el-date-picker
          v-model="selectedMonthDate"
          type="month"
          placeholder="選擇月份"
          format="YYYY/MM"
          :clearable="false"
        />
      </template>
    </PageHeader>

    <section class="flex flex-col gap-4">
      <SectionHeader title="日記帳">
        <template #actions>
          <el-button type="primary" :icon="Plus" size="small" @click="openCreateJournal">
            新增
          </el-button>
        </template>
      </SectionHeader>
      <el-skeleton v-if="store.journalsLoading" :rows="5" animated />
      <EmptyState v-else-if="store.journals.length === 0" message="本月尚無日記帳資料" />
      <template v-else>
        <el-table :data="store.journals" stripe border style="width: 100%">
          <el-table-column prop="spend_date" label="日期" width="110" />
          <el-table-column prop="spend_way" label="帳戶" min-width="140" />
          <el-table-column prop="action_main_type" label="類別" width="120" />
          <el-table-column prop="action_sub_type" label="子類" width="120">
            <template #default="{ row }">
              <span>{{ row.action_sub_type ?? '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="金額" width="180" align="right">
            <template #default="{ row }">
              <MoneyDisplay
                :amount="row.spending"
                :positive="row.spending > 0 ? true : row.spending < 0 ? false : null"
                size="sm"
              />
            </template>
          </el-table-column>
          <el-table-column prop="note" label="備註" min-width="160">
            <template #default="{ row }">
              <span>{{ row.note ?? '' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160" align="center">
            <template #default="{ row }">
              <el-button size="small" :icon="Edit" @click="editJournal(row)">編輯</el-button>
              <el-popconfirm
                title="確定刪除這筆日記帳?"
                @confirm="handleDeleteJournal(row.distinct_number)"
              >
                <template #reference>
                  <el-button size="small" type="danger" :icon="Delete">刪除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>

        <div
          class="grid grid-cols-1 md:grid-cols-3 gap-4 rounded-xl border border-slate-200 dark:border-primary/5 bg-white dark:bg-surface-dark p-6"
        >
          <div class="flex flex-col gap-1">
            <p class="text-slate-500 dark:text-muted-text text-xs uppercase tracking-wider">本月收入</p>
            <MoneyDisplay :amount="totalIncome" :positive="true" size="lg" />
          </div>
          <div class="flex flex-col gap-1">
            <p class="text-slate-500 dark:text-muted-text text-xs uppercase tracking-wider">本月支出</p>
            <MoneyDisplay :amount="totalExpense" :positive="false" size="lg" />
          </div>
          <div class="flex flex-col gap-1">
            <p class="text-slate-500 dark:text-muted-text text-xs uppercase tracking-wider">本月淨額</p>
            <MoneyDisplay
              :amount="netTotal"
              :positive="netTotal > 0 ? true : netTotal < 0 ? false : null"
              size="lg"
            />
          </div>
        </div>
      </template>
    </section>

    <FormDialog
      v-model="journalDialogVisible"
      :title="formMode === 'create' ? '新增日記帳' : '編輯日記帳'"
      :loading="submitting"
      width="640px"
      @submit="submitJournal"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="日期" prop="spend_date">
          <el-date-picker
            v-model="formDateValue"
            type="date"
            placeholder="選擇日期"
            format="YYYY/MM/DD"
            :clearable="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="支付來源" prop="spend_way_type">
          <el-radio-group v-model="formData.spend_way_type" @change="onSpendWayTypeChange">
            <el-radio value="account">帳戶</el-radio>
            <el-radio value="credit_card">信用卡</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="帳戶/卡片" prop="spend_way">
          <el-select v-model="formData.spend_way" placeholder="選擇" filterable style="width: 100%">
            <el-option-group
              v-for="group in activeSpendWayGroups"
              :key="group.label"
              :label="group.label"
            >
              <el-option
                v-for="opt in group.options"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-option-group>
          </el-select>
        </el-form-item>
        <el-form-item label="主類別" prop="action_main">
          <el-select
            v-model="formData.action_main"
            placeholder="選擇主類別"
            filterable
            style="width: 100%"
            @change="onActionMainChange"
          >
            <el-option-group
              v-for="group in codeGroups"
              :key="group.label"
              :label="group.label"
            >
              <el-option
                v-for="opt in group.options"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
                :data-type="group.label"
              />
            </el-option-group>
          </el-select>
        </el-form-item>
        <el-form-item label="子類別">
          <el-select
            v-model="formData.action_sub"
            placeholder="(可選)"
            filterable
            clearable
            style="width: 100%"
            :disabled="!formData.action_main"
            @change="onActionSubChange"
          >
            <el-option-group
              v-for="group in subCodeGroups"
              :key="group.label"
              :label="group.label"
            >
              <el-option
                v-for="opt in group.options"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
                :data-type="group.label"
              />
            </el-option-group>
          </el-select>
        </el-form-item>
        <el-form-item label="金額" prop="spending">
          <el-input-number
            v-model="formData.spending"
            :precision="2"
            :step="100"
            controls-position="right"
            style="width: 100%"
          />
          <p class="text-xs text-slate-400 dark:text-muted-text mt-1">
            正數 = 收入,負數 = 支出
          </p>
        </el-form-item>
        <el-form-item label="發票號碼">
          <el-input v-model="formData.invoice_number" placeholder="(可選)" />
        </el-form-item>
        <el-form-item label="備註">
          <el-input v-model="formData.note" type="textarea" :rows="2" placeholder="(可選)" />
        </el-form-item>
      </el-form>
    </FormDialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import SectionHeader from '@/components/ui/SectionHeader.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import FormDialog from '@/components/ui/FormDialog.vue'
import { useCashFlowStore } from '@/stores/cashFlow'
import { createJournal, updateJournal, deleteJournal } from '@/api/cashFlow'
import {
  getAccountSelections,
  getCodeSelections,
  getCreditCardSelections,
} from '@/api/utilities'
import type { Journal, JournalCreate, SelectionGroup } from '@/types/models'

const store = useCashFlowStore()

const selectedMonthDate = ref<Date>(dayjs(store.selectedMonth, 'YYYYMM').toDate())

watch(selectedMonthDate, (date) => {
  if (!date) return
  const next = dayjs(date).format('YYYYMM')
  if (next === store.selectedMonth) return
  store.selectedMonth = next
  store.fetchJournals()
})

const totalIncome = computed(() =>
  store.journals
    .filter((j) => j.spending > 0)
    .reduce((sum, j) => sum + j.spending, 0),
)

const totalExpense = computed(() =>
  store.journals
    .filter((j) => j.spending < 0)
    .reduce((sum, j) => sum + j.spending, 0),
)

const netTotal = computed(() => totalIncome.value + totalExpense.value)

// ─── Selection caches ──────────────────────────────────────────────────────
const accountGroups = ref<SelectionGroup[]>([])
const creditCardGroups = ref<SelectionGroup[]>([])
const codeGroups = ref<SelectionGroup[]>([])
const subCodeGroups = ref<SelectionGroup[]>([])

const activeSpendWayGroups = computed(() =>
  formData.value.spend_way_type === 'credit_card' ? creditCardGroups.value : accountGroups.value,
)

async function loadSpendWaySelections() {
  if (accountGroups.value.length === 0) {
    accountGroups.value = await getAccountSelections()
  }
  if (creditCardGroups.value.length === 0) {
    creditCardGroups.value = await getCreditCardSelections()
  }
}

async function loadCodeSelections() {
  if (codeGroups.value.length === 0) {
    codeGroups.value = await getCodeSelections()
  }
}

async function loadSubCodeSelections(parent: string) {
  if (!parent) {
    subCodeGroups.value = []
    return
  }
  try {
    subCodeGroups.value = await getCodeSelections(parent)
  } catch {
    subCodeGroups.value = []
  }
}

// ─── Form state ────────────────────────────────────────────────────────────
type JournalFormState = JournalCreate & { distinct_number?: number; action_sub?: string | null }

function emptyForm(): JournalFormState {
  return {
    vesting_month: store.selectedMonth,
    spend_date: dayjs().format('YYYYMMDD'),
    spend_way: '',
    spend_way_type: 'account',
    spend_way_table: 'Account',
    action_main: '',
    action_main_type: '',
    action_main_table: 'Code_Data',
    action_sub: null,
    action_sub_type: null,
    action_sub_table: null,
    spending: 0,
    invoice_number: null,
    note: null,
  }
}

const journalDialogVisible = ref(false)
const formMode = ref<'create' | 'edit'>('create')
const formData = ref<JournalFormState>(emptyForm())
const formRef = ref<FormInstance>()
const submitting = ref(false)

const formDateValue = computed<Date | null>({
  get: () => (formData.value.spend_date ? dayjs(formData.value.spend_date, 'YYYYMMDD').toDate() : null),
  set: (date) => {
    formData.value.spend_date = date ? dayjs(date).format('YYYYMMDD') : ''
  },
})

const formRules: FormRules = {
  spend_date: [{ required: true, message: '請選擇日期', trigger: 'change' }],
  spend_way: [{ required: true, message: '請選擇帳戶/卡片', trigger: 'change' }],
  spend_way_type: [{ required: true, message: '請選擇支付來源類型', trigger: 'change' }],
  action_main: [{ required: true, message: '請選擇主類別', trigger: 'change' }],
  spending: [{ required: true, message: '請輸入金額', trigger: 'blur' }],
}

function findCodeType(groups: SelectionGroup[], value: string): string {
  for (const group of groups) {
    if (group.options.some((opt) => opt.value === value)) return group.label
  }
  return ''
}

function onSpendWayTypeChange(value: string | number | boolean | undefined) {
  const v = String(value)
  formData.value.spend_way = ''
  formData.value.spend_way_table = v === 'credit_card' ? 'Credit_Card' : 'Account'
}

async function onActionMainChange(value: string | number | boolean | undefined) {
  const v = value ? String(value) : ''
  formData.value.action_main_type = findCodeType(codeGroups.value, v)
  formData.value.action_sub = null
  formData.value.action_sub_type = null
  formData.value.action_sub_table = null
  await loadSubCodeSelections(v)
}

function onActionSubChange(value: string | number | boolean | undefined) {
  const v = value ? String(value) : ''
  if (!v) {
    formData.value.action_sub = null
    formData.value.action_sub_type = null
    formData.value.action_sub_table = null
    return
  }
  formData.value.action_sub = v
  formData.value.action_sub_type = findCodeType(subCodeGroups.value, v)
  formData.value.action_sub_table = 'Code_Data'
}

async function openCreateJournal() {
  formMode.value = 'create'
  formData.value = emptyForm()
  subCodeGroups.value = []
  journalDialogVisible.value = true
  await Promise.all([loadSpendWaySelections(), loadCodeSelections()])
}

async function editJournal(row: Journal) {
  formMode.value = 'edit'
  formData.value = {
    distinct_number: row.distinct_number,
    vesting_month: row.vesting_month,
    spend_date: row.spend_date,
    spend_way: row.spend_way,
    spend_way_type: row.spend_way_type,
    spend_way_table: row.spend_way_table,
    action_main: row.action_main,
    action_main_type: row.action_main_type,
    action_main_table: row.action_main_table,
    action_sub: row.action_sub ?? null,
    action_sub_type: row.action_sub_type ?? null,
    action_sub_table: row.action_sub_table ?? null,
    spending: row.spending,
    invoice_number: row.invoice_number ?? null,
    note: row.note ?? null,
  }
  journalDialogVisible.value = true
  await Promise.all([loadSpendWaySelections(), loadCodeSelections()])
  if (row.action_main) await loadSubCodeSelections(row.action_main)
}

async function submitJournal() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const payload: JournalCreate = {
      vesting_month: formData.value.vesting_month,
      spend_date: formData.value.spend_date,
      spend_way: formData.value.spend_way,
      spend_way_type: formData.value.spend_way_type,
      spend_way_table: formData.value.spend_way_table,
      action_main: formData.value.action_main,
      action_main_type: formData.value.action_main_type,
      action_main_table: formData.value.action_main_table,
      action_sub: formData.value.action_sub ?? null,
      action_sub_type: formData.value.action_sub_type ?? null,
      action_sub_table: formData.value.action_sub_table ?? null,
      spending: Number(formData.value.spending ?? 0),
      invoice_number: formData.value.invoice_number || null,
      note: formData.value.note || null,
    }
    if (formMode.value === 'create') {
      await createJournal(payload)
      ElMessage.success('新增成功')
    } else if (formData.value.distinct_number !== undefined) {
      await updateJournal(formData.value.distinct_number, payload)
      ElMessage.success('更新成功')
    }
    journalDialogVisible.value = false
    await store.fetchJournals()
  } finally {
    submitting.value = false
  }
}

async function handleDeleteJournal(id: number) {
  await deleteJournal(id)
  ElMessage.success('已刪除')
  await store.fetchJournals()
}

onMounted(() => {
  store.fetchJournals()
})
</script>
