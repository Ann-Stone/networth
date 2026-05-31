"""Reports domain service functions (BE-025).

Aggregates Phase 1 monthly snapshots into balance sheet, expenditure trend,
and asset composition views. FX-converts everything to ``BASE_CURRENCY``.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Literal

from sqlmodel import Session, select

from app.models.assets.loan import Loan, LoanJournal
from app.models.assets.other_asset import OtherAsset
from app.models.assets.stock import StockJournal
from app.models.assets.stock_category import StockCategory
from app.models.dashboard.fx_rate import FXRate
from app.models.monthly_report.account_balance import AccountBalance
from app.models.monthly_report.credit_card_balance import CreditCardBalance
from app.models.monthly_report.estate_net_value_history import EstateNetValueHistory
from app.models.monthly_report.insurance_net_value_history import (
    InsuranceNetValueHistory,
)
from app.models.monthly_report.journal import Journal
from app.models.monthly_report.loan_balance import LoanBalance
from app.models.monthly_report.stock_net_value_history import StockNetValueHistory
from app.models.reports.asset_breakdown import AssetBreakdownRead, AssetShare
from app.models.reports.stock_allocation import StockAllocationRead, StockAllocationShare
from app.models.reports.balance import (
    BalanceAssets,
    BalanceLiabilities,
    BalanceLine,
    BalanceSheetRead,
)
from app.models.reports.budget_variance import (
    BudgetVarianceRead,
    BudgetVarianceRow,
    BudgetVarianceSummary,
)
from app.models.reports.cash_flow import (
    CashFlowActivity,
    CashFlowItem,
    CashFlowRead,
)
from app.models.reports.expense_insights import (
    ExpenseInsightsRead,
    LargeTxn,
    YoYRow,
)
from app.models.reports.expenditure import ExpenditurePoint, ExpenditureTrendRead
from app.models.reports.expenditure_composition import (
    ExpenditureCategoryNode,
    ExpenditureCompositionRead,
    ExpenditureSubNode,
)
from app.models.reports.income_expense import (
    IncomeExpensePoint,
    IncomeExpenseReportRead,
    IncomeExpenseSummary,
)
from app.models.settings.account import Account
from app.models.settings.budget import Budget
from app.models.settings.code_data import CodeData
from app.models.settings.credit_card import CreditCard

BASE_CURRENCY = "TWD"
EXPENSE_TYPES = ("Floating", "Fixed")

# Canonical action_main_type buckets, matched case-insensitively via _norm_type.
# The value's casing is inconsistent across the codebase and legacy data — the
# reports/dashboard domains use "Fixed"/"Income"/"Invest"/"Transfer" while the
# monthly domain and some imports use lowercase. Always normalize before
# comparing, or filters silently miss rows on real (capitalized) data.
EXPENSE_MAIN_TYPES = frozenset({"fixed", "floating"})
INCOME_MAIN_TYPES = frozenset({"income"})
INVEST_MAIN_TYPES = frozenset({"invest"})
TRANSFER_MAIN_TYPES = frozenset({"transfer"})


def _norm_type(action_main_type: str | None) -> str:
    """Lowercase/trim an action_main_type for case-insensitive comparison."""
    return (action_main_type or "").strip().lower()


def _month_end(yyyymm: str) -> str:
    return f"{yyyymm}31"


def get_latest_fx_rate(session: Session, currency: str, as_of_month: str) -> float:
    """Return latest ``FXRate.buy_rate`` with ``import_date <= month-end(as_of_month)``.

    Falls back to the most recent prior row of any date for the currency.
    Returns ``1.0`` when ``currency`` is the base currency or no row exists.
    """
    if not currency or currency == BASE_CURRENCY:
        return 1.0
    in_window = (
        select(FXRate)
        .where(FXRate.code == currency)
        .where(FXRate.import_date <= _month_end(as_of_month))
        .order_by(FXRate.import_date.desc())
    )
    row = session.exec(in_window).first()
    if row is not None:
        return row.buy_rate
    fallback = (
        select(FXRate).where(FXRate.code == currency).order_by(FXRate.import_date.desc())
    )
    row = session.exec(fallback).first()
    return row.buy_rate if row is not None else 1.0


def _latest_per_entity(rows, key):
    """Pick the row with the largest ``vesting_month`` per entity ``key(row)``."""
    latest: dict[str, object] = {}
    for r in rows:
        k = key(r)
        if k not in latest or r.vesting_month > latest[k].vesting_month:
            latest[k] = r
    return list(latest.values())


def get_balance_sheet(session: Session) -> BalanceSheetRead:
    accounts_rows = list(session.exec(select(AccountBalance)).all())
    accounts_latest = _latest_per_entity(accounts_rows, key=lambda r: r.id)
    accounts_lines = [
        BalanceLine(
            name=r.name,
            amount=round(r.balance * r.fx_rate, 2),
            original_amount=round(r.balance, 2),
            currency=r.fx_code,
        )
        for r in accounts_latest
        if r.is_calculate == "Y"
    ]

    stock_rows = list(session.exec(select(StockNetValueHistory)).all())
    stocks_lines = [
        BalanceLine(
            name=r.stock_name,
            amount=round(r.price * r.fx_rate, 2),
            original_amount=round(r.price, 2),
            currency=r.fx_code,
        )
        for r in _latest_per_entity(stock_rows, key=lambda r: r.id)
    ]

    estate_rows = list(session.exec(select(EstateNetValueHistory)).all())
    estates_lines = [
        BalanceLine(
            name=r.name,
            amount=round(r.market_value * r.fx_rate, 2),
            original_amount=round(r.market_value, 2),
            currency=r.fx_code,
        )
        for r in _latest_per_entity(estate_rows, key=lambda r: r.id)
    ]

    insurance_rows = list(session.exec(select(InsuranceNetValueHistory)).all())
    insurance_lines = [
        BalanceLine(
            name=r.name,
            amount=round(r.surrender_value * r.fx_rate, 2),
            original_amount=round(r.surrender_value, 2),
            currency=r.fx_code,
        )
        for r in _latest_per_entity(insurance_rows, key=lambda r: r.id)
    ]

    loan_rows = list(session.exec(select(LoanBalance)).all())
    loan_lines = [
        BalanceLine(
            name=r.name,
            amount=round(r.balance * r.fx_rate, 2),
            original_amount=round(r.balance, 2),
            currency=r.fx_code,
        )
        for r in _latest_per_entity(loan_rows, key=lambda r: r.id)
    ]

    cc_rows = list(session.exec(select(CreditCardBalance)).all())
    cc_lines = [
        BalanceLine(
            name=r.name,
            amount=round(r.balance * r.fx_rate, 2),
            original_amount=round(r.balance, 2),
            currency=BASE_CURRENCY,
        )
        for r in _latest_per_entity(cc_rows, key=lambda r: r.id)
    ]

    asset_total = sum(line.amount for line in accounts_lines + stocks_lines + estates_lines + insurance_lines)
    liability_total = sum(line.amount for line in loan_lines + cc_lines)
    net_worth = round(asset_total + liability_total, 2)  # liabilities are negative

    return BalanceSheetRead(
        assets=BalanceAssets(
            accounts=accounts_lines,
            stocks=stocks_lines,
            estates=estates_lines,
            insurances=insurance_lines,
        ),
        liabilities=BalanceLiabilities(loans=loan_lines, credit_cards=cc_lines),
        net_worth=net_worth,
    )


def _shift_month(yyyymm: str, delta: int) -> str:
    year = int(yyyymm[:4])
    month = int(yyyymm[4:]) + delta
    while month <= 0:
        month += 12
        year -= 1
    while month > 12:
        month -= 12
        year += 1
    return f"{year:04d}{month:02d}"


def _account_fx_code(session: Session, spend_way: str) -> str | None:
    """Resolve an Account's fx_code from Journal.spend_way (stringified Account.id)."""
    try:
        pk = int(spend_way)
    except (TypeError, ValueError):
        return None
    account = session.get(Account, pk)
    return account.fx_code if account is not None else None


