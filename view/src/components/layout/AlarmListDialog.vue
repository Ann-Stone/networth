<template>
  <el-dialog
    :model-value="modelValue"
    title="近期提醒"
    width="520"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <el-empty v-if="store.decorated.length === 0" description="近半年沒有待辦提醒" />
    <div v-else class="flex flex-col gap-5">
      <AlarmGroup
        v-if="store.grouped.this_week.length"
        title="⚠ 7 天內"
        tone="error"
        :alarms="store.grouped.this_week"
      />
      <AlarmGroup
        v-if="store.grouped.this_month.length"
        title="本月內"
        tone="secondary"
        :alarms="store.grouped.this_month"
      />
      <AlarmGroup
        v-if="store.grouped.later.length"
        title="未來"
        tone="muted"
        :alarms="store.grouped.later"
      />
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { useAlarmStore } from '@/stores/alarms'
import AlarmGroup from './AlarmGroup.vue'

defineProps<{ modelValue: boolean }>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()

const store = useAlarmStore()
</script>
