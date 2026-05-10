import { http } from 'msw'
import { ok, fail } from '../util'
import { _alarmsSnapshot, _budgetsForYear } from './settings'
import type {
  DashboardAlarm,
  DashboardBudget,
  DashboardBudgetLine,
  DashboardGift,
  DashboardSummary,
  TargetSetting,
  TargetSettingCreate,
  TargetSettingUpdate,
} from '@/types/models'

// ─── Targets — in-memory CRUD ────────────────────────────────────────────────

let targets: TargetSetting[] = [
  { distinct_number: 'T1', target_year: '2026', setting_value: 18000000, is_done: 'N' },
  { distinct_number: 'T2', target_year: '2026', setting_value: 1200000,  is_done: 'N' },
  { distinct_number: 'T3', target_year: '2025', setting_value: 15000000, is_done: 'Y' },
]

// ─── Summary points ──────────────────────────────────────────────────────────

function summaryPoints(type: string, period: string): DashboardSummary {
  // period = YYYYMM-YYYYMM
  const [start, end] = period.split('-')
  const startYM = start || '202505'
  const endYM = end || '202604'
  let y = Number(startYM.slice(0, 4))
  let m = Number(startYM.slice(4, 6))
  const endY = Number(endYM.slice(0, 4))
  const endM = Number(endYM.slice(4, 6))
  const points: { period: string; value: number }[] = []
  let base = 13800000
  while (y < endY || (y === endY && m <= endM)) {
    points.push({ period: `${y}${String(m).padStart(2, '0')}`, value: base })
    base += 95000 + Math.round(Math.sin(points.length) * 50000)
    m += 1
    if (m === 13) { m = 1; y += 1 }
  }
  return { type, points }
}

// ─── Budget overview ─────────────────────────────────────────────────────────

function dashboardBudget(type: string, period: string): DashboardBudget {
  const year = period.slice(0, 4)
  const monthIdx = type === 'monthly' ? Number(period.slice(4, 6)) : 0
  const yearBudgets = _budgetsForYear(year)
  const lines: DashboardBudgetLine[] = yearBudgets
    .filter((b) => b.code_type !== 'Income' && b.code_type !== 'Transfer')
    .map((b) => {
      let planned: number
      if (type === 'monthly') {
        const key = `expected${String(monthIdx).padStart(2, '0')}` as keyof typeof b
        planned = Number(b[key]) || 0
      } else {
        planned = (b.expected01 + b.expected02 + b.expected03 + b.expected04 + b.expected05 + b.expected06 + b.expected07 + b.expected08 + b.expected09 + b.expected10 + b.expected11 + b.expected12)
      }
      const actual = Math.round(planned * (0.55 + Math.random() * 0.4))
      return {
        category: b.category_name,
        planned,
        actual,
        usage_pct: planned ? actual / planned : 0,
      }
    })
  const total_planned = lines.reduce((s, l) => s + l.planned, 0)
  const total_actual = lines.reduce((s, l) => s + l.actual, 0)
  return { type, period, lines, total_planned, total_actual }
}

// ─── Gifts ───────────────────────────────────────────────────────────────────

function dashboardGifts(_year: string): DashboardGift[] {
  return [
    { owner: '父',     amount: 60000, rate: 0.5 },
    { owner: '母',     amount: 60000, rate: 0.5 },
    { owner: '配偶',   amount: 30000, rate: 0.25 },
  ]
}

// ─── Alarms ──────────────────────────────────────────────────────────────────

function dashboardAlarms(): DashboardAlarm[] {
  return _alarmsSnapshot().map((a) => ({
    date: `${a.alarm_date.slice(0, 4)}/${a.alarm_date.slice(4, 6)}/${a.alarm_date.slice(6, 8)}`,
    content: a.content,
  }))
}

// ─── Handlers ────────────────────────────────────────────────────────────────

export const dashboardHandlers = [
  http.get('*/dashboard/summary', ({ request }) => {
    const url = new URL(request.url)
    const type = url.searchParams.get('type') ?? 'monthly'
    const period = url.searchParams.get('period') ?? '202505-202604'
    return ok(summaryPoints(type, period))
  }),
  http.get('*/dashboard/alarms', () => ok(dashboardAlarms())),
  http.get('*/dashboard/targets', () => ok(targets)),
  http.post('*/dashboard/targets', async ({ request }) => {
    const body = (await request.json()) as TargetSettingCreate
    const created: TargetSetting = {
      distinct_number: body.distinct_number,
      target_year: body.target_year ?? String(new Date().getFullYear()),
      setting_value: body.setting_value,
      is_done: body.is_done ?? 'N',
    }
    targets.push(created)
    return ok(created)
  }),
  http.put('*/dashboard/targets/:id', async ({ params, request }) => {
    const body = (await request.json()) as TargetSettingUpdate
    const idx = targets.findIndex((t) => t.distinct_number === String(params.id))
    const cur = targets[idx]
    if (!cur) return fail('target not found', 404)
    const next: TargetSetting = { ...cur, ...body }
    targets[idx] = next
    return ok(next)
  }),
  http.delete('*/dashboard/targets/:id', ({ params }) => {
    const before = targets.length
    targets = targets.filter((t) => t.distinct_number !== String(params.id))
    if (targets.length === before) return fail('target not found', 404)
    return ok(null)
  }),
  http.get('*/dashboard/budget', ({ request }) => {
    const url = new URL(request.url)
    const type = url.searchParams.get('type') ?? 'monthly'
    const period = url.searchParams.get('period') ?? '202604'
    return ok(dashboardBudget(type, period))
  }),
  http.get('*/dashboard/gifts/:year', ({ params }) => ok(dashboardGifts(String(params.year)))),
]
