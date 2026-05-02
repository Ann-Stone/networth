<template>
  <div class="bg-white dark:bg-surface-dark rounded-xl border border-slate-200 dark:border-primary/5 overflow-hidden">
    <div
      class="px-6 py-4 border-b border-slate-100 dark:border-background-dark/50 bg-slate-50 dark:bg-background-dark/20 flex justify-between items-center"
    >
      <p class="text-sm font-bold text-slate-800 dark:text-cream">{{ title }}</p>
      <slot name="menu" />
    </div>
    <div class="divide-y divide-slate-100 dark:divide-background-dark/50">
      <slot />
    </div>
    <div
      v-if="$slots.footer"
      class="p-4 bg-slate-50 dark:bg-background-dark/20 text-center"
    >
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string }>()
</script>
