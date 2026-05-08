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
        <DataListCard title="主分類 / 子分類">
          <template #menu>
            <el-button type="primary" :icon="PlusIcon" @click="openCreateCode">
              新增主分類
            </el-button>
          </template>

          <div class="p-4">
            <el-table
              :data="store.codesWithSub"
              v-loading="store.codesLoading"
              row-key="code_id"
              stripe
              empty-text="尚無主分類"
            >
              <el-table-column type="expand">
                <template #default="{ row }">
                  <div class="px-6 py-4 flex flex-col gap-3">
                    <SectionHeader
                      :title="`${row.code_id} 子分類`"
                      action-text="新增子分類"
                      @action="openCreateSubCode(row)"
                    />
                    <el-table
                      :data="row.sub_codes ?? []"
                      empty-text="尚無子分類"
                      size="small"
                    >
                      <el-table-column prop="code_id" label="子分類 ID" min-width="120" />
                      <el-table-column prop="name" label="名稱" min-width="160" />
                      <el-table-column label="啟用" width="80">
                        <template #default="{ row: sub }">
                          <StatusBadge :value="sub.in_use" />
                        </template>
                      </el-table-column>
                      <el-table-column prop="code_index" label="排序" width="80" />
                      <el-table-column label="操作" width="160" fixed="right">
                        <template #default="{ row: sub }">
                          <el-button link type="primary" @click="openEditSubCode(row, sub)">
                            編輯
                          </el-button>
                          <el-button link type="danger" @click="handleDeleteSubCode(sub)">
                            刪除
                          </el-button>
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="code_id" label="分類 ID" min-width="120" />
              <el-table-column prop="name" label="名稱" min-width="160" />
              <el-table-column prop="code_type" label="類型" min-width="110" />
              <el-table-column label="啟用" width="80">
                <template #default="{ row }">
                  <StatusBadge :value="row.in_use" />
                </template>
              </el-table-column>
              <el-table-column prop="code_group" label="群組" min-width="120">
                <template #default="{ row }">{{ row.code_group ?? '—' }}</template>
              </el-table-column>
              <el-table-column prop="code_index" label="排序" width="80" />
              <el-table-column label="操作" width="160" fixed="right">
                <template #default="{ row }">
                  <el-button link type="primary" @click="openEditCode(row)">編輯</el-button>
                  <el-button link type="danger" @click="handleDeleteCode(row)">刪除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </DataListCard>
      </el-tab-pane>

      <el-tab-pane label="信用卡" name="credit-cards">
        <div class="bg-surface-container rounded-xl border border-outline-variant p-12 flex justify-center">
          <EmptyState message="開發中" />
        </div>
      </el-tab-pane>
    </el-tabs>

    <FormDialog
      v-model="codeDialogVisible"
      :title="codeFormMode === 'create' ? '新增主分類' : '編輯主分類'"
      :loading="codeSubmitting"
      width="520px"
      @submit="submitCode"
    >
      <el-form
        ref="codeFormRef"
        :model="codeForm"
        :rules="codeFormRules"
        label-width="100px"
      >
        <el-form-item label="分類 ID" prop="code_id">
          <el-input
            v-model="codeForm.code_id"
            :disabled="codeFormMode === 'edit'"
            placeholder="如 E01"
          />
        </el-form-item>
        <el-form-item label="類型" prop="code_type">
          <el-select v-model="codeForm.code_type" style="width: 100%">
            <el-option
              v-for="opt in CODE_TYPE_OPTIONS"
              :key="opt"
              :label="opt"
              :value="opt"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="名稱" prop="name">
          <el-input v-model="codeForm.name" />
        </el-form-item>
        <el-form-item label="啟用">
          <el-radio-group v-model="codeForm.in_use">
            <el-radio value="Y">啟用</el-radio>
            <el-radio value="N">停用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="群組">
          <el-input v-model="codeGroupModel" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number
            v-model="codeIndexModel"
            :min="0"
            :step="1"
            :precision="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
    </FormDialog>

    <FormDialog
      v-model="subCodeDialogVisible"
      :title="subCodeFormMode === 'create' ? '新增子分類' : '編輯子分類'"
      :loading="subCodeSubmitting"
      width="480px"
      @submit="submitSubCode"
    >
      <el-form
        ref="subCodeFormRef"
        :model="subCodeForm"
        :rules="subCodeFormRules"
        label-width="100px"
      >
        <el-form-item label="父分類">
          <el-input :model-value="subCodeForm.parent_id ?? ''" disabled />
        </el-form-item>
        <el-form-item label="子分類 ID" prop="code_id">
          <el-input
            v-model="subCodeForm.code_id"
            :disabled="subCodeFormMode === 'edit'"
          />
        </el-form-item>
        <el-form-item label="名稱" prop="name">
          <el-input v-model="subCodeForm.name" />
        </el-form-item>
        <el-form-item label="啟用">
          <el-radio-group v-model="subCodeForm.in_use">
            <el-radio value="Y">啟用</el-radio>
            <el-radio value="N">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
    </FormDialog>

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
import SectionHeader from '@/components/ui/SectionHeader.vue'
import { useConfirm } from '@/composables/useConfirm'
import { useSettingStore } from '@/stores/setting'
import {
  createAccount,
  updateAccount,
  deleteAccount,
  createCode,
  updateCode,
  deleteCode,
  createSubCode,
  updateSubCode,
  deleteSubCode,
} from '@/api/setting'
import type {
  Account,
  AccountCreate,
  CodeData,
  CodeDataCreate,
  CodeDataWithSub,
} from '@/types/models'

