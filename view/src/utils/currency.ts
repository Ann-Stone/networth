/**
 * Format a number as currency string with thousands separator.
 * @example formatCurrency(1234567.89) → '1,234,567.89'
 */
export function formatCurrency(
  value: number | null | undefined,
  decimals = 0,
): string {
  if (value == null || isNaN(value)) return '—'
  return new Intl.NumberFormat('zh-TW', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value)
}

/**
 * Return 'positive' | 'negative' | 'neutral' class name for money display.
 */
export function moneyClass(value: number): 'text-positive' | 'text-negative' | 'text-neutral' {
  if (value > 0) return 'text-positive'
  if (value < 0) return 'text-negative'
  return 'text-neutral'
}

/**
 * Format percentage, e.g. 0.1234 → '12.34%'
 */
export function formatPercent(value: number, decimals = 2): string {
  return `${(value * 100).toFixed(decimals)}%`
}
