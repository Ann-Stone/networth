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
      <div class="p-6 flex flex-col gap-3">
        <p class="text-sm text-on-surface-variant">
          解析財政部電子發票管道兜售平台 CSV，去重後寫入 Journal。背景任務處理。
        </p>
        <div class="flex flex-wrap items-center gap-3">
          <el-date-picker
            v-model="invoicePeriod"
            type="month"
            value-format="YYYYMM"
            placeholder="留白表示今日"
            style="width: 200px"
          />
          <el-button
            type="primary"
            :loading="invoiceLoading"
            @click="handleInvoiceImport"
          >
            匯入發票
          </el-button>
        </div>
        <p class="text-xs text-on-surface-muted">
          需先將 invoice CSV 放至 api 端設定的匯入目錄；留白表示今日。
        </p>
      </div>
    </DataListCard>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/ui/PageHeader.vue'
import DataListCard from '@/components/ui/DataListCard.vue'
import {
  importStockPrices,
  importFxRates,
  importInvoices,
} from '@/api/utilities'

const stockPeriod = ref<string>('')
const fxPeriod = ref<string>('')
const invoicePeriod = ref<string>('')

const stockLoading = ref(false)
const fxLoading = ref(false)
const invoiceLoading = ref(false)

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

async function handleInvoiceImport() {
  invoiceLoading.value = true
  try {
    const res = await importInvoices(invoicePeriod.value)
    ElMessage.success(res.message || '發票匯入已排程')
  } catch {
    ElMessage.error('發票匯入失敗')
  } finally {
    invoiceLoading.value = false
  }
}
</script>