const CODE_TYPE_OPTIONS = ['Floating', 'Fixed', 'Invest', 'Income', 'Transfer'] as const

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

// ─── Main code dialog ────────────────────────────────────────────────────────

const codeDialogVisible = ref(false)
const codeFormMode = ref<'create' | 'edit'>('create')
const codeSubmitting = ref(false)
const codeFormRef = ref<FormInstance>()
const editingCodeId = ref<string | null>(null)

function emptyCodeForm(): CodeDataCreate {
  return {
    code_id: '',
    code_type: 'Floating',
    name: '',
    parent_id: null,
    code_group: null,
    in_use: 'Y',
    code_index: undefined,
  }
}

const codeForm = ref<CodeDataCreate>(emptyCodeForm())

const codeGroupModel = computed<string>({
  get: () => codeForm.value.code_group ?? '',
  set: (v) => {
    codeForm.value.code_group = v ? v : null
  },
})

const codeIndexModel = computed<number | undefined>({
  get: () => codeForm.value.code_index,
  set: (v) => {
    codeForm.value.code_index = typeof v === 'number' ? v : undefined
  },
})

const codeFormRules: FormRules = {
  code_id: [{ required: true, message: '請輸入分類 ID', trigger: 'blur' }],
  code_type: [{ required: true, message: '請選擇類型', trigger: 'change' }],
  name: [{ required: true, message: '請輸入名稱', trigger: 'blur' }],
}

function openCreateCode() {
  codeFormMode.value = 'create'
  editingCodeId.value = null
  codeForm.value = emptyCodeForm()
  codeDialogVisible.value = true
}

function openEditCode(row: CodeDataWithSub) {
  codeFormMode.value = 'edit'
  editingCodeId.value = row.code_id
  codeForm.value = {
    code_id: row.code_id,
    code_type: row.code_type,
    name: row.name,
    parent_id: row.parent_id ?? null,
    code_group: row.code_group ?? null,
    in_use: row.in_use,
    code_index: row.code_index,
  }
  codeDialogVisible.value = true
}

