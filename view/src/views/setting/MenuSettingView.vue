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
                  <RowActions variant="link" @edit="openEditAccount(row)" @delete="handleDeleteAccount(row)" />
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
                          <RowActions
                            variant="link"
                            @edit="openEditSubCode(row, sub)"
                            @delete="handleDeleteSubCode(sub)"
                          />
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="code_id" label="分類 ID" min-width="120" />
              <el-table-column prop="name" label="名稱" min-width="160" />
              <el-table-column prop="code_type" label="類型" min-width="110" />
              <el-table-column label="年度事件" width="100">
                <template #default="{ row }">
                  <el-tag v-if="row.is_annual_event" size="small" type="warning">事件</el-tag>
                  <span v-else class="text-on-surface-muted">—</span>
                </template>
              </el-table-column>
              <el-table-column label="啟用" width="80">
                <template #default="{ row }">
                  <StatusBadge :value="row.in_use" />
                </template>
              </el-table-column>
              <el-table-column prop="code_index" label="排序" width="80" />
              <el-table-column label="操作" width="160" fixed="right">
                <template #default="{ row }">
                  <RowActions variant="link" @edit="openEditCode(row)" @delete="handleDeleteCode(row)" />
                </template>
              </el-table-column>
            </el-table>
          </div>
        </DataListCard>
      </el-tab-pane>

      <el-tab-pane label="信用卡" name="credit-cards">
        <DataListCard title="信用卡清單">
          <template #menu>
            <el-button type="primary" :icon="PlusIcon" @click="openCreateCreditCard">
              新增信用卡
            </el-button>
          </template>

          <div class="p-4">
            <el-table
              :data="store.creditCards"
              v-loading="store.creditCardsLoading"
              row-key="credit_card_id"
              stripe
              empty-text="尚無信用卡"
            >
              <el-table-column prop="credit_card_id" label="卡片 ID" min-width="140" />
              <el-table-column prop="card_name" label="卡名" min-width="160" />
              <el-table-column prop="card_no" label="卡號" min-width="160">
                <template #default="{ row }">{{ row.card_no ?? '—' }}</template>
              </el-table-column>
              <el-table-column prop="last_day" label="結帳日" width="90">
                <template #default="{ row }">{{ row.last_day ?? '—' }}</template>
              </el-table-column>
              <el-table-column prop="charge_day" label="扣款日" width="90">
                <template #default="{ row }">{{ row.charge_day ?? '—' }}</template>
              </el-table-column>
              <el-table-column prop="limit_date" label="繳費日" width="90">
                <template #default="{ row }">{{ row.limit_date ?? '—' }}</template>
              </el-table-column>
              <el-table-column prop="fx_code" label="幣別" width="80" />
              <el-table-column label="啟用" width="80">
                <template #default="{ row }">
                  <StatusBadge :value="row.in_use" />
                </template>
              </el-table-column>
              <el-table-column prop="credit_card_index" label="排序" width="80" />
              <el-table-column label="操作" width="160" fixed="right">
                <template #default="{ row }">
                  <RowActions variant="link" @edit="openEditCreditCard(row)" @delete="handleDeleteCreditCard(row)" />
                </template>
              </el-table-column>
            </el-table>
          </div>
        </DataListCard>
      </el-tab-pane>
    </el-tabs>

    <FormDialog
      v-model="creditCardDialogVisible"
      :title="creditCardFormMode === 'create' ? '新增信用卡' : '編輯信用卡'"
      :loading="creditCardSubmitting"
      width="540px"
      @submit="submitCreditCard"
    >
      <el-form
        ref="creditCardFormRef"
        :model="creditCardForm"
        :rules="creditCardFormRules"
        label-width="100px"
      >
        <el-form-item label="卡片 ID" prop="credit_card_id">
          <el-input
            v-model="creditCardForm.credit_card_id"
            :disabled="creditCardFormMode === 'edit'"
            placeholder="如 CC-VISA-01"
          />
        </el-form-item>
        <el-form-item label="卡名" prop="card_name">
          <el-input v-model="creditCardForm.card_name" />
        </el-form-item>
        <el-form-item label="卡號">
          <el-input v-model="cardNoModel" placeholder="如 4111-XXXX-XXXX-1111" />
        </el-form-item>
        <el-form-item label="結帳日">
          <el-input-number
            v-model="lastDayModel"
            :min="1"
            :max="31"
            :precision="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="扣款日">
          <el-input-number
            v-model="chargeDayModel"
            :min="1"
            :max="31"
            :precision="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="繳費日">
          <el-input-number
            v-model="limitDateModel"
            :min="1"
            :max="31"
            :precision="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="回饋方式">
          <el-input v-model="feedbackWayModel" placeholder="如 cashback / mileage" />
        </el-form-item>
        <el-form-item label="幣別" prop="fx_code">
          <el-input v-model="creditCardForm.fx_code" />
        </el-form-item>
        <el-form-item label="啟用">
          <el-radio-group v-model="creditCardForm.in_use">
            <el-radio value="Y">啟用</el-radio>
            <el-radio value="N">停用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number
            v-model="creditCardIndexModel"
            :min="0"
            :step="1"
            :precision="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="備註">
          <el-input v-model="creditCardNoteModel" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
    </FormDialog>

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
        <el-form-item label="年度事件">
          <div class="flex flex-col gap-1">
            <el-switch v-model="codeForm.is_annual_event" />
            <span class="text-xs text-on-surface-muted">
              開啟後此分類改以「全年一筆額度」編列,不分攤到 12 個月 (如過年、年節送禮)
            </span>
          </div>
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
import { type FormInstance, type FormRules } from 'element-plus'
import { Plus as PlusIcon } from '@element-plus/icons-vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import DataListCard from '@/components/ui/DataListCard.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import FormDialog from '@/components/ui/FormDialog.vue'
import SectionHeader from '@/components/ui/SectionHeader.vue'
import RowActions from '@/components/ui/RowActions.vue'
import { useCrudDialog } from '@/composables/useCrudDialog'
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
  createCreditCard,
  updateCreditCard,
  deleteCreditCard,
} from '@/api/setting'
import type {
  Account,
  AccountCreate,
  CodeData,
  CodeDataCreate,
  CodeDataWithSub,
  CreditCard,
  CreditCardCreate,
} from '@/types/models'