def _card_fx_code(session: Session, spend_way: str) -> str | None:
    """Resolve a CreditCard's fx_code from Journal.spend_way (credit_card_id PK)."""
    card = session.get(CreditCard, spend_way)
    return card.fx_code if card is not None else None


def journal_fx_code(session: Session, journal: Journal) -> str:
    """Transaction currency of a journal, inferred from its payment source.

    Falls back to ``BASE_CURRENCY`` for unknown/dangling payment sources so
    callers never crash on legacy rows.
    """
    if journal.spend_way_table == "Account":
        return _account_fx_code(session, journal.spend_way) or BASE_CURRENCY
    if journal.spend_way_table == "Credit_Card":
        return _card_fx_code(session, journal.spend_way) or BASE_CURRENCY
    return BASE_CURRENCY


def journal_amount_twd(
    session: Session,
    journal: Journal,
    fx_cache: dict[tuple[str, str], float] | None = None,
) -> float:
    """Signed ``journal.spending`` converted to base currency (TWD).

    Unlike the monthly ``compute_gain_loss`` (which only converts account-funded
    rows), this also converts credit-card-funded spending via ``CreditCard.fx_code``.
    The sign is preserved verbatim (positive = income, negative = expense) so
    callers can compute net cash flow; take ``abs()`` only for expense-magnitude
    aggregations. Pass a shared ``fx_cache`` keyed by ``(fx_code, vesting_month)``
    when looping to avoid repeated rate lookups.
    """
    fx_code = journal_fx_code(session, journal)
    if fx_code == BASE_CURRENCY:
        return journal.spending
    if fx_cache is None:
        fx_cache = {}
    key = (fx_code, journal.vesting_month)
    if key not in fx_cache:
        fx_cache[key] = get_latest_fx_rate(session, fx_code, journal.vesting_month)
    return journal.spending * fx_cache[key]


