<template>
  <span class="tabular-nums" :class="[colorClass, sizeClass]">
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
    size?: 'sm' | 'md' | 'lg'
  }>(),
  {
    currency: 'TWD',
    positive: null,
    size: 'md',
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

const sizeClass = computed(() => {
  if (props.size === 'sm') return 'text-sm'
  if (props.size === 'lg') return 'text-3xl font-bold'
  return 'text-base'
})
</script>
