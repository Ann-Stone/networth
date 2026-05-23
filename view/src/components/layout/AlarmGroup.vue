<template>
  <div class="flex flex-col gap-2">
    <p class="text-xs font-bold uppercase tracking-wider" :class="titleColor">
      {{ title }}
      <span class="text-on-surface-variant font-semibold ml-1">({{ alarms.length }})</span>
    </p>
    <ul class="flex flex-col divide-y divide-outline-variant/30 rounded-lg bg-surface-container-low">
      <li
        v-for="(a, idx) in alarms"
        :key="`${a.date}-${idx}`"
        class="flex items-center justify-between px-4 py-3"
      >
        <div class="flex items-center gap-2 min-w-0">
          <span
            class="shrink-0 text-[10px] font-semibold px-1.5 py-0.5 rounded bg-on-surface-variant/10 text-on-surface-variant"
            :title="a.recurrence === 'Y' ? '每年循環' : '每月循環'"
          >
            🔁 {{ a.recurrence === 'Y' ? '每年' : '每月' }}
          </span>
          <p class="text-on-surface text-sm truncate">{{ a.content }}</p>
        </div>
        <div class="flex items-center gap-3 shrink-0">
          <span class="text-on-surface-variant text-xs tabular-nums">{{ a.displayDate }}</span>
          <span
            class="tabular-nums text-xs font-bold px-2 py-0.5 rounded-full"
            :class="chipColor"
          >
            {{ relativeText(a.daysUntil) }}
          </span>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AlarmWithMeta } from '@/stores/alarms'

const props = defineProps<{
  title: string
  tone: 'error' | 'secondary' | 'muted'
  alarms: AlarmWithMeta[]
}>()

const titleColor = computed(() => {
  if (props.tone === 'error') return 'text-error'
  if (props.tone === 'secondary') return 'text-secondary'
  return 'text-on-surface-variant'
})

const chipColor = computed(() => {
  if (props.tone === 'error') return 'bg-error/10 text-error'
  if (props.tone === 'secondary') return 'bg-secondary/10 text-secondary'
  return 'bg-on-surface-variant/10 text-on-surface-variant'
})

function relativeText(days: number): string {
  if (days < 0) return `逾期 ${Math.abs(days)} 天`
  if (days === 0) return '今天'
  if (days === 1) return '明天'
  return `剩 ${days} 天`
}
</script>