def list_journals_by_range(
    session: Session, start_vesting_month: str, end_vesting_month: str
) -> list[Journal]:
    """All journals with ``start <= vesting_month <= end`` (inclusive), ordered."""
    statement = (
        select(Journal)
        .where(Journal.vesting_month >= start_vesting_month)
        .where(Journal.vesting_month <= end_vesting_month)
        .order_by(Journal.spend_date.asc(), Journal.distinct_number.asc())
    )
    return list(session.exec(statement).all())


def _period_window(
    type: Literal["monthly", "yearly"], vesting_month: str
) -> tuple[list[str], Callable[[str], str], str, str]:
    """Period axis for a trend: ``(periods oldest-first, bucket_of, start_vm, end_vm)``.

    ``monthly`` → 12 ``YYYYMM`` points ending at ``vesting_month``; ``yearly`` →
    10 ``YYYY`` points ending at that year. ``bucket_of`` maps a journal's
    ``vesting_month`` to its period key; ``start_vm``/``end_vm`` bound the
    inclusive query window. Shared by every range-based report so the windowing
    logic lives in one place.
    """
    if type == "monthly":
        periods = [_shift_month(vesting_month, -i) for i in range(11, -1, -1)]
        return periods, (lambda vm: vm), periods[0], periods[-1]
    end_year = int(vesting_month[:4])
    years = [str(y) for y in range(end_year - 9, end_year + 1)]
    return years, (lambda vm: vm[:4]), f"{years[0]}01", f"{years[-1]}12"


def get_expenditure_trend(
    session: Session,
    type: Literal["monthly", "yearly"],
    vesting_month: str,
) -> ExpenditureTrendRead:
    periods, bucket_of, start_vm, end_vm = _period_window(type, vesting_month)
    rows = list(
        session.exec(
            select(Journal)
            .where(Journal.vesting_month >= start_vm)
            .where(Journal.vesting_month <= end_vm)
            .where(Journal.action_main_type.in_(EXPENSE_TYPES))
        ).all()
    )
    sums: dict[str, float] = {p: 0.0 for p in periods}
    fx_cache: dict[tuple[str, str], float] = {}
    for j in rows:
        bucket = bucket_of(j.vesting_month)
        if bucket in sums:
            # FX-convert to base currency before summing; previously raw amounts
            # were added, mixing currencies (e.g. USD card spend + TWD). Rate is
            # positive, so abs() after conversion gives the expense magnitude.
            sums[bucket] += abs(journal_amount_twd(session, j, fx_cache))

    return ExpenditureTrendRead(
        type=type,
        points=[ExpenditurePoint(period=p, amount=round(sums[p], 2)) for p in periods],
    )


