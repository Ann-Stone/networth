<template>
  <div class="flex flex-col gap-8">
    <PageHeader title="資產負債管理" subtitle="股票 / 房產 / 保險 / 貸款 / 其他資產" />

    <el-tabs v-model="activeTab" class="other-assets-tabs">
      <!-- ─── Stocks ─────────────────────────────────────────── -->
      <el-tab-pane label="股票" name="stocks">
        <section class="flex flex-col gap-4">
          <SectionHeader title="股票持有">
            <template #actions>
              <el-select
                v-model="stocksAssetId"
                placeholder="選擇資產分類"
                style="width: 240px"
                :disabled="stockCategoryOptions.length === 0"
              >
                <el-option
                  v-for="cat in stockCategoryOptions"
                  :key="cat.asset_id"
                  :label="cat.asset_name"
                  :value="cat.asset_id"
                />
              </el-select>
              <el-button
                type="primary"
                :icon="Plus"
                size="small"
                :disabled="!stocksAssetId"
                @click="openCreateStock"
              >
                新增
              </el-button>
            </template>
          </SectionHeader>

          <el-skeleton v-if="store.stocksLoading" :rows="4" animated />
          <EmptyState
            v-else-if="!stocksAssetId"
            message="請先選擇資產分類"
          />
          <EmptyState
            v-else-if="store.stocks.length === 0"
            message="尚無股票持有資料"
          />
          <el-table
            v-else
            :data="store.stocks"
            stripe
            border
            style="width: 100%"
            @expand-change="onStockExpandChange"
          >
            <el-table-column type="expand">
              <template #default="{ row }">
                <div class="px-6 py-4 flex flex-col gap-3">
                  <div class="flex items-center justify-between">
                    <span class="text-on-surface font-medium">交易明細</span>
                    <el-button
                      type="primary"
                      :icon="Plus"
                      size="small"
                      @click="openCreateStockDetail(row)"
                    >
                      新增明細
                    </el-button>
                  </div>
                  <el-skeleton
                    v-if="stockDetailsLoadingByStock.get(row.stock_id)"
                    :rows="3"
                    animated
                  />
                  <EmptyState
                    v-else-if="(stockDetailsByStock.get(row.stock_id)?.length ?? 0) === 0"
                    message="尚無交易明細"
                  />
                  <el-table
                    v-else
                    :data="stockDetailsByStock.get(row.stock_id) ?? []"
                    border
                    size="small"
                  >
                    <el-table-column prop="excute_date" label="日期" width="110" />
                    <el-table-column prop="excute_type" label="類型" width="100" />
                    <el-table-column label="數量" width="120" align="right">
                      <template #default="{ row: d }">
                        {{ d.excute_amount }}
                      </template>
                    </el-table-column>
                    <el-table-column label="單價" width="160" align="right">
                      <template #default="{ row: d }">
                        <MoneyDisplay :amount="d.excute_price" size="sm" />
                      </template>
                    </el-table-column>
                    <el-table-column prop="account_name" label="結算帳戶" min-width="160" />
                    <el-table-column prop="memo" label="備註" min-width="120">
                      <template #default="{ row: d }">
                        <span>{{ d.memo ?? '' }}</span>
                      </template>
                    </el-table-column>
                    <el-table-column label="操作" width="180" align="center">
                      <template #default="{ row: d }">
                        <el-button size="small" :icon="Edit" @click="openEditStockDetail(row, d)">
                          編輯
                        </el-button>
                        <el-button
                          size="small"
                          type="danger"
                          :icon="Delete"
                          @click="handleDeleteStockDetail(row, d)"
                        >
                          刪除
                        </el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="stock_id" label="持有 ID" width="160" />
            <el-table-column prop="stock_code" label="代號" width="140" />
            <el-table-column prop="stock_name" label="名稱" min-width="200" />
            <el-table-column label="預計投入" width="200" align="right">
              <template #default="{ row }">
                <MoneyDisplay :amount="row.expected_spend" size="sm" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" align="center">
              <template #default="{ row }">
                <el-button size="small" :icon="Edit" @click="openEditStock(row)">
                  編輯
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  :icon="Delete"
                  @click="handleDeleteStock(row)"
                >
                  刪除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </section>
      </el-tab-pane>

      <!-- ─── Estates (placeholder) ──────────────────────────── -->
      <el-tab-pane label="房產" name="estates">
        <EmptyState message="開發中" />
      </el-tab-pane>

      <!-- ─── Insurances (placeholder) ───────────────────────── -->
      <el-tab-pane label="保險" name="insurances">
        <EmptyState message="開發中" />
      </el-tab-pane>

      <!-- ─── Loans (placeholder) ────────────────────────────── -->
      <el-tab-pane label="貸款" name="loans">
        <EmptyState message="開發中" />
      </el-tab-pane>

      <!-- ─── Other-Assets (placeholder) ─────────────────────── -->
      <el-tab-pane label="其他資產" name="other">
        <EmptyState message="開發中" />
      </el-tab-pane>
    </el-tabs>

    <!-- ─── Stock Create / Edit Dialog ─────────────────────────────────────── -->
    <FormDialog
      v-model="stockDialogVisible"
      :title="stockFormMode === 'create' ? '新增股票持有' : '編輯股票持有'"
      :loading="stockSubmitting"
      width="520px"
      @submit="submitStock"
    >
      <el-form
        ref="stockFormRef"
        :model="stockForm"
        :rules="stockFormRules"
        label-width="110px"
      >
        <el-form-item label="持有 ID" prop="stock_id">
          <el-input
            v-model="stockForm.stock_id"
            placeholder="例如 STK-H-001"
            :disabled="stockFormMode === 'edit'"
          />
        </el-form-item>
        <el-form-item label="代號" prop="stock_code">
          <el-input v-model="stockForm.stock_code" placeholder="例如 AAPL" />
        </el-form-item>
        <el-form-item label="名稱" prop="stock_name">
          <el-input v-model="stockForm.stock_name" placeholder="例如 Apple Inc." />
        </el-form-item>
        <el-form-item label="資產分類">
          <el-input :model-value="stockForm.asset_id" disabled />
        </el-form-item>
        <el-form-item label="預計投入" prop="expected_spend">
          <el-input-number
            v-model="stockForm.expected_spend"
            :precision="2"
            :step="1000"
            :min="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
    </FormDialog>

    <!-- ─── Stock Detail Create / Edit Dialog ──────────────────────────────── -->
    <FormDialog
      v-model="stockDetailDialogVisible"
      :title="stockDetailFormMode === 'create' ? '新增股票明細' : '編輯股票明細'"
      :loading="stockDetailSubmitting"
      width="560px"
      @submit="submitStockDetail"
    >
      <el-form
        ref="stockDetailFormRef"
        :model="stockDetailForm"
        :rules="stockDetailFormRules"
        label-width="110px"
      >
        <el-form-item label="持有 ID">
          <el-input :model-value="stockDetailForm.stock_id" disabled />
        </el-form-item>
        <el-form-item label="日期" prop="excute_date">
          <el-date-picker
            v-model="stockDetailFormDate"
            type="date"
            format="YYYY/MM/DD"
            :clearable="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="類型" prop="excute_type">
          <el-select v-model="stockDetailForm.excute_type" style="width: 100%">
            <el-option label="買入 (buy)" value="buy" />
            <el-option label="賣出 (sell)" value="sell" />
            <el-option label="股票股利 (stock)" value="stock" />
            <el-option label="現金股利 (cash)" value="cash" />
          </el-select>
        </el-form-item>
        <el-form-item label="數量" prop="excute_amount">
          <el-input-number
            v-model="stockDetailForm.excute_amount"
            :precision="2"
            :step="1"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="單價" prop="excute_price">
          <el-input-number
            v-model="stockDetailForm.excute_price"
            :precision="2"
            :step="1"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="帳戶 ID" prop="account_id">
          <el-input v-model="stockDetailForm.account_id" placeholder="例如 BANK-CHASE-01" />
        </el-form-item>
        <el-form-item label="帳戶名稱" prop="account_name">
          <el-input v-model="stockDetailForm.account_name" placeholder="例如 Chase Checking" />
        </el-form-item>
        <el-form-item label="備註">
          <el-input
            v-model="stockDetailForm.memo"
            type="textarea"
            :rows="2"
            placeholder="(可選)"
          />
        </el-form-item>
      </el-form>
    </FormDialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, shallowReactive, watch } from 'vue'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import SectionHeader from '@/components/ui/SectionHeader.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import FormDialog from '@/components/ui/FormDialog.vue'
