<!--
  Stock transaction detail form fields, shared by:
    1. OtherAssetsView (mode="asset-manage")  — full editor for an existing
       holding; `stock_id` displayed as a disabled input above the fields.
    2. CashFlowView    (mode="cashflow-sync") — the journal already supplies
       price (= spending), settling account (= spend_way), date and memo, so
       this mode hides those rows and only asks for type + share count.

  The parent owns the form state object (v-model) and the `stock_id` picker.
-->
<script setup lang="ts">
import { computed } from 'vue'
import dayjs from 'dayjs'

export interface StockDetailFormState {
  distinct_number?: number
  stock_id: string
  excute_type: string
  excute_amount: number
  excute_price: number
  excute_date: string
  account_id: string
  account_name: string
  memo?: string | null
}

const props = defineProps<{
  modelValue: StockDetailFormState
  mode: 'asset-manage' | 'cashflow-sync'
  showStockIdInput?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: StockDetailFormState): void
}>()

const form = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

const formDate = computed<Date | null>({
  get: () =>
    form.value.excute_date
      ? dayjs(form.value.excute_date, 'YYYYMMDD').toDate()
      : null,
  set: (date) => {
    form.value = {
      ...form.value,
      excute_date: date ? dayjs(date).format('YYYYMMDD') : '',
    }
  },
})

const isCashflow = computed(() => props.mode === 'cashflow-sync')
</script>

<template>
  <el-form-item v-if="showStockIdInput" label="持有 ID">
    <el-input :model-value="form.stock_id" disabled />
  </el-form-item>

  <el-form-item v-if="!isCashflow" label="日期" prop="excute_date">
    <el-date-picker
      v-model="formDate"
      type="date"
      format="YYYY/MM/DD"
      :clearable="false"
      style="width: 100%"
    />
  </el-form-item>

  <el-form-item label="類型" prop="excute_type">
    <el-select v-model="form.excute_type" style="width: 100%">
      <el-option label="買入 (buy)" value="buy" />
      <el-option label="賣出 (sell)" value="sell" />
      <el-option label="股票股利 (stock)" value="stock" />
      <el-option label="現金股利 (cash)" value="cash" />
    </el-select>
  </el-form-item>

  <el-form-item label="數量" prop="excute_amount">
    <el-input-number
      v-model="form.excute_amount"
      :precision="2"
      :step="1"
      controls-position="right"
      style="width: 100%"
    />
    <p v-if="isCashflow" class="text-xs text-on-surface-variant mt-1">
      現金股息可留 0；單價會自動帶入主表單的金額（含正負號）
    </p>
  </el-form-item>

  <el-form-item v-if="!isCashflow" label="單價" prop="excute_price">
    <el-input-number
      v-model="form.excute_price"
      :precision="2"
      :step="1"
      controls-position="right"
      style="width: 100%"
    />
  </el-form-item>

  <template v-if="!isCashflow">
    <el-form-item label="帳戶 ID" prop="account_id">
      <el-input v-model="form.account_id" placeholder="例如 BANK-CHASE-01" />
    </el-form-item>
    <el-form-item label="帳戶名稱" prop="account_name">
      <el-input v-model="form.account_name" placeholder="例如 Chase Checking" />
    </el-form-item>
    <el-form-item label="備註">
      <el-input
        v-model="form.memo"
        type="textarea"
        :rows="2"
        placeholder="(可選)"
      />
    </el-form-item>
  </template>
</template>

<script lang="ts">
import type { FormRules } from 'element-plus'

// Validation rules — exported so parents that compose this component into a
// larger form can spread the relevant subset into their own rules object.
export const STOCK_DETAIL_FULL_RULES: FormRules = {
  excute_date: [{ required: true, message: '請選擇日期', trigger: 'change' }],
  excute_type: [{ required: true, message: '請選擇類型', trigger: 'change' }],
  excute_amount: [{ required: true, message: '請輸入數量', trigger: 'blur' }],
  excute_price: [{ required: true, message: '請輸入單價', trigger: 'blur' }],
  account_id: [{ required: true, message: '請輸入帳戶 ID', trigger: 'blur' }],
  account_name: [{ required: true, message: '請輸入帳戶名稱', trigger: 'blur' }],
}

export const STOCK_DETAIL_CASHFLOW_RULES: FormRules = {
  excute_type: [{ required: true, message: '請選擇類型', trigger: 'change' }],
}
</script>