def get_income_expense_report(
    session: Session,
    type: Literal["monthly", "yearly"],
    vesting_month: str,
) -> IncomeExpenseReportRead:
    """Income-statement view: per-period income / fixed / floating / net plus an
    annual summary with savings rate.

    Invest and transfer rows are excluded — they are balance-sheet swaps, not
    operating income or expense. ``action_main_type`` is matched
    case-insensitively (``_norm_type``) so capitalized real data and lowercase
    legacy/import data both classify correctly.
    """
    periods, bucket_of, start_vm, end_vm = _period_window(type, vesting_month)
    journals = list_journals_by_range(session, start_vm, end_vm)
    fx_cache: dict[tuple[str, str], float] = {}
    income = {p: 0.0 for p in periods}
    fixed = {p: 0.0 for p in periods}
    floating = {p: 0.0 for p in periods}
    for j in journals:
        bucket = bucket_of(j.vesting_month)
        if bucket not in income:
            continue
        t = _norm_type(j.action_main_type)
        amount = journal_amount_twd(session, j, fx_cache)
        if t in INCOME_MAIN_TYPES:
            income[bucket] += amount  # signed pass-through; income is positive
        elif t == "fixed":
            fixed[bucket] += abs(amount)
        elif t == "floating":
            floating[bucket] += abs(amount)
        # invest / transfer intentionally excluded

    points: list[IncomeExpensePoint] = []
    for p in periods:
        inc = round(income[p], 2)
        fx = round(fixed[p], 2)
        fl = round(floating[p], 2)
        exp = round(fx + fl, 2)
        points.append(
            IncomeExpensePoint(
                period=p,
                income=inc,
                fixed=fx,
                floating=fl,
                expense=exp,
                net=round(inc - exp, 2),
            )
        )

    total_income = round(sum(pt.income for pt in points), 2)
    total_expense = round(sum(pt.expense for pt in points), 2)
    net = round(total_income - total_expense, 2)
    savings_rate = round(net / total_income, 4) if total_income else 0.0
    return IncomeExpenseReportRead(
        type=type,
        points=points,
        summary=IncomeExpenseSummary(
            total_income=total_income,
            total_expense=total_expense,
            net=net,
            savings_rate=savings_rate,
        ),
    )


def get_expenditure_composition(
    session: Session,
    type: Literal["monthly", "yearly"],
    vesting_month: str,
) -> ExpenditureCompositionRead:
    """Category → subcategory tree of expense magnitude over the window.

    Only Fixed/Floating rows are counted (income/invest/transfer excluded).
    Amounts are FX-converted; labels resolve ``action_main``/``action_sub`` codes
    to ``Code_Data.name``. Each node's ``share`` is a percentage of the grand
    total. When a category is partly sub-categorized, a synthetic "未細分"
    remainder child is appended so children reconcile to the category total.
    """
    _, _, start_vm, end_vm = _period_window(type, vesting_month)
    journals = list_journals_by_range(session, start_vm, end_vm)
    codes = {c.code_id: c for c in session.exec(select(CodeData)).all()}
    fx_cache: dict[tuple[str, str], float] = {}

    cat_amount: dict[str, float] = {}
    cat_type: dict[str, str] = {}
    sub_amount: dict[str, dict[str, float]] = {}
    for j in journals:
        if _norm_type(j.action_main_type) not in EXPENSE_MAIN_TYPES:
            continue
        amount = abs(journal_amount_twd(session, j, fx_cache))
        cat = j.action_main
        cat_amount[cat] = cat_amount.get(cat, 0.0) + amount
        cat_type.setdefault(cat, j.action_main_type)
        if j.action_sub:
            sub_amount.setdefault(cat, {})
            sub_amount[cat][j.action_sub] = sub_amount[cat].get(j.action_sub, 0.0) + amount

    total = sum(cat_amount.values())

    def share(value: float) -> float:
        return round(value * 100 / total, 2) if total else 0.0

    def name_of(code: str) -> str:
        row = codes.get(code)
        return row.name if row is not None else code

    categories: list[ExpenditureCategoryNode] = []
    for cat in sorted(cat_amount, key=lambda c: cat_amount[c], reverse=True):
        subs = sub_amount.get(cat, {})
        children: list[ExpenditureSubNode] = [
            ExpenditureSubNode(
                code=sc,
                name=name_of(sc),
                amount=round(subs[sc], 2),
                share=share(subs[sc]),
            )
            for sc in sorted(subs, key=lambda s: subs[s], reverse=True)
        ]
        if children:
            remainder = cat_amount[cat] - sum(subs.values())
            if remainder > 0.005:
                children.append(
                    ExpenditureSubNode(
                        code="",
                        name="未細分",
                        amount=round(remainder, 2),
                        share=share(remainder),
                    )
                )
        categories.append(
            ExpenditureCategoryNode(
                code=cat,
                name=name_of(cat),
                type=cat_type[cat],
                amount=round(cat_amount[cat], 2),
                share=share(cat_amount[cat]),
                children=children,
            )
        )

    fixed_total = sum(
        v for c, v in cat_amount.items() if _norm_type(cat_type[c]) == "fixed"
    )
    return ExpenditureCompositionRead(
        total=round(total, 2),
        fixed_total=round(fixed_total, 2),
        floating_total=round(total - fixed_total, 2),
        categories=categories,
    )


