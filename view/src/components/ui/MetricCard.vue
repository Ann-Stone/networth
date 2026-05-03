<template>
  <div
    class="flex flex-col gap-3 rounded-xl p-8 bg-surface-container border border-outline-variant shadow-sm"
  >
    <div class="flex justify-between items-start">
      <p class="text-on-surface-variant text-sm font-semibold uppercase tracking-wider">
        {{ label }}
      </p>
      <el-icon v-if="icon" :class="iconClass">
        <component :is="icon" />
      </el-icon>
    </div>

    <MoneyDisplay
      :amount="amount"
      :currency="currency"
      size="lg"
      class="text-on-surface"
    />

    <div v-if="hasDelta" class="flex items-center gap-1.5 mt-2">
      <TrendBadge
        v-if="deltaPercent !== undefined"
        :value="deltaPercent"
        :tone="badgeTone"
      />
      <span
        v-if="deltaLabel"
        class="text-on-surface-variant text-xs"
      >
        {{ deltaLabel }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, type Component } from 'vue'
import MoneyDisplay from './MoneyDisplay.vue'
import TrendBadge from './TrendBadge.vue'

const props = withDefaults(
  defineProps<{
    label: string
    amount: number
    currency?: string
    deltaPercent?: number
    deltaLabel?: string
    icon?: Component
    tone?: 'primary' | 'rose'
  }>(),
  {
    currency: 'TWD',
    tone: 'primary',
  },
)

const iconClass = computed(() =>
  props.tone === 'rose' ? 'text-secondary' : 'text-primary',
)

const badgeTone = computed<'positive' | 'negative' | 'auto'>(() => {
  if (props.tone === 'rose') return 'negative'
  return 'auto'
})

const hasDelta = computed(
  () => props.deltaPercent !== undefined || !!props.deltaLabel,
)
</script>