const CODE_TYPE_OPTIONS = ['Floating', 'Fixed', 'Invest', 'Income', 'Transfer'] as const

const store = useSettingStore()

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

const accountFormRef = ref<FormInstance>()

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

const accountFormRules: FormRules = {
  account_id: [{ required: true, message: '請輸入帳戶 ID', trigger: 'blur' }],
  name: [{ required: true, message: '請輸入名稱', trigger: 'blur' }],
  account_type: [{ required: true, message: '請輸入類型', trigger: 'blur' }],
  fx_code: [{ required: true, message: '請輸入幣別', trigger: 'blur' }],
}

const {
  dialogVisible: accountDialogVisible,
  formMode: accountFormMode,
  submitting: accountSubmitting,
  form: accountForm,
  openCreate: openCreateAccount,
  openEdit: openEditAccount,
  submit: submitAccount,
  remove: handleDeleteAccount,
} = useCrudDialog<Account, AccountCreate>({
  formRef: accountFormRef,
  emptyForm: emptyAccountForm,
  toForm: (row) => ({
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
  }),
  getId: (row) => row.id,
  create: (form) => createAccount({ ...form }),
  update: (id, form) => {
    const { account_id, ...rest } = form
    void account_id
    return updateAccount(id as number, rest)
  },
  remove: (id) => deleteAccount(id as number),
  refetch: () => store.fetchAccounts(),
  confirmDelete: (row) => ({ title: '刪除帳戶', message: `確定要刪除「${row.name}」?` }),
})

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

// ─── Main code dialog ────────────────────────────────────────────────────────

const codeFormRef = ref<FormInstance>()

