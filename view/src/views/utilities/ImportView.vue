<template>
  <div class="flex flex-col gap-6">
    <PageHeader title="資料匯入" subtitle="批次匯入股價、匯率與發票" />

    <DataListCard title="股價匯入">
      <div class="p-6 flex flex-col gap-3">
        <p class="text-sm text-on-surface-variant">
          透過 yfinance 抓取股票交易紀錄中所有 ticker 的指定期間日線價格，寫入 Stock_Price_History。
        </p>
        <div class="flex flex-wrap items-center gap-3">
          <el-date-picker
            v-model="stockPeriod"
            type="month"
            value-format="YYYYMM"
            placeholder="留白表示今日"
            style="width: 200px"
          />
          <el-button
            type="primary"
            :loading="stockLoading"
            @click="handleStockPriceImport"
          >
            匯入股價
          </el-button>
        </div>
        <p class="text-xs text-on-surface-muted">
          留白表示今日；填入 YYYYMM 抓該月最後一個交易日的價格。
        </p>
      </div>
    </DataListCard>

    <DataListCard title="匯率匯入">
      <div class="p-6 flex flex-col gap-3">
        <p class="text-sm text-on-surface-variant">
          從永豐銀行抓取指定期間的外幣買入匯率，upsert 至 FX_Rate。
        </p>
        <div class="flex flex-wrap items-center gap-3">
          <el-date-picker
            v-model="fxPeriod"
            type="month"
            value-format="YYYYMM"
            placeholder="留白表示今日"
            style="width: 200px"
          />
          <el-button
            type="primary"
            :loading="fxLoading"
            @click="handleFxRateImport"
          >
            匯入匯率
          </el-button>
        </div>
        <p class="text-xs text-on-surface-muted">
          留白表示今日；填入 YYYYMM 抓該月最後一日的匯率。
        </p>
      </div>
    </DataListCard>

    <DataListCard title="發票匯入">
      <div v-loading="invoiceLoading" class="p-6 flex flex-col gap-3">
        <p class="text-sm text-on-surface-variant">
          上傳財政部電子發票平台匯出的 CSV（pipe 分隔），系統會解析、去重後寫入 Journal，並回報匯入結果。
        </p>
        <div class="flex flex-wrap items-center gap-3">
          <el-upload
            ref="invoiceUploadRef"
            class="shrink-0"
            :auto-upload="false"
            :limit="1"
            accept=".csv"
            :on-change="handleInvoiceChange"
            :on-remove="handleInvoiceRemove"
            :on-exceed="handleInvoiceExceed"
          >
            <template #trigger>
              <el-button>選擇 CSV 檔</el-button>
            </template>
          </el-upload>
          <el-button
            type="primary"
            :loading="invoiceLoading"
            :disabled="!invoiceFile"
            @click="handleInvoiceImport"
          >
            匯入發票
          </el-button>
        </div>
        <div v-if="invoiceResult" class="flex flex-col gap-1">
          <p class="text-xs text-on-surface-muted">
            最近一次：匯入 {{ invoiceResult.imported }} 筆 · 略過
            {{ invoiceResult.skipped }} 筆 · 失敗 {{ invoiceResult.failed }} 筆
          </p>
          <ul
            v-if="invoiceResult.months.length"
            class="flex flex-col gap-0.5 text-xs text-on-surface-muted"
          >
            <li v-for="m in invoiceResult.months" :key="m.month">
              {{ formatMonth(m.month) }}：匯入 {{ m.imported }} 筆<span v-if="m.skipped">
                · 略過 {{ m.skipped }} 筆</span>
            </li>
          </ul>
        </div>
        <p v-else class="text-xs text-on-surface-muted">
          僅接受 CSV 檔；選擇檔案後按「匯入發票」即可。
        </p>
      </div>
    </DataListCard>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, genFileId } from 'element-plus'
import type { UploadInstance, UploadProps, UploadRawFile } from 'element-plus'
import PageHeader from '@/components/ui/PageHeader.vue'
import DataListCard from '@/components/ui/DataListCard.vue'
import {
  importStockPrices,
  importFxRates,
  importInvoices,
} from '@/api/utilities'
import type { InvoiceImportResult } from '@/types/models'

const stockPeriod = ref<string>('')
const fxPeriod = ref<string>('')

const stockLoading = ref(false)
const fxLoading = ref(false)
const invoiceLoading = ref(false)

const invoiceUploadRef = ref<UploadInstance>()
const invoiceFile = ref<File | null>(null)
const invoiceResult = ref<InvoiceImportResult | null>(null)

// 202603 → 2026/03; leave anything unexpected untouched.
function formatMonth(yyyymm: string): string {
  if (yyyymm.length !== 6) return yyyymm
  return `${yyyymm.slice(0, 4)}/${yyyymm.slice(4, 6)}`
}

async function handleStockPriceImport() {
  stockLoading.value = true
  try {
    const res = await importStockPrices(stockPeriod.value)
    ElMessage.success(res.message || '股價匯入已排程')
  } catch {
    ElMessage.error('股價匯入失敗')
  } finally {
    stockLoading.value = false
  }
}

async function handleFxRateImport() {
  fxLoading.value = true
  try {
    const res = await importFxRates(fxPeriod.value)
    ElMessage.success(res.message || '匯率匯入已排程')
  } catch {
    ElMessage.error('匯率匯入失敗')
  } finally {
    fxLoading.value = false
  }
}

const handleInvoiceChange: UploadProps['onChange'] = (uploadFile) => {
  invoiceFile.value = uploadFile.raw ?? null
  invoiceResult.value = null
}

const handleInvoiceRemove: UploadProps['onRemove'] = () => {
  invoiceFile.value = null
}

// el-upload is capped at one file; picking another replaces the current one.
const handleInvoiceExceed: UploadProps['onExceed'] = (files) => {
  invoiceUploadRef.value?.clearFiles()
  const file = files[0] as UploadRawFile
  file.uid = genFileId()
  invoiceUploadRef.value?.handleStart(file)
  invoiceFile.value = file
  invoiceResult.value = null
}

async function handleInvoiceImport() {
  if (!invoiceFile.value) {
    ElMessage.warning('請先選擇要匯入的 CSV 檔')
    return
  }
  invoiceLoading.value = true
  try {
    const res = await importInvoices(invoiceFile.value)
    invoiceResult.value = res
    const msg = `匯入 ${res.imported} 筆，略過 ${res.skipped} 筆，失敗 ${res.failed} 筆`
    if (res.failed > 0) ElMessage.warning(msg)
    else ElMessage.success(msg)
    invoiceUploadRef.value?.clearFiles()
    invoiceFile.value = null
  } catch {
    ElMessage.error('發票匯入失敗')
  } finally {
    invoiceLoading.value = false
  }
}
</script>
