"""Dashboard domain service functions (BE-026..BE-028)."""
from __future__ import annotations

import re
from datetime import datetime

from dateutil.relativedelta import relativedelta
from fastapi import HTTPException
from sqlalchemy import text
from sqlmodel import Session, select

from app.models.dashboard.alarm_view import AlarmItem
from app.models.dashboard.budget import BudgetLine, BudgetRead, BudgetType
from app.models.dashboard.gift_view import GiftItem
from app.models.dashboard.summary import SummaryPoint, SummaryRead, SummaryType
from app.models.dashboard.target_setting import (
    TargetSetting,
    TargetSettingCreate,
    TargetSettingUpdate,
)
from app.models.monthly_report.account_balance import AccountBalance
from app.models.monthly_report.credit_card_balance import CreditCardBalance
from app.models.monthly_report.estate_net_value_history import EstateNetValueHistory
from app.models.monthly_report.insurance_net_value_history import (
    InsuranceNetValueHistory,
)
from app.models.monthly_report.journal import Journal
from app.models.monthly_report.loan_balance import LoanBalance
from app.models.monthly_report.stock_net_value_history import StockNetValueHistory
from app.models.settings.alarm import Alarm
from app.models.settings.budget import Budget
from app.models.settings.code_data import CodeData

EXPENSE_TYPES = ("Floating", "Fixed")
GIFT_THRESHOLD = 2_200_000


# ---------- Period helpers ----------


def parse_summary_period(period: str) -> tuple[str, str]:
    if not isinstance(period, str) or not re.fullmatch(r"\d{6}-\d{6}", period):
        raise HTTPException(status_code=422, detail="period must be YYYYMM-YYYYMM")
    start, end = period.split("-")
    if start > end:
        raise HTTPException(status_code=422, detail="period start must precede end")
    return start, end


def _iter_months(start: str, end: str) -> list[str]:
    months: list[str] = []
    cur_year, cur_month = int(start[:4]), int(start[4:])
    end_year, end_month = int(end[:4]), int(end[4:])
    while (cur_year, cur_month) <= (end_year, end_month):
        months.append(f"{cur_year:04d}{cur_month:02d}")
        cur_month += 1
        if cur_month > 12:
            cur_month = 1
            cur_year += 1
    return months


# ---------- Summary services ----------


def get_spending_summary(session: Session, period: str) -> SummaryRead:
    start, end = parse_summary_period(period)
    months = _iter_months(start, end)
    rows = list(
        session.exec(
            select(Journal)
            .where(Journal.vesting_month >= start)
            .where(Journal.vesting_month <= end)
            .where(Journal.action_main_type.in_(EXPENSE_TYPES))
        ).all()
    )
    sums = {m: 0.0 for m in months}
    for j in rows:
        if j.vesting_month in sums:
            sums[j.vesting_month] += abs(j.spending)
    return SummaryRead(
        type=SummaryType.spending,
        points=[SummaryPoint(period=m, value=round(sums[m], 2)) for m in months],
    )


def get_freedom_ratio_summary(session: Session, period: str) -> SummaryRead:
    start, end = parse_summary_period(period)
    months = _iter_months(start, end)
    fixed_codes = {
        c.code_id
        for c in session.exec(select(CodeData).where(CodeData.code_type == "Fixed")).all()
    }
    rows = list(
        session.exec(
            select(Journal)
            .where(Journal.vesting_month >= start)
            .where(Journal.vesting_month <= end)
        ).all()
    )
    income = {m: 0.0 for m in months}
    fixed = {m: 0.0 for m in months}
    for j in rows:
        if j.vesting_month not in income:
            continue
        if j.action_main_type in ("Income", "Passive"):
            income[j.vesting_month] += abs(j.spending)
        if j.action_main in fixed_codes:
            fixed[j.vesting_month] += abs(j.spending)
    points: list[SummaryPoint] = []
    for m in months:
        ratio = (income[m] - fixed[m]) / income[m] if income[m] > 0 else 0.0
        breakdown = {
            "income": round(income[m], 2),
            "fixed_expenses": round(fixed[m], 2),
        }
        points.append(
            SummaryPoint(period=m, value=round(ratio, 4), breakdown=breakdown)
        )
    return SummaryRead(type=SummaryType.freedom_ratio, points=points)


