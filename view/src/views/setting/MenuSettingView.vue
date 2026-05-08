<template>
  <div class="flex flex-col gap-6">
    <PageHeader title="選單設定" subtitle="管理帳戶、分類與信用卡" />

    <el-tabs v-model="activeTab" class="settings-tabs">
      <el-tab-pane label="帳戶" name="accounts">
        <DataListCard title="帳戶清單">
          <template #menu>
            <el-button type="primary" :icon="PlusIcon" @click="openCreateAccount">
              新增帳戶
            </el-button>
          </template>

          <div class="p-4">
            <el-table
              :data="store.accounts"
              v-loading="store.accountsLoading"
              row-key="id"
              stripe
              empty-text="尚無帳戶"
            >
              <el-table-column prop="account_id" label="帳戶 ID" min-width="140" />
              <el-table-column prop="name" label="名稱" min-width="160" />
              <el-table-column prop="account_type" label="類型" min-width="100" />
              <el-table-column prop="fx_code" label="幣別" width="80" />
              <el-table-column label="啟用" width="80">
                <template #default="{ row }">
                  <StatusBadge :value="row.in_use" />
                </template>
              </el-table-column>
              <el-table-column prop="discount" label="折扣" width="80" />
              <el-table-column prop="owner" label="持有人" min-width="120">
                <template #default="{ row }">{{ row.owner ?? '—' }}</template>
              </el-table-column>
              <el-table-column prop="account_index" label="排序" width="80" />
              <el-table-column label="操作" width="160" fixed="right">
                <template #default="{ row }">
                  <el-button link type="primary" @click="openEditAccount(row)">編輯</el-button>
                  <el-button link type="danger" @click="handleDeleteAccount(row)">刪除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </DataListCard>
      </el-tab-pane>

      <el-tab-pane label="分類" name="codes">
        <div class="bg-surface-container rounded-xl border border-outline-variant p-12 flex justify-center">
          <EmptyState message="開發中" />
        </div>
      </el-tab-pane>

      <el-tab-pane label="信用卡" name="credit-cards">
        <div class="bg-surface-container rounded-xl border border-outline-variant p-12 flex justify-center">
          <EmptyState message="開發中" />
        </div>
      </el-tab-pane>
    </el-tabs>

    <FormDialog
      v-model="accountDialogVisible"
      :title="accountFormMode === 'create' ? '新增帳戶' : '編輯帳戶'"
      :loading="accountSubmitting"
      width="540px"
      @submit="submitAccount"
    >
      <el-form
        ref="accountFormRef"
        :model="accountForm"
        :rules="accountFormRules"
        label-width="100px"
      >
        <el-form-item label="帳戶 ID" prop="account_id">
          <el-input
            v-model="accountForm.account_id"
            :disabled="accountFormMode === 'edit'"
            placeholder="如 BANK-CHASE-01"
          />
        </el-form-item>
        <el-form-item label="名稱" prop="name">
          <el-input v-model="accountForm.name" />
        </el-form-item>
        <el-form-item label="類型" prop="account_type">
          <el-input v-model="accountForm.account_type" placeholder="如 BANK / CASH / INVEST" />
        </el-form-item>
        <el-form-item label="幣別" prop="fx_code">
          <el-input v-model="accountForm.fx_code" placeholder="如 TWD / USD" />
        </el-form-item>
        <el-form-item label="計入資產">
          <el-radio-group v-model="accountForm.is_calculate">
            <el-radio value="Y">是</el-radio>
            <el-radio value="N">否</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="啟用">
          <el-radio-group v-model="accountForm.in_use">
            <el-radio value="Y">啟用</el-radio>
            <el-radio value="N">停用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="折扣">
          <el-input-number
            v-model="accountForm.discount"
            :precision="4"
            :step="0.01"
            :min="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="持有人">
          <el-input v-model="ownerModel" />
        </el-form-item>
        <el-form-item label="備註">
          <el-input v-model="memoModel" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number
            v-model="accountIndexModel"
            :min="0"
            :step="1"
            :precision="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
    </FormDialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Plus as PlusIcon } from '@element-plus/icons-vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import DataListCard from '@/components/ui/DataListCard.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import FormDialog from '@/components/ui/FormDialog.vue'
