<template>
  <span class="tabular-nums" :class="colorClass">
    {{ formatted }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    amount: number
    currency?: string
    positive?: boolean | null
  }>(),
  {
    currency: 'TWD',
    positive: null,
  },
)

const formatted = computed(() => {
  const value = Number(props.amount ?? 0)
  if (Number.isNaN(value)) return '-'
  const sign = value < 0 ? '-' : ''
  const abs = Math.abs(value)
  const formattedNumber = new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(abs)
  return `${sign}${props.currency} ${formattedNumber}`
})

const colorClass = computed(() => {
  if (props.positive === true) return 'text-positive'
  if (props.positive === false) return 'text-negative'
  return 'text-neutral'
})
</script>