def get_work_freedom_ratio_summary(session: Session, period: str) -> SummaryRead:
    start, end = parse_summary_period(period)
    months = _iter_months(start, end)
    rows = list(
        session.exec(
            select(Journal)
            .where(Journal.vesting_month >= start)
            .where(Journal.vesting_month <= end)
        ).all()
    )
    passive = {m: 0.0 for m in months}
    active = {m: 0.0 for m in months}
    for j in rows:
        if j.vesting_month not in passive:
            continue
        if j.action_main_type == "Passive":
            passive[j.vesting_month] += abs(j.spending)
        elif j.action_main_type == "Income":
            active[j.vesting_month] += abs(j.spending)
    points: list[SummaryPoint] = []
    for m in months:
        total = passive[m] + active[m]
        ratio = passive[m] / total if total > 0 else 0.0
        breakdown = {
            "passive": round(passive[m], 2),
            "active": round(active[m], 2),
        }
        points.append(
            SummaryPoint(period=m, value=round(ratio, 4), breakdown=breakdown)
        )
    return SummaryRead(type=SummaryType.work_freedom_ratio, points=points)


def _latest_per_entity_at(rows, vesting_month: str, key):
    """Latest snapshot per entity whose vesting_month <= vesting_month."""
    latest: dict[str, object] = {}
    for r in rows:
        if r.vesting_month > vesting_month:
            continue
        k = key(r)
        if k not in latest or r.vesting_month > latest[k].vesting_month:
            latest[k] = r
    return list(latest.values())


def get_asset_debt_trend(session: Session, period: str) -> SummaryRead:
    start, end = parse_summary_period(period)
    months = _iter_months(start, end)

    accounts = list(session.exec(select(AccountBalance)).all())
    stocks = list(session.exec(select(StockNetValueHistory)).all())
    estates = list(session.exec(select(EstateNetValueHistory)).all())
    insurances = list(session.exec(select(InsuranceNetValueHistory)).all())
    loans = list(session.exec(select(LoanBalance)).all())
    cards = list(session.exec(select(CreditCardBalance)).all())

    points: list[SummaryPoint] = []
    for m in months:
        a_total = sum(
            r.balance * r.fx_rate
            for r in _latest_per_entity_at(accounts, m, key=lambda r: r.id)
            if r.is_calculate == "Y"
        )
        s_total = sum(
            r.price * r.fx_rate for r in _latest_per_entity_at(stocks, m, key=lambda r: r.id)
        )
        e_total = sum(
            r.market_value for r in _latest_per_entity_at(estates, m, key=lambda r: r.id)
        )
        i_total = sum(
            r.surrender_value * r.fx_rate
            for r in _latest_per_entity_at(insurances, m, key=lambda r: r.id)
        )
        l_total = sum(
            r.balance for r in _latest_per_entity_at(loans, m, key=lambda r: r.id)
        )
        c_total = sum(
            r.balance * r.fx_rate
            for r in _latest_per_entity_at(cards, m, key=lambda r: r.id)
        )
        # liabilities are negative balances; net = assets + liabilities
        value = a_total + s_total + e_total + i_total + l_total + c_total
        breakdown = {
            "accounts": round(a_total, 2),
            "stocks": round(s_total, 2),
            "estates": round(e_total, 2),
            "insurances": round(i_total, 2),
            "loans": round(l_total, 2),
            "cards": round(c_total, 2),
        }
        points.append(
            SummaryPoint(period=m, value=round(value, 2), breakdown=breakdown)
        )
    return SummaryRead(type=SummaryType.asset_debt_trend, points=points)


def get_summary(session: Session, type: SummaryType, period: str) -> SummaryRead:
    parse_summary_period(period)
    if type == SummaryType.spending:
        return get_spending_summary(session, period)
    if type == SummaryType.freedom_ratio:
        return get_freedom_ratio_summary(session, period)
    if type == SummaryType.asset_debt_trend:
        return get_asset_debt_trend(session, period)
    if type == SummaryType.work_freedom_ratio:
        return get_work_freedom_ratio_summary(session, period)
    raise HTTPException(status_code=422, detail=f"Unknown summary type: {type}")


# ---------- Budget service ----------


