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
          <el-table v-else :data="store.stocks" stripe border style="width: 100%">
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
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
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
import { createStock, deleteStock, updateStock } from '@/api/otherAssets'
import type { StockAsset, StockAssetCreate } from '@/types/models'

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
  if (stocksAssetId.value) await fetchStocks(stocksAssetId.value)
}

// ─── Lifecycle ──────────────────────────────────────────────────────────────
onMounted(() => {
  void store.fetchOtherAssets()
})
</script>