function emptyCodeForm(): CodeDataCreate {
  return {
    code_id: '',
    code_type: 'Floating',
    name: '',
    parent_id: null,
    in_use: 'Y',
    code_index: undefined,
    is_annual_event: false,
  }
}

const codeFormRules: FormRules = {
  code_id: [{ required: true, message: '請輸入分類 ID', trigger: 'blur' }],
  code_type: [{ required: true, message: '請選擇類型', trigger: 'change' }],
  name: [{ required: true, message: '請輸入名稱', trigger: 'blur' }],
}

const {
  dialogVisible: codeDialogVisible,
  formMode: codeFormMode,
  submitting: codeSubmitting,
  form: codeForm,
  openCreate: openCreateCode,
  openEdit: openEditCode,
  submit: submitCode,
  remove: handleDeleteCode,
} = useCrudDialog<CodeDataWithSub, CodeDataCreate>({
  formRef: codeFormRef,
  emptyForm: emptyCodeForm,
  toForm: (row) => ({
    code_id: row.code_id,
    code_type: row.code_type,
    name: row.name,
    parent_id: row.parent_id ?? null,
    in_use: row.in_use,
    code_index: row.code_index,
    is_annual_event: row.is_annual_event,
  }),
  getId: (row) => row.code_id,
  create: (form) => createCode({ ...form }),
  update: (id, form) => {
    const { code_id, ...rest } = form
    void code_id
    return updateCode(id as string, rest)
  },
  remove: (id) => deleteCode(id as string),
  refetch: () => store.fetchCodesWithSub(),
  confirmDelete: (row) => ({
    title: '刪除主分類',
    message: `確定要刪除「${row.name}」? 子分類需先清空。`,
  }),
})

const codeIndexModel = computed<number | undefined>({
  get: () => codeForm.value.code_index,
  set: (v) => {
    codeForm.value.code_index = typeof v === 'number' ? v : undefined
  },
})

// ─── Sub-code dialog ─────────────────────────────────────────────────────────

const subCodeFormRef = ref<FormInstance>()
const subCodeParent = ref<CodeDataWithSub | null>(null)

function emptySubCodeForm(parent: CodeDataWithSub): CodeDataCreate {
  return {
    code_id: '',
    code_type: parent.code_type,
    name: '',
    parent_id: parent.code_id,
    in_use: 'Y',
    code_index: undefined,
  }
}

const subCodeFormRules: FormRules = {
  code_id: [{ required: true, message: '請輸入子分類 ID', trigger: 'blur' }],
  name: [{ required: true, message: '請輸入名稱', trigger: 'blur' }],
}

const {
  dialogVisible: subCodeDialogVisible,
  formMode: subCodeFormMode,
  submitting: subCodeSubmitting,
  form: subCodeForm,
  openCreate: openCreateSubCodeBase,
  openEdit: openEditSubCodeBase,
  submit: submitSubCode,
  remove: handleDeleteSubCode,
} = useCrudDialog<CodeData, CodeDataCreate>({
  formRef: subCodeFormRef,
  // The open* wrappers below always set `subCodeParent` before a dialog opens;
  // the null branch only covers the eager emptyForm() call during setup.
  emptyForm: () =>
    subCodeParent.value
      ? emptySubCodeForm(subCodeParent.value)
      : { code_id: '', code_type: '', name: '', parent_id: null, in_use: 'Y' },
  toForm: (row) => ({
    code_id: row.code_id,
    code_type: row.code_type || subCodeParent.value!.code_type,
    name: row.name,
    parent_id: subCodeParent.value!.code_id,
    in_use: row.in_use,
    code_index: row.code_index,
  }),
  getId: (row) => row.code_id,
  create: (form) => createSubCode({ ...form }),
  update: (id, form) => {
    const { code_id, ...rest } = form
    void code_id
    return updateSubCode(id as string, rest)
  },
  remove: (id) => deleteSubCode(id as string),
  refetch: () => store.fetchCodesWithSub(),
  confirmDelete: (row) => ({ title: '刪除子分類', message: `確定要刪除「${row.name}」?` }),
})

