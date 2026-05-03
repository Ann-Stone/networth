<template>
  <div class="bg-surface-container rounded-xl border border-outline-variant overflow-hidden">
    <div
      class="px-6 py-4 border-b border-outline-variant/30 bg-surface-container-low flex justify-between items-center"
    >
      <p class="text-sm font-bold text-on-surface">{{ title }}</p>
      <slot name="menu" />
    </div>
    <div class="divide-y divide-outline-variant/20">
      <slot />
    </div>
    <div
      v-if="$slots.footer"
      class="p-4 bg-surface-container-low text-center"
    >
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string }>()
</script>