import { useConfirm } from '@/composables/useConfirm'
import { useOtherAssetsStore } from '@/stores/otherAssets'
import {
  createStock,
  createStockDetail,
  deleteStock,
  deleteStockDetail,
  getStockDetails,
  updateStock,
  updateStockDetail,
} from '@/api/otherAssets'
import type {
  StockAsset,
  StockAssetCreate,
  StockJournal,
  StockJournalCreate,
} from '@/types/models'

const store = useOtherAssetsStore()
const confirm = useConfirm()

const activeTab = ref<string>('stocks')

// ─── Stock category options ─────────────────────────────────────────────────
const stockCategoryOptions = computed(() =>
  [...store.otherAssets]
    .filter((a) => a.asset_type === 'stock' && a.in_use === 'Y')
    .sort((a, b) => a.asset_index - b.asset_index),
)

const stocksAssetId = ref<string>('')

watch(stockCategoryOptions, (options) => {
  if (!stocksAssetId.value && options.length > 0) {
    stocksAssetId.value = options[0]!.asset_id
  }
})

watch(stocksAssetId, (assetId) => {
  if (assetId) void fetchStocks(assetId)
})

async function fetchStocks(assetId: string) {
  await store.fetchStocks(assetId)
}

// ─── Stock create/edit form ─────────────────────────────────────────────────
const stockDialogVisible = ref(false)
const stockFormMode = ref<'create' | 'edit'>('create')
const stockSubmitting = ref(false)
const stockFormRef = ref<FormInstance>()