async function submitCode() {
  if (!codeFormRef.value) return
  const valid = await codeFormRef.value.validate().catch(() => false)
  if (!valid) return
  codeSubmitting.value = true
  try {
    if (codeFormMode.value === 'create') {
      await createCode({ ...codeForm.value })
      ElMessage.success('新增成功')
    } else if (editingCodeId.value) {
      const { code_id, ...rest } = codeForm.value
      void code_id
      await updateCode(editingCodeId.value, rest)
      ElMessage.success('更新成功')
    }
    codeDialogVisible.value = false
    await store.fetchCodesWithSub()
  } finally {
    codeSubmitting.value = false
  }
}

async function handleDeleteCode(row: CodeDataWithSub) {
  const ok = await confirm({
    title: '刪除主分類',
    message: `確定要刪除「${row.name}」? 子分類需先清空。`,
    type: 'warning',
  })
  if (!ok) return
  await deleteCode(row.code_id)
  ElMessage.success('已刪除')
  await store.fetchCodesWithSub()
}

// ─── Sub-code dialog ─────────────────────────────────────────────────────────

const subCodeDialogVisible = ref(false)
const subCodeFormMode = ref<'create' | 'edit'>('create')
const subCodeSubmitting = ref(false)
const subCodeFormRef = ref<FormInstance>()
const editingSubCodeId = ref<string | null>(null)

function emptySubCodeForm(parent: CodeDataWithSub): CodeDataCreate {
  return {
    code_id: '',
    code_type: parent.code_type,
    name: '',
    parent_id: parent.code_id,
    code_group: parent.code_group ?? null,
    in_use: 'Y',
    code_index: undefined,
  }
}

const subCodeForm = ref<CodeDataCreate>({
  code_id: '',
  code_type: '',
  name: '',
  parent_id: null,
  in_use: 'Y',
})

const subCodeFormRules: FormRules = {
  code_id: [{ required: true, message: '請輸入子分類 ID', trigger: 'blur' }],
  name: [{ required: true, message: '請輸入名稱', trigger: 'blur' }],
}

function openCreateSubCode(parent: CodeDataWithSub) {
  subCodeFormMode.value = 'create'
  editingSubCodeId.value = null
  subCodeForm.value = emptySubCodeForm(parent)
  subCodeDialogVisible.value = true
}

function openEditSubCode(parent: CodeDataWithSub, row: CodeData) {
  subCodeFormMode.value = 'edit'
  editingSubCodeId.value = row.code_id
  subCodeForm.value = {
    code_id: row.code_id,
    code_type: row.code_type || parent.code_type,
    name: row.name,
    parent_id: parent.code_id,
    code_group: row.code_group ?? parent.code_group ?? null,
    in_use: row.in_use,
    code_index: row.code_index,
  }
  subCodeDialogVisible.value = true
}

async function submitSubCode() {
  if (!subCodeFormRef.value) return
  const valid = await subCodeFormRef.value.validate().catch(() => false)
  if (!valid) return
  subCodeSubmitting.value = true
  try {
    if (subCodeFormMode.value === 'create') {
      await createSubCode({ ...subCodeForm.value })
      ElMessage.success('新增成功')
    } else if (editingSubCodeId.value) {
      const { code_id, ...rest } = subCodeForm.value
      void code_id
      await updateSubCode(editingSubCodeId.value, rest)
      ElMessage.success('更新成功')
    }
    subCodeDialogVisible.value = false
    await store.fetchCodesWithSub()
  } finally {
    subCodeSubmitting.value = false
  }
}

async function handleDeleteSubCode(row: CodeData) {
  const ok = await confirm({
    title: '刪除子分類',
    message: `確定要刪除「${row.name}」?`,
    type: 'warning',
  })
  if (!ok) return
  await deleteSubCode(row.code_id)
  ElMessage.success('已刪除')
  await store.fetchCodesWithSub()
}
</script>

<style scoped>
.settings-tabs :deep(.el-tabs__nav-wrap::after) {
  background-color: var(--ds-color-outline-variant);
}
</style>