import { useConfirm } from '@/composables/useConfirm'
import { useSettingStore } from '@/stores/setting'
import {
  createAccount,
  updateAccount,
  deleteAccount,
} from '@/api/setting'
import type { Account, AccountCreate } from '@/types/models'

const store = useSettingStore()
const confirm = useConfirm()

const activeTab = ref<'accounts' | 'codes' | 'credit-cards'>('accounts')

onMounted(() => {
  void store.fetchAccounts()
})

const codesLoaded = ref(false)
const creditCardsLoaded = ref(false)
watch(activeTab, (tab) => {
  if (tab === 'codes' && !codesLoaded.value) {
    codesLoaded.value = true
    void store.fetchCodesWithSub()
  }
  if (tab === 'credit-cards' && !creditCardsLoaded.value) {
    creditCardsLoaded.value = true
    void store.fetchCreditCards()
  }
})

// ─── Account dialog ──────────────────────────────────────────────────────────

const accountDialogVisible = ref(false)
const accountFormMode = ref<'create' | 'edit'>('create')
const accountSubmitting = ref(false)
const accountFormRef = ref<FormInstance>()
const editingAccountId = ref<number | null>(null)

function emptyAccountForm(): AccountCreate {
  return {
    account_id: '',
    name: '',
    account_type: '',
    fx_code: 'TWD',
    is_calculate: 'Y',
    in_use: 'Y',
    discount: 1,
    memo: null,
    owner: null,
    account_index: undefined,
  }
}

const accountForm = ref<AccountCreate>(emptyAccountForm())

const ownerModel = computed<string>({
  get: () => accountForm.value.owner ?? '',
  set: (v) => {
    accountForm.value.owner = v ? v : null
  },
})

const memoModel = computed<string>({
  get: () => accountForm.value.memo ?? '',
  set: (v) => {
    accountForm.value.memo = v ? v : null
  },
})

const accountIndexModel = computed<number | undefined>({
  get: () => accountForm.value.account_index,
  set: (v) => {
    accountForm.value.account_index = typeof v === 'number' ? v : undefined
  },
})

const accountFormRules: FormRules = {
  account_id: [{ required: true, message: '請輸入帳戶 ID', trigger: 'blur' }],
  name: [{ required: true, message: '請輸入名稱', trigger: 'blur' }],
  account_type: [{ required: true, message: '請輸入類型', trigger: 'blur' }],
  fx_code: [{ required: true, message: '請輸入幣別', trigger: 'blur' }],
}

function openCreateAccount() {
  accountFormMode.value = 'create'
  editingAccountId.value = null
  accountForm.value = emptyAccountForm()
  accountDialogVisible.value = true
}

function openEditAccount(row: Account) {
  accountFormMode.value = 'edit'
  editingAccountId.value = row.id
  accountForm.value = {
    account_id: row.account_id,
    name: row.name,
    account_type: row.account_type,
    fx_code: row.fx_code,
    is_calculate: row.is_calculate,
    in_use: row.in_use,
    discount: row.discount,
    memo: row.memo ?? null,
    owner: row.owner ?? null,
    account_index: row.account_index,
  }
  accountDialogVisible.value = true
}

async function submitAccount() {
  if (!accountFormRef.value) return
  const valid = await accountFormRef.value.validate().catch(() => false)
  if (!valid) return
  accountSubmitting.value = true
  try {
    if (accountFormMode.value === 'create') {
      await createAccount({ ...accountForm.value })
      ElMessage.success('新增成功')
    } else if (editingAccountId.value !== null) {
      const { account_id, ...rest } = accountForm.value
      void account_id
      await updateAccount(editingAccountId.value, rest)
      ElMessage.success('更新成功')
    }
    accountDialogVisible.value = false
    await store.fetchAccounts()
  } finally {
    accountSubmitting.value = false
  }
}

async function handleDeleteAccount(row: Account) {
  const ok = await confirm({
    title: '刪除帳戶',
    message: `確定要刪除「${row.name}」?`,
    type: 'warning',
  })
  if (!ok) return
  await deleteAccount(row.id)
  ElMessage.success('已刪除')
  await store.fetchAccounts()
}
</script>

<style scoped>
.settings-tabs :deep(.el-tabs__nav-wrap::after) {
  background-color: var(--ds-color-outline-variant);
}
</style>
