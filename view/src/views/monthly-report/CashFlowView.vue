<template>
  <div class="flex flex-col gap-8">
    <PageHeader title="月度現金流" :subtitle="store.selectedMonth">
      <template #actions>
        <el-date-picker
          v-model="selectedMonthDate"
          type="month"
          placeholder="選擇月份"
          format="YYYY/MM"
          :clearable="false"
        />
      </template>
    </PageHeader>

    <section class="flex flex-col gap-4">
      <SectionHeader title="日記帳" />
      <el-skeleton v-if="store.journalsLoading" :rows="5" animated />
      <EmptyState v-else-if="store.journals.length === 0" message="本月尚無日記帳資料" />
      <template v-else>
        <el-table :data="store.journals" stripe border style="width: 100%">
          <el-table-column prop="spend_date" label="日期" width="110" />
          <el-table-column prop="spend_way" label="帳戶" min-width="140" />
          <el-table-column prop="action_main_type" label="類別" width="120" />
          <el-table-column prop="action_sub_type" label="子類" width="120">
            <template #default="{ row }">
              <span>{{ row.action_sub_type ?? '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="金額" width="180" align="right">
            <template #default="{ row }">
              <MoneyDisplay
                :amount="row.spending"
                :positive="row.spending > 0 ? true : row.spending < 0 ? false : null"
                size="sm"
              />
            </template>
          </el-table-column>
          <el-table-column prop="note" label="備註" min-width="160">
            <template #default="{ row }">
              <span>{{ row.note ?? '' }}</span>
            </template>
          </el-table-column>
        </el-table>

        <div
          class="grid grid-cols-1 md:grid-cols-3 gap-4 rounded-xl border border-slate-200 dark:border-primary/5 bg-white dark:bg-surface-dark p-6"
        >
          <div class="flex flex-col gap-1">
            <p class="text-slate-500 dark:text-muted-text text-xs uppercase tracking-wider">本月收入</p>
            <MoneyDisplay :amount="totalIncome" :positive="true" size="lg" />
          </div>
          <div class="flex flex-col gap-1">
            <p class="text-slate-500 dark:text-muted-text text-xs uppercase tracking-wider">本月支出</p>
            <MoneyDisplay :amount="totalExpense" :positive="false" size="lg" />
          </div>
          <div class="flex flex-col gap-1">
            <p class="text-slate-500 dark:text-muted-text text-xs uppercase tracking-wider">本月淨額</p>
            <MoneyDisplay
              :amount="netTotal"
              :positive="netTotal > 0 ? true : netTotal < 0 ? false : null"
              size="lg"
            />
          </div>
        </div>
      </template>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import dayjs from 'dayjs'
import PageHeader from '@/components/ui/PageHeader.vue'
import SectionHeader from '@/components/ui/SectionHeader.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import { useCashFlowStore } from '@/stores/cashFlow'

const store = useCashFlowStore()

const selectedMonthDate = ref<Date>(dayjs(store.selectedMonth, 'YYYYMM').toDate())

watch(selectedMonthDate, (date) => {
  if (!date) return
  const next = dayjs(date).format('YYYYMM')
  if (next === store.selectedMonth) return
  store.selectedMonth = next
  store.fetchJournals()
})

const totalIncome = computed(() =>
  store.journals
    .filter((j) => j.spending > 0)
    .reduce((sum, j) => sum + j.spending, 0),
)

const totalExpense = computed(() =>
  store.journals
    .filter((j) => j.spending < 0)
    .reduce((sum, j) => sum + j.spending, 0),
)

const netTotal = computed(() => totalIncome.value + totalExpense.value)

onMounted(() => {
  store.fetchJournals()
})
</script>
