import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import {
  useDashboardStore,
  trailingTwelveMonthsPeriod,
} from '@/stores/dashboard'
import type { DashboardSummary } from '@/types/models'

function makeFreedomSummary(
  points: Array<{ period: string; value: number; income?: number; fixed?: number }>,
): DashboardSummary {
  return {
    type: 'freedom_ratio',
    points: points.map((p) => ({
      period: p.period,
      value: p.value,
      breakdown:
        p.income === undefined && p.fixed === undefined
          ? undefined
          : { income: p.income ?? 0, fixed_expenses: p.fixed ?? 0 },
    })),
  }
}

describe('trailingTwelveMonthsPeriod', () => {
  it('returns YYYYMM-YYYYMM with start 11 months before end', () => {
    const period = trailingTwelveMonthsPeriod(new Date('2026-05-15T12:00:00Z'))
    expect(period).toBe('202506-202605')
  })

  it('handles year wrap', () => {
    const period = trailingTwelveMonthsPeriod(new Date('2026-01-10T12:00:00Z'))
    expect(period).toBe('202502-202601')
  })
})

describe('useDashboardStore — freedomRatioRolling12M', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('returns (sumIncome - sumFixed) / sumIncome over 12 points with breakdown', () => {
    const store = useDashboardStore()
    // 12 months: income=100 each, fixed_expenses=75 each → (1200-900)/1200 = 0.25
    const points = Array.from({ length: 12 }, (_, i) => ({
      period: `20250${i % 9 + 1}`,
      value: 0.25,
      income: 100,
      fixed: 75,
    }))
    store.summaries.freedom_ratio = makeFreedomSummary(points)
    expect(store.freedomRatioRolling12M).toBeCloseTo(0.25, 10)
  })

  it('degrades gracefully when some points lack breakdown', () => {
    const store = useDashboardStore()
    const points = [
      { period: '202504', value: 0 }, // no breakdown
      { period: '202505', value: 0.5, income: 100, fixed: 50 },
      { period: '202506', value: 0.4, income: 100, fixed: 60 },
    ]
    store.summaries.freedom_ratio = makeFreedomSummary(points)
    // sumIncome=200, sumFixed=110 → (200-110)/200 = 0.45
    expect(store.freedomRatioRolling12M).toBeCloseTo(0.45, 10)
  })

  it('returns 0 when total income is 0 (no Infinity / NaN)', () => {
    const store = useDashboardStore()
    const points = [
      { period: '202504', value: 0, income: 0, fixed: 0 },
      { period: '202505', value: 0, income: 0, fixed: 50 },
    ]
    store.summaries.freedom_ratio = makeFreedomSummary(points)
    expect(store.freedomRatioRolling12M).toBe(0)
  })

  it('returns 0 when no freedom_ratio summary loaded', () => {
    const store = useDashboardStore()
    expect(store.freedomRatioRolling12M).toBe(0)
  })
})
