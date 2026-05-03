/**
 * CSS-var–driven chart colour helper.
 * Reads current design-system tokens at call time so the palette
 * automatically adapts when the html.dark / html.light class changes.
 */
export function getChartColors(): string[] {
  const s = getComputedStyle(document.documentElement)
  const v = (name: string) => s.getPropertyValue(name).trim()
  return [
    v('--ds-primary-container'),    // sage (primary accent)
    v('--ds-secondary'),            // dusty rose
    v('--ds-on-surface-variant'),   // muted text tone
    v('--ds-outline'),              // outline / neutral
    v('--ds-primary'),              // light sage
  ]
}