def get_budget_variance(session: Session, year: str) -> BudgetVarianceRead:
    """Annual budget vs actual per expense category for the calendar ``year``.

    Expected: ``Budget.annual_amount`` for annual-event categories (which budget
    as a single yearly envelope), else the sum of ``expected01..12``. Actual: the
    year's FX-converted Fixed/Floating journals grouped by ``action_main``.
    Annual-event categories are *included* here (unlike the monthly budget view)
    because a yearly review should account for lumpy once-a-year costs. Income,
    invest and transfer categories are excluded. ``projected_total`` annualizes
    the actual by the latest month carrying data, so a part-year reads as a
    run-rate rather than an apparent under-spend.
    """
    budgets = list(
        session.exec(select(Budget).where(Budget.budget_year == year)).all()
    )
    expected_by_code: dict[str, float] = {}
    name_by_code: dict[str, str] = {}
    type_by_code: dict[str, str] = {}
    for b in budgets:
        if _norm_type(b.code_type) not in EXPENSE_MAIN_TYPES:
            continue
        if b.annual_amount is not None:
            expected = b.annual_amount
        else:
            expected = sum(
                float(getattr(b, f"expected{m:02d}") or 0.0) for m in range(1, 13)
            )
        expected_by_code[b.category_code] = expected
        name_by_code[b.category_code] = b.category_name
        type_by_code[b.category_code] = b.code_type

    journals = list_journals_by_range(session, f"{year}01", f"{year}12")
    codes = {c.code_id: c for c in session.exec(select(CodeData)).all()}
    fx_cache: dict[tuple[str, str], float] = {}
    actual_by_code: dict[str, float] = {}
    months_with_data: set[int] = set()
    for j in journals:
        if _norm_type(j.action_main_type) not in EXPENSE_MAIN_TYPES:
            continue
        amount = abs(journal_amount_twd(session, j, fx_cache))
        actual_by_code[j.action_main] = actual_by_code.get(j.action_main, 0.0) + amount
        vm = j.vesting_month or ""
        if len(vm) == 6:
            months_with_data.add(int(vm[4:6]))
        if j.action_main not in name_by_code:
            row = codes.get(j.action_main)
            name_by_code[j.action_main] = row.name if row is not None else j.action_main
            type_by_code[j.action_main] = (
                row.code_type if row is not None else j.action_main_type
            )

    rows: list[BudgetVarianceRow] = []
    for code in sorted(
        set(expected_by_code) | set(actual_by_code),
        key=lambda c: actual_by_code.get(c, 0.0),
        reverse=True,
    ):
        expected = round(expected_by_code.get(code, 0.0), 2)
        actual = round(actual_by_code.get(code, 0.0), 2)
        rows.append(
            BudgetVarianceRow(
                code=code,
                name=name_by_code.get(code, code),
                type=type_by_code.get(code, ""),
                expected=expected,
                actual=actual,
                diff=round(actual - expected, 2),
                usage_rate=round(actual / expected, 4) if expected else 0.0,
            )
        )

    total_expected = round(sum(r.expected for r in rows), 2)
    total_actual = round(sum(r.actual for r in rows), 2)
    elapsed = max(months_with_data) if months_with_data else 0
    projected_total = (
        round(total_actual / elapsed * 12, 2) if 0 < elapsed < 12 else total_actual
    )
    return BudgetVarianceRead(
        year=year,
        rows=rows,
        summary=BudgetVarianceSummary(
            total_expected=total_expected,
            total_actual=total_actual,
            total_diff=round(total_actual - total_expected, 2),
            usage_rate=round(total_actual / total_expected, 4) if total_expected else 0.0,
            elapsed_months=elapsed,
            projected_total=projected_total,
        ),
    )


