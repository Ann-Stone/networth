<!--
  Insurance journal (premium/claim) detail form fields, shared by:
    1. OtherAssetsView (mode="asset-manage")  — full editor for an existing
       policy's detail row; `insurance_id` displayed as a disabled input above.
    2. CashFlowView    (mode="cashflow-sync") — the journal already supplies
       amount (= spending), date and memo, so this mode hides those rows and
       only asks for the execution type.

  The parent owns the form state object (v-model) and the `insurance_id` picker.
  Mirrors StockDetailFormFields.vue.
-->
<script setup lang="ts">
import { computed } from 'vue'
import dayjs from 'dayjs'

export interface InsuranceDetailFormState {
  distinct_number?: number
  insurance_id: string
  insurance_excute_type: string
  excute_price: number
  excute_date: string
  memo?: string | null
}

const props = defineProps<{
  modelValue: InsuranceDetailFormState
  mode: 'asset-manage' | 'cashflow-sync'
  showInsuranceIdInput?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: InsuranceDetailFormState): void
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
  <el-form-item v-if="showInsuranceIdInput" label="保險 ID">
    <el-input :model-value="form.insurance_id" disabled />
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

  <el-form-item label="類型" prop="insurance_excute_type">
    <el-select v-model="form.insurance_excute_type" style="width: 100%">
      <el-option label="繳費 (pay)" value="pay" />
      <el-option label="現金回饋 (cash)" value="cash" />
      <el-option label="退費 (return)" value="return" />
      <el-option label="預期 (expect)" value="expect" />
    </el-select>
  </el-form-item>

  <el-form-item v-if="!isCashflow" label="金額" prop="excute_price">
    <el-input-number
      v-model="form.excute_price"
      :precision="2"
      :step="100"
      controls-position="right"
      style="width: 100%"
    />
  </el-form-item>
  <p v-else class="text-xs text-on-surface-variant mt-1">
    金額會自動帶入主表單的金額（含正負號）
  </p>

  <el-form-item v-if="!isCashflow" label="備註">
    <el-input
      v-model="form.memo"
      type="textarea"
      :rows="2"
      placeholder="(可選)"
    />
  </el-form-item>
</template>

<script lang="ts">
import type { FormRules } from 'element-plus'

// Validation rules — exported so parents that compose this component into a
// larger form can spread the relevant subset into their own rules object.
export const INSURANCE_DETAIL_FULL_RULES: FormRules = {
  excute_date: [{ required: true, message: '請選擇日期', trigger: 'change' }],
  insurance_excute_type: [{ required: true, message: '請選擇類型', trigger: 'change' }],
  excute_price: [{ required: true, message: '請輸入金額', trigger: 'blur' }],
}

export const INSURANCE_DETAIL_CASHFLOW_RULES: FormRules = {
  insurance_excute_type: [{ required: true, message: '請選擇類型', trigger: 'change' }],
}
</script>