def get_budget_usage(session: Session, type: BudgetType, period: str) -> BudgetRead:
    if type == BudgetType.monthly:
        if not re.fullmatch(r"\d{6}", period):
            raise HTTPException(status_code=422, detail="period must be YYYYMM for monthly")
        year = period[:4]
        mm = period[4:]
        budget_field = f"expected{mm}"
        journal_filter = Journal.vesting_month == period
    else:
        if not re.fullmatch(r"\d{4}", period):
            raise HTTPException(status_code=422, detail="period must be YYYY for yearly")
        year = period
        budget_field = None
        journal_filter = (Journal.vesting_month >= f"{year}01") & (
            Journal.vesting_month <= f"{year}12"
        )

    budget_rows = list(session.exec(select(Budget).where(Budget.budget_year == year)).all())
    planned_by_cat: dict[str, float] = {}
    name_by_cat: dict[str, str] = {}
    for b in budget_rows:
        if budget_field is not None:
            planned_by_cat[b.category_code] = float(getattr(b, budget_field) or 0.0)
        else:
            planned_by_cat[b.category_code] = sum(
                float(getattr(b, f"expected{m:02d}") or 0.0) for m in range(1, 13)
            )
        name_by_cat[b.category_code] = b.category_name or b.category_code

    journals = list(session.exec(select(Journal).where(journal_filter)).all())
    actual_by_cat: dict[str, float] = {}
    for j in journals:
        actual_by_cat[j.action_main] = actual_by_cat.get(j.action_main, 0.0) + abs(j.spending)

    categories = sorted(set(planned_by_cat) | set(actual_by_cat))
    lines: list[BudgetLine] = []
    for cat in categories:
        planned = planned_by_cat.get(cat, 0.0)
        actual = actual_by_cat.get(cat, 0.0)
        usage = round(actual * 100 / planned, 2) if planned else 0.0
        lines.append(
            BudgetLine(
                category=name_by_cat.get(cat, cat),
                planned=round(planned, 2),
                actual=round(actual, 2),
                usage_pct=usage,
            )
        )
    return BudgetRead(
        type=type,
        period=period,
        lines=lines,
        total_planned=round(sum(l.planned for l in lines), 2),
        total_actual=round(sum(l.actual for l in lines), 2),
    )


# ---------- Target settings (BE-027) ----------


def list_targets(session: Session) -> list[TargetSetting]:
    return list(
        session.exec(
            select(TargetSetting).order_by(
                TargetSetting.target_year.desc(), TargetSetting.distinct_number.asc()
            )
        ).all()
    )


def create_target(session: Session, payload: TargetSettingCreate) -> TargetSetting:
    data = payload.model_dump()
    if not data.get("target_year"):
        data["target_year"] = datetime.now().strftime("%Y")
    if not data.get("is_done"):
        data["is_done"] = "N"
    data["distinct_number"] = _next_target_serial(session)
    row = TargetSetting(**data)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def _next_target_serial(session: Session) -> str:
    """Return the next sequential serial (str) for TargetSetting.distinct_number.

    Legacy rows whose distinct_number is non-numeric are ignored when computing
    the max — they keep their string IDs but new rows always get an integer.
    """
    existing = session.exec(select(TargetSetting.distinct_number)).all()
    max_seen = 0
    for v in existing:
        if isinstance(v, str) and v.isdigit():
            max_seen = max(max_seen, int(v))
    return str(max_seen + 1)