function openCreateSubCode(parent: CodeDataWithSub) {
  subCodeParent.value = parent
  openCreateSubCodeBase()
}

function openEditSubCode(parent: CodeDataWithSub, row: CodeData) {
  subCodeParent.value = parent
  openEditSubCodeBase(row)
}

// ─── Credit-card dialog ──────────────────────────────────────────────────────

const creditCardFormRef = ref<FormInstance>()

function emptyCreditCardForm(): CreditCardCreate {
  return {
    credit_card_id: '',
    card_name: '',
    card_no: null,
    last_day: null,
    charge_day: null,
    limit_date: null,
    feedback_way: null,
    fx_code: 'TWD',
    in_use: 'Y',
    credit_card_index: undefined,
    note: null,
  }
}

const creditCardFormRules: FormRules = {
  credit_card_id: [{ required: true, message: '請輸入卡片 ID', trigger: 'blur' }],
  card_name: [{ required: true, message: '請輸入卡名', trigger: 'blur' }],
  fx_code: [{ required: true, message: '請輸入幣別', trigger: 'blur' }],
}

const {
  dialogVisible: creditCardDialogVisible,
  formMode: creditCardFormMode,
  submitting: creditCardSubmitting,
  form: creditCardForm,
  openCreate: openCreateCreditCard,
  openEdit: openEditCreditCard,
  submit: submitCreditCard,
  remove: handleDeleteCreditCard,
} = useCrudDialog<CreditCard, CreditCardCreate>({
  formRef: creditCardFormRef,
  emptyForm: emptyCreditCardForm,
  toForm: (row) => ({
    credit_card_id: row.credit_card_id,
    card_name: row.card_name,
    card_no: row.card_no ?? null,
    last_day: row.last_day ?? null,
    charge_day: row.charge_day ?? null,
    limit_date: row.limit_date ?? null,
    feedback_way: row.feedback_way ?? null,
    fx_code: row.fx_code,
    in_use: row.in_use,
    credit_card_index: row.credit_card_index,
    note: row.note ?? null,
  }),
  getId: (row) => row.credit_card_id,
  create: (form) => createCreditCard({ ...form }),
  update: (id, form) => {
    const { credit_card_id, ...rest } = form
    void credit_card_id
    return updateCreditCard(id as string, rest)
  },
  remove: (id) => deleteCreditCard(id as string),
  refetch: () => store.fetchCreditCards(),
  confirmDelete: (row) => ({ title: '刪除信用卡', message: `確定要刪除「${row.card_name}」?` }),
})

const cardNoModel = computed<string>({
  get: () => creditCardForm.value.card_no ?? '',
  set: (v) => {
    creditCardForm.value.card_no = v ? v : null
  },
})

function makeNumberNullableModel(field: 'last_day' | 'charge_day' | 'limit_date') {
  return computed<number | undefined>({
    get: () => creditCardForm.value[field] ?? undefined,
    set: (v) => {
      creditCardForm.value[field] = typeof v === 'number' ? v : null
    },
  })
}

const lastDayModel = makeNumberNullableModel('last_day')
const chargeDayModel = makeNumberNullableModel('charge_day')
const limitDateModel = makeNumberNullableModel('limit_date')

const feedbackWayModel = computed<string>({
  get: () => creditCardForm.value.feedback_way ?? '',
  set: (v) => {
    creditCardForm.value.feedback_way = v ? v : null
  },
})

const creditCardIndexModel = computed<number | undefined>({
  get: () => creditCardForm.value.credit_card_index,
  set: (v) => {
    creditCardForm.value.credit_card_index = typeof v === 'number' ? v : undefined
  },
})

const creditCardNoteModel = computed<string>({
  get: () => creditCardForm.value.note ?? '',
  set: (v) => {
    creditCardForm.value.note = v ? v : null
  },
})
</script>

<style scoped>
.settings-tabs :deep(.el-tabs__nav-wrap::after) {
  background-color: var(--ds-color-outline-variant);
}
</style>
