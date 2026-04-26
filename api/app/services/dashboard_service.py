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
        if j.action_main_type == "Income":
            income[j.vesting_month] += abs(j.spending)
        if j.action_main in fixed_codes:
            fixed[j.vesting_month] += abs(j.spending)
    points: list[SummaryPoint] = []
    for m in months:
        ratio = (income[m] - fixed[m]) / income[m] if income[m] > 0 else 0.0
        points.append(SummaryPoint(period=m, value=round(ratio, 4)))
    return SummaryRead(type=SummaryType.freedom_ratio, points=points)


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
        points.append(SummaryPoint(period=m, value=round(value, 2)))
    return SummaryRead(type=SummaryType.asset_debt_trend, points=points)


def get_summary(session: Session, type: SummaryType, period: str) -> SummaryRead:
    parse_summary_period(period)
    if type == SummaryType.spending:
        return get_spending_summary(session, period)
    if type == SummaryType.freedom_ratio:
        return get_freedom_ratio_summary(session, period)
    if type == SummaryType.asset_debt_trend:
        return get_asset_debt_trend(session, period)
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
    if session.get(TargetSetting, data["distinct_number"]) is not None:
        raise HTTPException(
            status_code=409,
            detail=f"Duplicate distinct_number: {data['distinct_number']}",
        )
    row = TargetSetting(**data)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


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
    now = now or datetime.now()
    this_month = now.strftime("%Y%m")
    horizon_dt = now + relativedelta(months=6)
    horizon = horizon_dt.strftime("%Y%m")

    alarms = list(session.exec(select(Alarm)).all())
    items: list[AlarmItem] = []
    for a in alarms:
        if a.alarm_type == "M":
            base_year, base_month = now.year, now.month
            for i in range(6):
                month = base_month + i
                year = base_year
                while month > 12:
                    month -= 12
                    year += 1
                month_yyyymm = f"{year:04d}{month:02d}"
                if a.due_date and month_yyyymm > a.due_date[:6]:
                    continue
                items.append(
                    AlarmItem(date=f"{month:02d}/{a.alarm_date}", content=a.content)
                )
        else:
            alarm_period = a.alarm_date[:6] if len(a.alarm_date) >= 6 else a.alarm_date
            if alarm_period < this_month or alarm_period > horizon:
                continue
            items.append(AlarmItem(date=a.alarm_date, content=a.content))

    items.sort(key=lambda it: it.date)
    return items


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