def _loanjournal_amount_twd(
    session: Session,
    row: LoanJournal,
    loan_by_id: dict[str, Loan],
    fx_cache: dict[tuple[str, str], float],
) -> float:
    """``LoanJournal.excute_price`` (a positive magnitude) converted to TWD.

    Currency follows the loan's repayment account (``Loan.account_id`` →
    ``Account.fx_code``); the rate is taken for the excute_date's month. Domestic
    loans stay 1:1.
    """
    loan = loan_by_id.get(row.loan_id)
    fx_code = BASE_CURRENCY
    if loan is not None:
        account = session.exec(
            select(Account).where(Account.account_id == loan.account_id)
        ).first()
        if account is not None and account.fx_code:
            fx_code = account.fx_code
    month = (row.excute_date or "")[:6]
    if fx_code == BASE_CURRENCY or len(month) != 6:
        return row.excute_price
    key = (fx_code, month)
    if key not in fx_cache:
        fx_cache[key] = get_latest_fx_rate(session, fx_code, month)
    return row.excute_price * fx_cache[key]


def get_cash_flow(
    session: Session,
    type: Literal["monthly", "yearly"],
    vesting_month: str,
) -> CashFlowRead:
    """Personal cash-flow statement split into 生活 / 投資 / 債務.

    - 生活 (operating): income (+) − living expenses (Fixed/Floating, −) − loan
      interest/fee (from LoanJournal, −).
    - 投資 (investing): signed Invest journals (buy negative, sell positive).
    - 債務 (financing): new borrowing (LoanJournal ``increment``, +) − principal
      repayment (LoanJournal ``principal``, −).

    Self-transfers are excluded (net-zero between own accounts; the type is also
    reused for gifts). Credit-card spend is counted once here as an operating
    outflow — settlement is a balance snapshot, not re-counted. Loan servicing is
    sourced solely from LoanJournal (it is not duplicated as main-Journal rows),
    so interest and principal are never double-counted. All amounts FX-converted.
    """
    _, _, start_vm, end_vm = _period_window(type, vesting_month)
    journals = list_journals_by_range(session, start_vm, end_vm)
    fx_cache: dict[tuple[str, str], float] = {}

    income = 0.0
    living = 0.0  # signed (negative)
    investing = 0.0  # signed
    for j in journals:
        t = _norm_type(j.action_main_type)
        amount = journal_amount_twd(session, j, fx_cache)
        if t in INCOME_MAIN_TYPES:
            income += amount
        elif t in EXPENSE_MAIN_TYPES:
            living += amount
        elif t in INVEST_MAIN_TYPES:
            investing += amount
        # transfer excluded

    loan_by_id = {loan.loan_id: loan for loan in session.exec(select(Loan)).all()}
    loan_interest = 0.0
    principal = 0.0
    increment = 0.0
    for lr in session.exec(select(LoanJournal)).all():
        month = (lr.excute_date or "")[:6]
        if not (start_vm <= month <= end_vm):
            continue
        magnitude = _loanjournal_amount_twd(session, lr, loan_by_id, fx_cache)
        et = (lr.loan_excute_type or "").strip().lower()
        if et in {"interest", "fee"}:
            loan_interest += magnitude
        elif et == "principal":
            principal += magnitude
        elif et == "increment":
            increment += magnitude

    operating_net = round(income + living - loan_interest, 2)
    investing_net = round(investing, 2)
    financing_net = round(increment - principal, 2)
    net_change = round(operating_net + investing_net + financing_net, 2)

    operating_items = [
        CashFlowItem(label="收入", amount=round(income, 2)),
        CashFlowItem(label="生活支出", amount=round(living, 2)),
    ]
    if loan_interest:
        operating_items.append(CashFlowItem(label="貸款利息", amount=round(-loan_interest, 2)))

    financing_items: list[CashFlowItem] = []
    if increment:
        financing_items.append(CashFlowItem(label="新增借款", amount=round(increment, 2)))
    if principal:
        financing_items.append(CashFlowItem(label="償還本金", amount=round(-principal, 2)))

    activities = [
        CashFlowActivity(
            key="operating", label="生活", net=operating_net, items=operating_items
        ),
        CashFlowActivity(
            key="investing",
            label="投資",
            net=investing_net,
            items=[CashFlowItem(label="投資淨額", amount=round(investing, 2))],
        ),
        CashFlowActivity(
            key="financing", label="債務", net=financing_net, items=financing_items
        ),
    ]
    return CashFlowRead(activities=activities, net_change=net_change)