interface StockFormState extends StockAssetCreate {}

function emptyStockForm(): StockFormState {
  return {
    stock_id: '',
    stock_code: '',
    stock_name: '',
    asset_id: stocksAssetId.value,
    expected_spend: 0,
  }
}

const stockForm = ref<StockFormState>(emptyStockForm())

const stockFormRules: FormRules = {
  stock_id: [{ required: true, message: '請輸入持有 ID', trigger: 'blur' }],
  stock_code: [{ required: true, message: '請輸入代號', trigger: 'blur' }],
  stock_name: [{ required: true, message: '請輸入名稱', trigger: 'blur' }],
  expected_spend: [{ required: true, message: '請輸入預計投入金額', trigger: 'blur' }],
}

function openCreateStock() {
  stockFormMode.value = 'create'
  stockForm.value = emptyStockForm()
  stockDialogVisible.value = true
}

function openEditStock(row: StockAsset) {
  stockFormMode.value = 'edit'
  stockForm.value = {
    stock_id: row.stock_id,
    stock_code: row.stock_code,
    stock_name: row.stock_name,
    asset_id: row.asset_id,
    expected_spend: row.expected_spend,
  }
  stockDialogVisible.value = true
}

async function submitStock() {
  if (!stockFormRef.value) return
  const valid = await stockFormRef.value.validate().catch(() => false)
  if (!valid) return
  stockSubmitting.value = true
  try {
    if (stockFormMode.value === 'create') {
      await createStock({ ...stockForm.value })
      ElMessage.success('新增成功')
    } else {
      await updateStock(stockForm.value.stock_id, {
        stock_code: stockForm.value.stock_code,
        stock_name: stockForm.value.stock_name,
        asset_id: stockForm.value.asset_id,
        expected_spend: stockForm.value.expected_spend,
      })
      ElMessage.success('更新成功')
    }
    stockDialogVisible.value = false
    if (stocksAssetId.value) await fetchStocks(stocksAssetId.value)
  } finally {
    stockSubmitting.value = false
  }
}

async function handleDeleteStock(row: StockAsset) {
  const ok = await confirm({
    title: '刪除股票持有',
    message: `確定要刪除「${row.stock_name}」(${row.stock_code})?`,
    type: 'warning',
  })
  if (!ok) return
  await deleteStock(row.stock_id)
  ElMessage.success('已刪除')
  stockDetailsByStock.delete(row.stock_id)
  if (stocksAssetId.value) await fetchStocks(stocksAssetId.value)
}

// ─── Stock journal (details) ────────────────────────────────────────────────
const stockDetailsByStock = shallowReactive(new Map<string, StockJournal[]>())
const stockDetailsLoadingByStock = shallowReactive(new Map<string, boolean>())

async function fetchStockDetails(stockId: string) {
  stockDetailsLoadingByStock.set(stockId, true)
  try {
    const details = await getStockDetails(stockId)
    stockDetailsByStock.set(stockId, details)
  } finally {
    stockDetailsLoadingByStock.set(stockId, false)
  }
}

function onStockExpandChange(row: StockAsset, expanded: StockAsset[]) {
  const isExpanded = expanded.some((r) => r.stock_id === row.stock_id)
  if (isExpanded && !stockDetailsByStock.has(row.stock_id)) {
    void fetchStockDetails(row.stock_id)
  }
}

