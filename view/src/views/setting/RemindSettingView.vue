<template>
  <div class="flex flex-col gap-6">
    <PageHeader title="提醒設定" subtitle="管理重要日期與提示">
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
          <el-table-column prop="alarm_type" label="類型" min-width="140" />
          <el-table-column label="提醒日" min-width="140">
            <template #default="{ row }">{{ formatDate(row.alarm_date) }}</template>
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
        <el-form-item label="類型" prop="alarm_type">
          <el-input v-model="alarmForm.alarm_type" placeholder="如 保單續期 / 信用卡帳單" />
        </el-form-item>
        <el-form-item label="提醒日" prop="alarm_date">
          <el-date-picker
            v-model="alarmForm.alarm_date"
            type="date"
            value-format="YYYYMMDD"
            placeholder="選擇日期"
            style="width: 100%"
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
            placeholder="選擇日期 (選填)"
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
import type { Alarm, AlarmCreate } from '@/types/models'

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

const alarmDialogVisible = ref(false)
const formMode = ref<'create' | 'edit'>('create')
const submitting = ref(false)
const alarmFormRef = ref<FormInstance>()
const editingAlarmId = ref<number | null>(null)

function emptyAlarmForm(): AlarmCreate {
  return {
    alarm_type: '',
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

const alarmFormRules: FormRules = {
  alarm_type: [{ required: true, message: '請輸入類型', trigger: 'blur' }],
  alarm_date: [{ required: true, message: '請選擇提醒日', trigger: 'change' }],
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
    message: `確定要刪除「${row.alarm_type}」?`,
    type: 'warning',
  })
  if (!ok) return
  await deleteAlarm(row.alarm_id)
  ElMessage.success('已刪除')
  await store.fetchAlarms()
}
</script>