def _pay_way_name(session: Session, journal: Journal) -> str:
    """Human-readable payment source name for a journal (account or card)."""
    if journal.spend_way_table == "Account":
        try:
            pk = int(journal.spend_way)
        except (TypeError, ValueError):
            return journal.spend_way
        account = session.get(Account, pk)
        return account.name if account is not None else journal.spend_way
    if journal.spend_way_table == "Credit_Card":
        card = session.get(CreditCard, journal.spend_way)
        return card.card_name if card is not None else journal.spend_way
    return journal.spend_way


def get_expense_insights(
    session: Session, year: str, top_n: int = 10
) -> ExpenseInsightsRead:
    """Year-over-year change per expense category + the year's largest expenses.

    YoY compares the calendar ``year`` against the prior year, per ``action_main``
    category, ordered by the absolute change so the biggest movers surface first.
    ``largest`` lists the top-N individual Fixed/Floating transactions by
    FX-converted magnitude, each drilled down to date / category / amount /
    payment source / note.
    """
    codes = {c.code_id: c for c in session.exec(select(CodeData)).all()}
    fx_cache: dict[tuple[str, str], float] = {}

    def name_of(code: str) -> str:
        row = codes.get(code)
        return row.name if row is not None else code

    def type_of(code: str) -> str:
        row = codes.get(code)
        return row.code_type if row is not None else ""

    def expense_by_code(journals: list[Journal]) -> dict[str, float]:
        out: dict[str, float] = {}
        for j in journals:
            if _norm_type(j.action_main_type) not in EXPENSE_MAIN_TYPES:
                continue
            out[j.action_main] = out.get(j.action_main, 0.0) + abs(
                journal_amount_twd(session, j, fx_cache)
            )
        return out

    current_journals = list_journals_by_range(session, f"{year}01", f"{year}12")
    prev_year = str(int(year) - 1)
    prev_journals = list_journals_by_range(session, f"{prev_year}01", f"{prev_year}12")
    current = expense_by_code(current_journals)
    previous = expense_by_code(prev_journals)

    yoy: list[YoYRow] = []
    for code in sorted(
        set(current) | set(previous),
        key=lambda c: abs(current.get(c, 0.0) - previous.get(c, 0.0)),
        reverse=True,
    ):
        cur = round(current.get(code, 0.0), 2)
        prev = round(previous.get(code, 0.0), 2)
        yoy.append(
            YoYRow(
                code=code,
                name=name_of(code),
                type=type_of(code),
                current=cur,
                previous=prev,
                delta=round(cur - prev, 2),
                yoy_rate=round((cur - prev) / prev, 4) if prev else 0.0,
            )
        )

    expense_txns = [
        (j, abs(journal_amount_twd(session, j, fx_cache)))
        for j in current_journals
        if _norm_type(j.action_main_type) in EXPENSE_MAIN_TYPES
    ]
    expense_txns.sort(key=lambda pair: pair[1], reverse=True)
    largest = [
        LargeTxn(
            date=j.spend_date,
            category=name_of(j.action_main),
            amount=round(amount, 2),
            pay_way=_pay_way_name(session, j),
            note=j.note,
        )
        for j, amount in expense_txns[:top_n]
    ]

    return ExpenseInsightsRead(year=year, yoy=yoy, largest=largest)