interface StockDetailFormState extends StockJournalCreate {
  distinct_number?: number
}

const stockDetailDialogVisible = ref(false)
const stockDetailFormMode = ref<'create' | 'edit'>('create')
const stockDetailSubmitting = ref(false)
const stockDetailFormRef = ref<FormInstance>()

function emptyStockDetailForm(stockId: string): StockDetailFormState {
  return {
    stock_id: stockId,
    excute_type: 'buy',
    excute_amount: 0,
    excute_price: 0,
    excute_date: dayjs().format('YYYYMMDD'),
    account_id: '',
    account_name: '',
    memo: null,
  }
}

const stockDetailForm = ref<StockDetailFormState>(emptyStockDetailForm(''))

const stockDetailFormDate = computed<Date | null>({
  get: () =>
    stockDetailForm.value.excute_date
      ? dayjs(stockDetailForm.value.excute_date, 'YYYYMMDD').toDate()
      : null,
  set: (date) => {
    stockDetailForm.value.excute_date = date ? dayjs(date).format('YYYYMMDD') : ''
  },
})

const stockDetailFormRules: FormRules = {
  excute_date: [{ required: true, message: '請選擇日期', trigger: 'change' }],
  excute_type: [{ required: true, message: '請選擇類型', trigger: 'change' }],
  excute_amount: [{ required: true, message: '請輸入數量', trigger: 'blur' }],
  excute_price: [{ required: true, message: '請輸入單價', trigger: 'blur' }],
  account_id: [{ required: true, message: '請輸入帳戶 ID', trigger: 'blur' }],
  account_name: [{ required: true, message: '請輸入帳戶名稱', trigger: 'blur' }],
}

function openCreateStockDetail(stock: StockAsset) {
  stockDetailFormMode.value = 'create'
  stockDetailForm.value = emptyStockDetailForm(stock.stock_id)
  stockDetailDialogVisible.value = true
}

function openEditStockDetail(stock: StockAsset, detail: StockJournal) {
  stockDetailFormMode.value = 'edit'
  stockDetailForm.value = {
    distinct_number: detail.distinct_number,
    stock_id: stock.stock_id,
    excute_type: detail.excute_type,
    excute_amount: detail.excute_amount,
    excute_price: detail.excute_price,
    excute_date: detail.excute_date,
    account_id: detail.account_id,
    account_name: detail.account_name,
    memo: detail.memo ?? null,
  }
  stockDetailDialogVisible.value = true
}

async function submitStockDetail() {
  if (!stockDetailFormRef.value) return
  const valid = await stockDetailFormRef.value.validate().catch(() => false)
  if (!valid) return
  stockDetailSubmitting.value = true
  try {
    const payload: StockJournalCreate = {
      stock_id: stockDetailForm.value.stock_id,
      excute_type: stockDetailForm.value.excute_type,
      excute_amount: Number(stockDetailForm.value.excute_amount ?? 0),
      excute_price: Number(stockDetailForm.value.excute_price ?? 0),
      excute_date: stockDetailForm.value.excute_date,
      account_id: stockDetailForm.value.account_id,
      account_name: stockDetailForm.value.account_name,
      memo: stockDetailForm.value.memo || null,
    }
    if (stockDetailFormMode.value === 'create') {
      await createStockDetail(stockDetailForm.value.stock_id, payload)
      ElMessage.success('新增成功')
    } else if (stockDetailForm.value.distinct_number !== undefined) {
      await updateStockDetail(stockDetailForm.value.distinct_number, payload)
      ElMessage.success('更新成功')
    }
    stockDetailDialogVisible.value = false
    await fetchStockDetails(stockDetailForm.value.stock_id)
  } finally {
    stockDetailSubmitting.value = false
  }
}

async function handleDeleteStockDetail(stock: StockAsset, detail: StockJournal) {
  const ok = await confirm({
    title: '刪除股票明細',
    message: `確定要刪除這筆 ${detail.excute_date} ${detail.excute_type} 紀錄?`,
    type: 'warning',
  })
  if (!ok) return
  await deleteStockDetail(detail.distinct_number)
  ElMessage.success('已刪除')
  await fetchStockDetails(stock.stock_id)
}

// ─── Lifecycle ──────────────────────────────────────────────────────────────
onMounted(() => {
  void store.fetchOtherAssets()
})
</script>