def update_target(
    session: Session, target_id: str, payload: TargetSettingUpdate
) -> TargetSetting:
    row = session.get(TargetSetting, target_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Target not found: {target_id}")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def delete_target(session: Session, target_id: str) -> None:
    row = session.get(TargetSetting, target_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Target not found: {target_id}")
    session.delete(row)
    session.commit()


# ---------- Alarms (BE-028) ----------


def get_upcoming_alarms(
    session: Session, now: datetime | None = None
) -> list[AlarmItem]:
    """Expand recurring alarms into concrete occurrences within a 6-month horizon.

    Y alarms: `alarm_date` is MMDD → one occurrence per calendar year falling
    in [today, today + 6 months]. M alarms: `alarm_date` is DD → one occurrence
    per month in that same window. Past dates within the current month are
    included so the user still sees recently-passed reminders for review.
    """
    now = now or datetime.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    horizon_dt = today + relativedelta(months=6)
    window_start_yyyymm = today.strftime("%Y%m")

    alarms = list(session.exec(select(Alarm)).all())
    items: list[AlarmItem] = []
    for a in alarms:
        for occ in _expand_alarm(a, today, horizon_dt, window_start_yyyymm):
            items.append(occ)

    items.sort(key=lambda it: it.date)
    return items


def _expand_alarm(
    a: Alarm,
    today: datetime,
    horizon_dt: datetime,
    window_start_yyyymm: str,
) -> list[AlarmItem]:
    """Yield AlarmItem occurrences for one Alarm row inside the horizon window."""
    items: list[AlarmItem] = []

    if a.alarm_type == "M":
        if len(a.alarm_date) != 2 or not a.alarm_date.isdigit():
            return items
        dd = int(a.alarm_date)
        year, month = today.year, today.month
        for _ in range(7):  # cover current month + up to 6 forward
            yyyymm = f"{year:04d}{month:02d}"
            if yyyymm > horizon_dt.strftime("%Y%m"):
                break
            if a.due_date and yyyymm > a.due_date[:6]:
                break
            occ_dd = _clamp_day(year, month, dd)
            yyyymmdd = f"{yyyymm}{occ_dd:02d}"
            if yyyymm >= window_start_yyyymm:
                items.append(
                    AlarmItem(date=yyyymmdd, content=a.content, alarm_type="M")
                )
            month += 1
            if month > 12:
                month = 1
                year += 1
        return items

    if a.alarm_type == "Y":
        if len(a.alarm_date) != 4 or not a.alarm_date.isdigit():
            return items
        mm = int(a.alarm_date[:2])
        dd = int(a.alarm_date[2:])
        # Yearly: include this year's anchor and possibly next year's if the
        # 6-month horizon spans Dec→Jan.
        for year in (today.year, today.year + 1):
            occ_dd = _clamp_day(year, mm, dd)
            occ = datetime(year, mm, occ_dd)
            yyyymm = occ.strftime("%Y%m")
            if a.due_date and yyyymm > a.due_date[:6]:
                continue
            if occ.replace(day=1) > horizon_dt.replace(day=1):
                continue
            if yyyymm < window_start_yyyymm:
                continue
            items.append(
                AlarmItem(date=occ.strftime("%Y%m%d"), content=a.content, alarm_type="Y")
            )
        return items

    return items


def _clamp_day(year: int, month: int, day: int) -> int:
    """Cap day at last valid day of month (e.g. Feb 30 → Feb 28/29)."""
    next_month_first = datetime(year + (1 if month == 12 else 0), 1 if month == 12 else month + 1, 1)
    last_day = (next_month_first - relativedelta(days=1)).day
    return min(day, last_day)


# ---------- Gifts (BE-028) ----------


_GIFT_SQL = text(
    """
    SELECT af.owner AS owner,
           SUM(ABS(j.spending) * COALESCE(fx.buy_rate, 1)) AS amount
    FROM Journal j
    JOIN Account af
      ON af.account_id = CASE WHEN j.spending < 0 THEN j.spend_way ELSE j.action_sub END
    JOIN Account at_
      ON at_.account_id = CASE WHEN j.spending < 0 THEN j.action_sub ELSE j.spend_way END
    LEFT JOIN FX_Rate fx
      ON fx.code = af.fx_code
     AND fx.import_date = (
            SELECT MAX(fx2.import_date)
            FROM FX_Rate fx2
            WHERE fx2.code = af.fx_code
              AND substr(fx2.import_date, 1, 6) <= j.vesting_month
     )
    WHERE j.spend_way_table = 'Account'
      AND j.action_sub_table = 'Account'
      AND j.action_main = 'Transfer'
      AND af.owner IS NOT NULL
      AND substr(j.spend_date, 1, 4) = :year
      AND af.owner != at_.owner
    GROUP BY af.owner
    """
)


def get_gifted_by_year(session: Session, year: str) -> list[GiftItem]:
    if not re.fullmatch(r"\d{4}", year or ""):
        raise HTTPException(status_code=422, detail="year must be YYYY")
    result = session.exec(_GIFT_SQL, params={"year": year}).all()
    items: list[GiftItem] = []
    for row in result:
        owner = row[0]
        amount = float(row[1] or 0.0)
        rate = round(amount * 100 / GIFT_THRESHOLD, 2)
        items.append(GiftItem(owner=owner, amount=round(amount, 2), rate=rate))
    return items
