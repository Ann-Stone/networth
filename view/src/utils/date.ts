import dayjs from 'dayjs'

/** YYYYMM → 'YYYY年MM月' */
export function formatYearMonth(yyyymm: string): string {
  return dayjs(yyyymm, 'YYYYMM').format('YYYY年MM月')
}

/** YYYY-MM-DD → 'YYYY/MM/DD' */
export function formatDate(dateStr: string): string {
  return dayjs(dateStr).format('YYYY/MM/DD')
}

/** Get current YYYYMM string */
export function currentYearMonth(): string {
  return dayjs().format('YYYYMM')
}

/** Get current YYYY string */
export function currentYear(): string {
  return dayjs().format('YYYY')
}

/** Generate list of last N months as YYYYMM strings */
export function lastNMonths(n: number): string[] {
  return Array.from({ length: n }, (_, i) =>
    dayjs().subtract(i, 'month').format('YYYYMM'),
  ).reverse()
}
