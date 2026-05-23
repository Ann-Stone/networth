<template>
  <div class="flex flex-col gap-6">
    <PageHeader title="提醒設定" subtitle="管理財務循環提醒（每年 / 每月）">
      <template #actions>
        <el-button type="primary" :icon="PlusIcon" @click="openCreate">
          新增提醒
        </el-button>
      </template>
    </PageHeader>

    <DataListCard title="提醒清單">
      <div class="p-4">
        <el-table
          :data="store.alarms"
          v-loading="store.alarmsLoading"
          stripe
          empty-text="尚無提醒"
        >
          <el-table-column label="循環" min-width="100">
            <template #default="{ row }">
              <span
                class="text-xs font-semibold px-2 py-0.5 rounded bg-on-surface-variant/10 text-on-surface-variant"
              >
                🔁 {{ row.alarm_type === 'Y' ? '每年' : '每月' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="提醒日" min-width="140">
            <template #default="{ row }">{{ formatRecurAnchor(row) }}</template>
          </el-table-column>
          <el-table-column prop="content" label="內容" min-width="260" />
          <el-table-column label="到期日" min-width="140">
            <template #default="{ row }">{{ formatDate(row.due_date) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openEdit(row)">編輯</el-button>
              <el-button link type="danger" @click="handleDelete(row)">刪除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </DataListCard>

    <FormDialog
      v-model="alarmDialogVisible"
      :title="formMode === 'create' ? '新增提醒' : '編輯提醒'"
      :loading="submitting"
      width="520px"
      @submit="submitAlarm"
    >
      <el-form
        ref="alarmFormRef"
        :model="alarmForm"
        :rules="alarmFormRules"
        label-width="100px"
      >
        <el-form-item label="循環" prop="alarm_type">
          <el-select v-model="alarmForm.alarm_type" placeholder="選擇循環" style="width: 100%">
            <el-option label="每年（Y）" value="Y" />
            <el-option label="每月（M）" value="M" />
          </el-select>
        </el-form-item>
        <el-form-item :label="anchorLabel" prop="alarm_date">
          <el-input
            v-model="alarmForm.alarm_date"
            :placeholder="anchorPlaceholder"
            :maxlength="alarmForm.alarm_type === 'Y' ? 4 : 2"
          />
        </el-form-item>
        <el-form-item label="內容" prop="content">
          <el-input v-model="alarmForm.content" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="到期日">
          <el-date-picker
            v-model="dueDateModel"
            type="date"
            value-format="YYYYMMDD"
            placeholder="選填，超過此日不再展開"
            clearable
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
    </FormDialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Plus as PlusIcon } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import PageHeader from '@/components/ui/PageHeader.vue'
import DataListCard from '@/components/ui/DataListCard.vue'
import FormDialog from '@/components/ui/FormDialog.vue'
import { useConfirm } from '@/composables/useConfirm'
import { useSettingStore } from '@/stores/setting'
import { createAlarm, updateAlarm, deleteAlarm } from '@/api/setting'
import type { Alarm, AlarmCreate, AlarmType } from '@/types/models'

const store = useSettingStore()
const confirm = useConfirm()

onMounted(() => {
  void store.fetchAlarms()
})

function formatDate(value: string | null | undefined): string {
  if (!value) return '—'
  const parsed = dayjs(value, 'YYYYMMDD')
  return parsed.isValid() ? parsed.format('YYYY/MM/DD') : value
}

function formatRecurAnchor(row: Alarm): string {
  if (row.alarm_type === 'Y' && row.alarm_date.length === 4) {
    return `每年 ${row.alarm_date.slice(0, 2)}/${row.alarm_date.slice(2)}`
  }
  if (row.alarm_type === 'M' && row.alarm_date.length === 2) {
    return `每月 ${row.alarm_date} 日`
  }
  return row.alarm_date
}

const alarmDialogVisible = ref(false)
const formMode = ref<'create' | 'edit'>('create')
const submitting = ref(false)
const alarmFormRef = ref<FormInstance>()
const editingAlarmId = ref<number | null>(null)

function emptyAlarmForm(): AlarmCreate {
  return {
    alarm_type: 'Y',
    alarm_date: '',
    content: '',
    due_date: null,
  }
}

const alarmForm = ref<AlarmCreate>(emptyAlarmForm())

const dueDateModel = computed<string>({
  get: () => alarmForm.value.due_date ?? '',
  set: (v) => {
    alarmForm.value.due_date = v ? v : null
  },
})

const anchorLabel = computed(() =>
  alarmForm.value.alarm_type === 'Y' ? '提醒日 (MMDD)' : '提醒日 (DD)',
)

const anchorPlaceholder = computed(() =>
  alarmForm.value.alarm_type === 'Y' ? '例：0531（每年 5/31）' : '例：15（每月 15 號）',
)

const alarmFormRules: FormRules = {
  alarm_type: [{ required: true, message: '請選擇循環', trigger: 'change' }],
  alarm_date: [
    { required: true, message: '請輸入提醒日', trigger: 'blur' },
    {
      validator: (_rule: unknown, value: string, callback: (error?: Error) => void) => {
        const type: AlarmType = alarmForm.value.alarm_type as AlarmType
        if (type === 'Y') {
          if (!/^\d{4}$/.test(value)) return callback(new Error('每年提醒需為 4 碼 MMDD'))
          const mm = Number(value.slice(0, 2))
          const dd = Number(value.slice(2))
          if (mm < 1 || mm > 12) return callback(new Error('月份需 01-12'))
          if (dd < 1 || dd > 31) return callback(new Error('日期需 01-31'))
        } else {
          if (!/^\d{2}$/.test(value)) return callback(new Error('每月提醒需為 2 碼 DD'))
          const dd = Number(value)
          if (dd < 1 || dd > 31) return callback(new Error('日期需 01-31'))
        }
        callback()
      },
      trigger: 'blur',
    },
  ],
  content: [{ required: true, message: '請輸入內容', trigger: 'blur' }],
}

function openCreate() {
  formMode.value = 'create'
  editingAlarmId.value = null
  alarmForm.value = emptyAlarmForm()
  alarmDialogVisible.value = true
}

function openEdit(row: Alarm) {
  formMode.value = 'edit'
  editingAlarmId.value = row.alarm_id
  alarmForm.value = {
    alarm_type: row.alarm_type,
    alarm_date: row.alarm_date,
    content: row.content,
    due_date: row.due_date ?? null,
  }
  alarmDialogVisible.value = true
}

async function submitAlarm() {
  if (!alarmFormRef.value) return
  const valid = await alarmFormRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    if (formMode.value === 'create') {
      await createAlarm({ ...alarmForm.value })
      ElMessage.success('新增成功')
    } else if (editingAlarmId.value !== null) {
      await updateAlarm(editingAlarmId.value, { ...alarmForm.value })
      ElMessage.success('更新成功')
    }
    alarmDialogVisible.value = false
    await store.fetchAlarms()
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row: Alarm) {
  const ok = await confirm({
    title: '刪除提醒',
    message: `確定要刪除「${row.content}」?`,
    type: 'warning',
  })
  if (!ok) return
  await deleteAlarm(row.alarm_id)
  ElMessage.success('已刪除')
  await store.fetchAlarms()
}
</script>