def get_asset_breakdown(session: Session) -> AssetBreakdownRead:
    """Latest-month totals per bucket; ``other`` aggregates ``OtherAsset`` of type ``other``."""
    accounts_rows = list(session.exec(select(AccountBalance)).all())
    accounts_total = sum(
        r.balance * r.fx_rate
        for r in _latest_per_entity(accounts_rows, key=lambda r: r.id)
        if r.is_calculate == "Y"
    )

    stock_rows = list(session.exec(select(StockNetValueHistory)).all())
    stocks_total = sum(
        r.price * r.fx_rate
        for r in _latest_per_entity(stock_rows, key=lambda r: r.id)
    )

    estate_rows = list(session.exec(select(EstateNetValueHistory)).all())
    estates_total = sum(
        r.market_value * r.fx_rate
        for r in _latest_per_entity(estate_rows, key=lambda r: r.id)
    )

    insurance_rows = list(session.exec(select(InsuranceNetValueHistory)).all())
    insurances_total = sum(
        r.surrender_value * r.fx_rate
        for r in _latest_per_entity(insurance_rows, key=lambda r: r.id)
    )

    other_assets = list(
        session.exec(select(OtherAsset).where(OtherAsset.asset_type == "other")).all()
    )
    other_total = float(len(other_assets)) and 0.0  # placeholder; OtherAsset has no value column
    other_total = 0.0

    bucket_amounts = {
        "accounts": accounts_total,
        "stocks": stocks_total,
        "estates": estates_total,
        "insurances": insurances_total,
        "other": other_total,
    }
    total = sum(bucket_amounts.values())
    items = []
    for bucket_type, amount in bucket_amounts.items():
        share = round(amount * 100 / total, 2) if total else 0.0
        items.append(
            AssetShare(type=bucket_type, amount=round(amount, 2), share=share)
        )
    return AssetBreakdownRead(total=round(total, 2), items=items)


def get_stock_allocation(session: Session) -> StockAllocationRead:
    """Latest-month stock value split by ``Stock_Journal.category_id``.

    Mirrors ``get_asset_breakdown``'s stock valuation (``price * fx_rate`` on the
    latest snapshot per holding) so the per-category amounts reconcile with the
    ``stocks`` bucket there. Holdings with a null or dangling category collapse
    into the synthetic "未分類" (unclassified) share. Items are ordered by
    ``category_index`` with the unclassified share last.
    """
    unclassified = "未分類"

    stock_rows = list(session.exec(select(StockNetValueHistory)).all())
    latest = _latest_per_entity(stock_rows, key=lambda r: r.id)

    category_of = {
        s.stock_id: s.category_id for s in session.exec(select(StockJournal)).all()
    }
    categories = list(session.exec(select(StockCategory)).all())
    name_of = {c.category_id: c.name for c in categories}
    index_of = {c.category_id: c.category_index for c in categories}

    amounts: dict[str | None, float] = {}
    for r in latest:
        cid = category_of.get(r.id)
        if cid is not None and cid not in name_of:
            cid = None  # dangling reference → unclassified
        amounts[cid] = amounts.get(cid, 0.0) + r.price * r.fx_rate

    total = sum(amounts.values())
    ordered = sorted(
        amounts.items(),
        key=lambda kv: (kv[0] is None, index_of.get(kv[0], 0), kv[0] or ""),
    )
    items = [
        StockAllocationShare(
            category_id=cid,
            category_name=name_of[cid] if cid is not None else unclassified,
            amount=round(amount, 2),
            share=round(amount * 100 / total, 2) if total else 0.0,
        )
        for cid, amount in ordered
    ]
    return StockAllocationRead(total=round(total, 2), items=items)
