"""BE-005 — One-shot data migration from legacy ``account-book-API`` to networth-api.

Invocation
----------
    uv run python scripts/migrate_from_legacy.py \\
        [--legacy-db path/to/ledger.db] \\
        [--target-db-url sqlite:///path.db] \\
        [--no-wipe]

Defaults
--------
- ``--legacy-db``: ``account-book-API/data/ledger.db`` (relative to the repo
  root). Opened **read-only** via ``sqlite3.connect(... mode=ro ...)`` —
  this script never writes to the legacy DB.
- ``--target-db-url``: ``app.config.settings.database_url`` (typically
  ``sqlite:///~/.networth/networth.db``). Validated by
  ``_assert_safe_target_url`` — see "Safety" below.
- ``--no-wipe``: skip ``drop_all + create_all`` on the target before
  migrating. Default is ``wipe=True`` so the script is idempotent.

Idempotency contract
--------------------
With ``wipe=True`` (default), re-running produces identical state — every
table is dropped and re-created, then re-populated. With ``--no-wipe``,
each migrator uses ``session.merge()`` so re-running is still safe for
rows whose PK already exists; rows in the target but not in the source
are kept.

FK-safe execution order
-----------------------
The orchestrator runs migrators in this order so that referenced rows are
inserted before referencing rows:

    1. Code_Data                      (FK target of Budget, Journal action_*)
    2. Account                        (FK target of Loan, Stock_Detail, Insurance)
    3. Credit_Card                    (polymorphic Journal.spend_way target)
    4. Budget                         (FK -> Code_Data.code_id)
    5. Alarm
    6. Other_Asset                    (FK target of Stock_Journal, Insurance, Estate)
    7. Loan                           (FK target of Estate.loan_id)
    8. Loan_Journal
    9. Loan_Balance
   10. Stock_Journal
   11. Stock_Detail                   (FK -> Stock_Journal, Account)
   12. Stock_Net_Value_History
   13. Insurance                      (FK -> Other_Asset, Account)
   14. Insurance_Journal
   15. Insurance_Net_Value_History
   16. Estate                         (FK -> Other_Asset, Loan)
   17. Estate_Journal
   18. Estate_Net_Value_History
   19. Journal                        (polymorphic FK -> Account / Credit_Card / Code_Data)
   20. Account_Balance
   21. Credit_Card_Balance
   22. FX_Rate
   23. Stock_Price_History
   24. Target_Setting

Sub-task 13 of the granular ticket omitted four snapshot tables
(Loan_Balance, *_Net_Value_History x3) and placed Other_Asset / Loan in
the wrong slot for FK safety. The user confirmed the snapshots are in
active use, so they are migrated here as a scope expansion. Granular
Notes pair "migrate_stocks + migrate_stock_journals" did not match the
actual ``Stock_Journal`` (master) / ``Stock_Detail`` (transactions)
table layout; the migrator function names match the real ``__tablename__``s.

Field-removal rules
-------------------
- ``Account.carrier_no``: dropped. Legacy bug wrote ``carrier_no`` to
  ``owner``; we do **not** backfill (granular Notes).
- ``Credit_Card.carrier_no``: dropped. Legacy bug wrote ``carrier_no``
  to ``note``; we do **not** backfill.
- ``Initial_Setting``: skipped entirely; a logger warning is emitted if
  the source DB contains the table.

Semantic changes worth auditing
-------------------------------
- ``Loan.repayed``: legacy schema is ``CHARACTER(1)`` (Y/N flag); the new
  schema is ``float`` (cumulative principal repaid). Migration sets
  ``repayed = 0.0``; recompute downstream via the monthly settlement
  service (BE-019) before relying on balance reports.
- ``Insurance.in_account_name`` / ``out_account_name``: dropped. The new
  schema stores only ``in_account`` / ``out_account`` as the business
  ``Account.account_id`` strings, resolved from the legacy integer
  ``in_account_id`` / ``out_account_id`` via the Account lookup map.

Safety
------
- The legacy DB is opened read-only.
- ``_assert_safe_target_url`` refuses non-``sqlite:///`` URLs and any URL
  containing ``"prod"``.
- ``view/``, ``account-book-view/``, ``account-book-API/`` are never
  written.
"""
from __future__ import annotations

import argparse
import logging
import re
import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import dateutil.parser
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, func, select

import app.models  # noqa: F401  registers tables on SQLModel.metadata
from app.config import settings as app_settings
from app.database import SQLITE_PREFIX, _resolve_sqlite_url
from app.models.assets.estate import Estate, EstateJournal
from app.models.assets.insurance import Insurance, InsuranceJournal
from app.models.assets.loan import Loan, LoanJournal
from app.models.assets.other_asset import OtherAsset
from app.models.assets.stock import StockDetail, StockJournal
from app.models.dashboard.fx_rate import FXRate
from app.models.dashboard.stock_price_history import StockPriceHistory
from app.models.dashboard.target_setting import TargetSetting
from app.models.monthly_report.account_balance import AccountBalance
from app.models.monthly_report.credit_card_balance import CreditCardBalance
from app.models.monthly_report.estate_net_value_history import EstateNetValueHistory
from app.models.monthly_report.insurance_net_value_history import (
    InsuranceNetValueHistory,
)
from app.models.monthly_report.journal import Journal
from app.models.monthly_report.loan_balance import LoanBalance
from app.models.monthly_report.stock_net_value_history import StockNetValueHistory
from app.models.settings.account import Account
from app.models.settings.alarm import Alarm
from app.models.settings.budget import Budget
from app.models.settings.code_data import CodeData
from app.models.settings.credit_card import CreditCard


logger = logging.getLogger("migrate_from_legacy")

SKIP_TABLES = frozenset({"Initial_Setting"})

# Maps every retained legacy table name to its SQLModel target class.
# Order here is documentation only — execution order is set by
# ``run_migration``.
RETAINED_TABLES: dict[str, type[SQLModel]] = {
    "Code_Data": CodeData,
    "Account": Account,
    "Credit_Card": CreditCard,
    "Budget": Budget,
    "Alarm": Alarm,
    "Other_Asset": OtherAsset,
    "Loan": Loan,
    "Loan_Journal": LoanJournal,
    "Loan_Balance": LoanBalance,
    "Stock_Journal": StockJournal,
    "Stock_Detail": StockDetail,
    "Stock_Net_Value_History": StockNetValueHistory,
    "Insurance": Insurance,
    "Insurance_Journal": InsuranceJournal,
    "Insurance_Net_Value_History": InsuranceNetValueHistory,
    "Estate": Estate,
    "Estate_Journal": EstateJournal,
    "Estate_Net_Value_History": EstateNetValueHistory,
    "Journal": Journal,
    "Account_Balance": AccountBalance,
    "Credit_Card_Balance": CreditCardBalance,
    "FX_Rate": FXRate,
    "Stock_Price_History": StockPriceHistory,
    "Target_Setting": TargetSetting,
}


class MigrationCountMismatch(RuntimeError):
    """Raised when a migrator's inserted count differs from the source count."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_CAMEL_RE = re.compile(r"(?<!^)(?=[A-Z])")


def _snake(name: str) -> str:
    """Convert ``camelCase`` / ``PascalCase`` to ``snake_case``.

    Defensive helper for legacy DDL drift. Real ``create_db.sql`` is
    already snake_case but the fixture builder exercises one camelCase
    column to keep this helper honest.
    """
    return _CAMEL_RE.sub("_", name).lower()


def _row_to_dict(row: sqlite3.Row, *, drop: Iterable[str] = ()) -> dict[str, Any]:
    """Return a column-name -> value dict, snake-casing keys and dropping fields."""
    dropped = set(drop)
    return {
        _snake(k): row[k] for k in row.keys() if k not in dropped
    }


def _to_yyyymmdd(value: Any) -> str | None:
    """Normalize a legacy date/datetime value into ``YYYYMMDD``.

    Returns ``None`` for null / empty input. Already-normalized inputs
    pass through; everything else is parsed by ``dateutil.parser``.
    """
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    if re.fullmatch(r"\d{8}", s):
        return s
    return dateutil.parser.parse(s).strftime("%Y%m%d")


def _to_yyyymm(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    if re.fullmatch(r"\d{6}", s):
        return s
    return dateutil.parser.parse(s).strftime("%Y%m")


def _opt_int(value: Any) -> int | None:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    return int(float(s))


def _opt_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def _opt_str(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    return s or None


def _str(value: Any) -> str:
    return str(value)


@dataclass(frozen=True)
class LookupMaps:
    """Pre-loaded translation maps from legacy integer FKs to new string FKs."""

    account_int_to_str: dict[int, str]


def _synth_account_id(legacy_id: int) -> str:
    """Stable synthetic business ID for legacy Account rows whose
    ``account_id`` column is NULL/empty. Matches schema's NOT NULL +
    UNIQUE constraint while keeping FK resolution deterministic. User
    can rename these through the UI after migration.
    """
    return f"LEGACY-ACC-{legacy_id}"


def _load_lookup_maps(src: sqlite3.Connection) -> LookupMaps:
    """Build legacy.id → new business_id map for Account.

    Two patches over raw legacy data:
      * NULL / empty ``account_id`` → ``LEGACY-ACC-{id}`` (see ``_synth_account_id``).
      * Duplicate ``account_id`` (legacy schema lacked UNIQUE) → 2nd+
        occurrence gets ``-DUP-{id}`` suffix so it satisfies the new
        UNIQUE constraint. First occurrence keeps the original ID.
    Ordered by legacy ``id`` so "first wins" is deterministic.
    """
    cur = src.execute("SELECT id, account_id FROM Account ORDER BY id")
    account_map: dict[int, str] = {}
    seen: set[str] = set()
    for row in cur:
        if row["id"] is None:
            continue
        legacy_id = int(row["id"])
        biz_id = _opt_str(row["account_id"]) or _synth_account_id(legacy_id)
        if biz_id in seen:
            biz_id = f"{biz_id}-DUP-{legacy_id}"
        seen.add(biz_id)
        account_map[legacy_id] = biz_id
    return LookupMaps(account_int_to_str=account_map)


# ---------------------------------------------------------------------------
# Safety / engine plumbing
# ---------------------------------------------------------------------------

def _assert_safe_target_url(url: str) -> None:
    """Reject non-SQLite URLs and URLs that look like production."""
    if not url.startswith(SQLITE_PREFIX):
        raise RuntimeError(
            f"Refusing to migrate into non-SQLite target: {url!r}. "
            "Migration runs only against sqlite:/// URLs."
        )
    if "prod" in url.lower():
        raise RuntimeError(
            f"Refusing to migrate into production-pattern URL: {url!r} "
            "(contains 'prod')."
        )


def _build_engine(url: str):
    resolved = _resolve_sqlite_url(url)
    raw = resolved[len(SQLITE_PREFIX):]
    if raw == ":memory:":
        return create_engine(
            resolved,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    return create_engine(resolved, connect_args={"check_same_thread": False})


def _reset_target(engine) -> None:
    """Drop and re-create every table registered on SQLModel.metadata."""
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def _open_legacy(path: Path) -> sqlite3.Connection:
    if not path.exists():
        raise FileNotFoundError(f"Legacy DB not found: {path}")
    uri = f"file:{path.resolve()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Per-table migrators
# ---------------------------------------------------------------------------

def migrate_codes(src: sqlite3.Connection, session: Session) -> int:
    """Migrate ``Code_Data``. Legacy ``code_id INT`` → new ``code_id: str``.

    Legacy used ``code_group`` for parent/child hierarchy and stored the parent
    name in ``code_group_name``. The new schema uses ``parent_id`` only — pull
    hierarchy from ``code_group`` (fall back to ``parent_id`` if present in a
    newer snapshot) and discard the denormalized parent-name column.
    """
    count = 0
    for row in src.execute("SELECT * FROM Code_Data"):
        keys = row.keys()
        parent = None
        if "parent_id" in keys and row["parent_id"] is not None:
            parent = _opt_str(row["parent_id"])
        elif "code_group" in keys:
            parent = _opt_str(row["code_group"])
        session.merge(CodeData(
            code_id=_str(row["code_id"]),
            code_type=row["code_type"],
            name=row["name"],
            parent_id=parent,
            in_use=row["in_use"],
            code_index=_opt_int(row["code_index"]) or 0,
        ))
        count += 1
    session.commit()
    return count


def migrate_accounts(
    src: sqlite3.Connection, session: Session, *, maps: LookupMaps
) -> int:
    """Migrate ``Account`` rows. Drops ``carrier_no`` (no backfill).

    Business IDs come from ``maps.account_int_to_str``, which already
    applied NULL-synthesis and duplicate-dedup. We just compare against
    the raw legacy column to count and log adjustments.
    """
    count = 0
    synthesized = 0
    deduped = 0
    for row in src.execute("SELECT * FROM Account ORDER BY id"):
        legacy_id = int(row["id"])
        original = _opt_str(row["account_id"])
        final = maps.account_int_to_str[legacy_id]
        if not original:
            synthesized += 1
        elif final != original:
            deduped += 1
        session.merge(Account(
            id=legacy_id,
            account_id=final,
            name=row["name"],
            account_type=row["account_type"],
            fx_code=row["fx_code"],
            is_calculate=row["is_calculate"],
            in_use=row["in_use"],
            discount=float(row["discount"]) if row["discount"] is not None else 1.0,
            memo=_opt_str(row["memo"]),
            owner=_opt_str(row["owner"]),
            account_index=_opt_int(row["account_index"]) or 0,
        ))
        count += 1
    session.commit()
    if synthesized:
        logger.warning(
            "migrate_accounts: synthesized account_id for %d row(s) "
            "(legacy account_id was NULL/empty). Look for LEGACY-ACC-* "
            "entries and rename via the UI if desired.",
            synthesized,
        )
    if deduped:
        logger.warning(
            "migrate_accounts: dedup-renamed %d row(s) whose account_id "
            "collided with an earlier row. Look for *-DUP-{id} entries "
            "and rename via the UI if desired.",
            deduped,
        )
    return count


def migrate_credit_cards(src: sqlite3.Connection, session: Session) -> int:
    """Migrate ``Credit_Card`` rows. Drops ``carrier_no`` (no backfill)."""
    count = 0
    for row in src.execute("SELECT * FROM Credit_Card"):
        # Legacy semantic mismatch: legacy `limit_date` stored card
        # expiration ("YYYY/MM"), but the new schema's `limit_date` means
        # "payment due day of month" (int 1-31). Reroute the legacy value
        # into the new `card_expiry` column and leave `limit_date` NULL
        # for the user to fill in via UI later.
        legacy_limit = _opt_str(row["limit_date"])
        session.merge(CreditCard(
            credit_card_id=_str(row["credit_card_id"]),
            card_name=row["card_name"],
            card_no=_opt_str(row["card_no"]),
            last_day=_opt_int(row["last_day"]),
            charge_day=_opt_int(row["charge_day"]),
            limit_date=None,
            card_expiry=legacy_limit,
            feedback_way=_opt_str(row["feedback_way"]),
            fx_code=row["fx_code"],
            in_use=row["in_use"],
            credit_card_index=_opt_int(row["credit_card_index"]) or 0,
            note=_opt_str(row["note"]),
        ))
        count += 1
    session.commit()
    return count


def migrate_budgets(src: sqlite3.Connection, session: Session) -> int:
    count = 0
    for row in src.execute("SELECT * FROM Budget"):
        session.merge(Budget(
            budget_year=str(row["budget_year"]),
            category_code=_str(row["category_code"]),
            category_name=row["category_name"],
            code_type=row["code_type"],
            **{f"expected{m:02d}": float(row[f"expected{m:02d}"]) for m in range(1, 13)},
        ))
        count += 1
    session.commit()
    return count


def migrate_alarms(src: sqlite3.Connection, session: Session) -> int:
    count = 0
    for row in src.execute("SELECT * FROM Alarm"):
        session.merge(Alarm(
            alarm_id=int(row["alarm_id"]),
            alarm_type=row["alarm_type"],
            alarm_date=_to_yyyymmdd(row["alarm_date"]) or str(row["alarm_date"]),
            content=row["content"],
            due_date=_to_yyyymmdd(row["due_date"]),
        ))
        count += 1
    session.commit()
    return count


def migrate_other_assets(src: sqlite3.Connection, session: Session) -> int:
    count = 0
    for row in src.execute("SELECT * FROM Other_Asset"):
        session.merge(OtherAsset(
            asset_id=_str(row["asset_id"]),
            asset_name=row["asset_name"],
            asset_type=row["asset_type"],
            in_use=row["in_use"],
            asset_index=_opt_int(row["asset_index"]) or 0,
        ))
        count += 1
    session.commit()
    return count


def migrate_loans(src: sqlite3.Connection, session: Session, *, maps: LookupMaps) -> int:
    """Migrate ``Loan``. Translates ``account_id INT -> str`` via account map.

    ``Loan.repayed`` semantics changed (legacy CHARACTER(1) Y/N flag, new
    float cumulative principal). We set ``repayed=0.0`` here; downstream
    settlement logic should recompute before balance reports are trusted.
    """
    count = 0
    for row in src.execute("SELECT * FROM Loan"):
        legacy_account_int = int(row["account_id"])
        account_id_str = maps.account_int_to_str.get(legacy_account_int, str(legacy_account_int))
        session.merge(Loan(
            loan_id=_str(row["loan_id"]),
            loan_name=row["loan_name"],
            loan_type=row["loan_type"],
            account_id=account_id_str,
            account_name=row["account_name"],
            interest_rate=float(row["interest_rate"]),
            period=int(row["period"]),
            apply_date=_to_yyyymmdd(row["apply_date"]) or "",
            grace_expire_date=_to_yyyymmdd(row["grace_expire_date"]),
            pay_day=int(str(row["pay_day"]).strip()),
            amount=float(row["amount"]),
            repayed=0.0,  # IMPL-NOTE: legacy is Y/N flag; new is float — recompute downstream
            loan_index=_opt_int(row["loan_index"]) or 0,
        ))
        count += 1
    session.commit()
    return count


def migrate_loan_journals(src: sqlite3.Connection, session: Session) -> int:
    count = 0
    for row in src.execute("SELECT * FROM Loan_Journal"):
        session.merge(LoanJournal(
            distinct_number=int(row["distinct_number"]),
            loan_id=_str(row["loan_id"]),
            loan_excute_type=row["loan_excute_type"],
            excute_price=float(row["excute_price"]),
            excute_date=_to_yyyymmdd(row["excute_date"]) or "",
            memo=_opt_str(row["memo"]),
        ))
        count += 1
    session.commit()
    return count


def migrate_loan_balances(src: sqlite3.Connection, session: Session) -> int:
    """Scope expansion vs granular doc — confirmed in plan."""
    count = 0
    for row in src.execute("SELECT * FROM Loan_Balance"):
        session.merge(LoanBalance(
            vesting_month=_to_yyyymm(row["vesting_month"]) or str(row["vesting_month"]),
            id=_str(row["id"]),
            name=row["name"],
            balance=float(row["balance"]),
            cost=float(row["cost"]),
            fx_code="TWD",
            fx_rate=1.0,
        ))
        count += 1
    session.commit()
    return count


def migrate_stock_journals(src: sqlite3.Connection, session: Session) -> int:
    """Master holdings (legacy ``Stock_Journal``). Preserves ``expected_spend``."""
    count = 0
    for row in src.execute("SELECT * FROM Stock_Journal"):
        session.merge(StockJournal(
            stock_id=_str(row["stock_id"]),
            stock_code=row["stock_code"],
            stock_name=row["stock_name"],
            asset_id=_str(row["asset_id"]),
            expected_spend=float(row["expected_spend"]) if row["expected_spend"] is not None else 0.0,
        ))
        count += 1
    session.commit()
    return count


def migrate_stock_details(src: sqlite3.Connection, session: Session, *, maps: LookupMaps) -> int:
    """Transactions (legacy ``Stock_Detail``). Translates account_id INT -> str."""
    count = 0
    for row in src.execute("SELECT * FROM Stock_Detail"):
        legacy_account_int = int(row["account_id"])
        account_id_str = maps.account_int_to_str.get(legacy_account_int, str(legacy_account_int))
        session.merge(StockDetail(
            distinct_number=int(row["distinct_number"]),
            stock_id=_str(row["stock_id"]),
            excute_type=row["excute_type"],
            excute_amount=float(row["excute_amount"]) if row["excute_amount"] is not None else 0.0,
            excute_price=float(row["excute_price"]) if row["excute_price"] is not None else 0.0,
            excute_date=_to_yyyymmdd(row["excute_date"]) or "",
            account_id=account_id_str,
            account_name=row["account_name"],
            memo=_opt_str(row["memo"]),
        ))
        count += 1
    session.commit()
    return count


def migrate_stock_net_value_history(src: sqlite3.Connection, session: Session) -> int:
    """Scope expansion vs granular doc."""
    count = 0
    for row in src.execute("SELECT * FROM Stock_Net_Value_History"):
        session.merge(StockNetValueHistory(
            vesting_month=_to_yyyymm(row["vesting_month"]) or str(row["vesting_month"]),
            id=_str(row["id"]),
            asset_id=_str(row["asset_id"]),
            stock_code=row["stock_code"],
            stock_name=row["stock_name"],
            amount=float(row["amount"]),
            price=float(row["price"]),
            cost=float(row["cost"]),
            fx_code=row["fx_code"],
            fx_rate=float(row["fx_rate"]),
        ))
        count += 1
    session.commit()
    return count


def migrate_insurance(src: sqlite3.Connection, session: Session, *, maps: LookupMaps) -> int:
    """Migrate ``Insurance``. Translates in/out_account_id INT -> account_id str.

    Drops legacy ``in_account_name`` / ``out_account_name`` (new schema
    stores only the business ID references; names are looked up via JOIN).
    Maps legacy ``expected_end_date`` → new ``end_date``.
    """
    count = 0
    for row in src.execute("SELECT * FROM Insurance"):
        in_account = maps.account_int_to_str.get(
            int(row["in_account_id"]), str(row["in_account_id"])
        )
        out_account = maps.account_int_to_str.get(
            int(row["out_account_id"]), str(row["out_account_id"])
        )
        session.merge(Insurance(
            insurance_id=_str(row["insurance_id"]),
            insurance_name=row["insurance_name"],
            asset_id=_str(row["asset_id"]),
            in_account=in_account,
            out_account=out_account,
            start_date=_to_yyyymmdd(row["start_date"]) or "",
            end_date=_to_yyyymmdd(row["expected_end_date"]) or "",
            pay_type=row["pay_type"],
            pay_day=_opt_str(row["pay_day"]) or "",
            expected_spend=float(row["expected_spend"]) if row["expected_spend"] is not None else 0.0,
            has_closed=row["has_closed"],
        ))
        count += 1
    session.commit()
    return count


def migrate_insurance_journals(src: sqlite3.Connection, session: Session) -> int:
    count = 0
    for row in src.execute("SELECT * FROM Insurance_Journal"):
        session.merge(InsuranceJournal(
            distinct_number=int(row["distinct_number"]),
            insurance_id=_str(row["insurance_id"]),
            insurance_excute_type=row["insurance_excute_type"],
            excute_price=float(row["excute_price"]),
            excute_date=_to_yyyymmdd(row["excute_date"]) or "",
            memo=_opt_str(row["memo"]),
        ))
        count += 1
    session.commit()
    return count


def migrate_insurance_net_value_history(src: sqlite3.Connection, session: Session) -> int:
    """Scope expansion vs granular doc."""
    count = 0
    for row in src.execute("SELECT * FROM Insurance_Net_Value_History"):
        session.merge(InsuranceNetValueHistory(
            vesting_month=_to_yyyymm(row["vesting_month"]) or str(row["vesting_month"]),
            id=_str(row["id"]),
            asset_id=_str(row["asset_id"]),
            name=row["name"],
            surrender_value=float(row["surrender_value"]),
            cost=float(row["cost"]),
            fx_code=row["fx_code"],
            fx_rate=float(row["fx_rate"]),
        ))
        count += 1
    session.commit()
    return count


def migrate_estate(src: sqlite3.Connection, session: Session) -> int:
    count = 0
    for row in src.execute("SELECT * FROM Estate"):
        session.merge(Estate(
            estate_id=_str(row["estate_id"]),
            estate_name=row["estate_name"],
            estate_type=row["estate_type"],
            estate_address=row["estate_address"],
            asset_id=_str(row["asset_id"]),
            obtain_date=_to_yyyymmdd(row["obtain_date"]) or "",
            loan_id=_str(row["loan_id"]) if row["loan_id"] is not None else None,
            estate_status=row["estate_status"],
            memo=_opt_str(row["memo"]),
        ))
        count += 1
    session.commit()
    return count


def migrate_estate_journals(src: sqlite3.Connection, session: Session) -> int:
    count = 0
    for row in src.execute("SELECT * FROM Estate_Journal"):
        session.merge(EstateJournal(
            distinct_number=int(row["distinct_number"]),
            estate_id=_str(row["estate_id"]),
            estate_excute_type=row["estate_excute_type"],
            excute_price=float(row["excute_price"]),
            excute_date=_to_yyyymmdd(row["excute_date"]) or "",
            memo=_opt_str(row["memo"]),
        ))
        count += 1
    session.commit()
    return count


def migrate_estate_net_value_history(src: sqlite3.Connection, session: Session) -> int:
    """Scope expansion vs granular doc."""
    count = 0
    for row in src.execute("SELECT * FROM Estate_Net_Value_History"):
        session.merge(EstateNetValueHistory(
            vesting_month=_to_yyyymm(row["vesting_month"]) or str(row["vesting_month"]),
            id=_str(row["id"]),
            asset_id=_str(row["asset_id"]),
            name=row["name"],
            market_value=float(row["market_value"]),
            cost=float(row["cost"]),
            estate_status=row["estate_status"],
            fx_code="TWD",
            fx_rate=1.0,
        ))
        count += 1
    session.commit()
    return count


def migrate_journals(src: sqlite3.Connection, session: Session) -> int:
    """Preserves ``invoice_number``; normalizes dates to YYYYMMDD / YYYYMM."""
    count = 0
    for row in src.execute("SELECT * FROM Journal"):
        session.merge(Journal(
            distinct_number=int(row["distinct_number"]),
            vesting_month=_to_yyyymm(row["vesting_month"]) or str(row["vesting_month"]),
            spend_date=_to_yyyymmdd(row["spend_date"]) or "",
            spend_way=_str(row["spend_way"]),
            spend_way_type=row["spend_way_type"],
            spend_way_table=row["spend_way_table"],
            action_main=_str(row["action_main"]),
            action_main_type=row["action_main_type"],
            action_main_table=row["action_main_table"],
            action_sub=_opt_str(row["action_sub"]),
            action_sub_type=_opt_str(row["action_sub_type"]),
            action_sub_table=_opt_str(row["action_sub_table"]),
            spending=float(row["spending"]),
            invoice_number=_opt_str(row["invoice_number"]),
            note=_opt_str(row["note"]),
        ))
        count += 1
    session.commit()
    return count


def migrate_account_balances(src: sqlite3.Connection, session: Session) -> int:
    count = 0
    for row in src.execute("SELECT * FROM Account_Balance"):
        session.merge(AccountBalance(
            vesting_month=_to_yyyymm(row["vesting_month"]) or str(row["vesting_month"]),
            id=_str(row["id"]),
            name=row["name"],
            balance=float(row["balance"]),
            fx_code=row["fx_code"],
            fx_rate=float(row["fx_rate"]),
            is_calculate=row["is_calculate"],
        ))
        count += 1
    session.commit()
    return count


def migrate_credit_card_balances(src: sqlite3.Connection, session: Session) -> int:
    count = 0
    for row in src.execute("SELECT * FROM Credit_Card_Balance"):
        session.merge(CreditCardBalance(
            vesting_month=_to_yyyymm(row["vesting_month"]) or str(row["vesting_month"]),
            id=_str(row["id"]),
            name=row["name"],
            balance=float(row["balance"]),
            fx_rate=float(row["fx_rate"]),
        ))
        count += 1
    session.commit()
    return count


def migrate_fx_rates(src: sqlite3.Connection, session: Session) -> int:
    count = 0
    for row in src.execute("SELECT * FROM FX_Rate"):
        session.merge(FXRate(
            import_date=_to_yyyymmdd(row["import_date"]) or str(row["import_date"]),
            code=row["code"],
            buy_rate=float(row["buy_rate"]),
        ))
        count += 1
    session.commit()
    return count


def migrate_stock_price_history(src: sqlite3.Connection, session: Session) -> int:
    count = 0
    for row in src.execute("SELECT * FROM Stock_Price_History"):
        session.merge(StockPriceHistory(
            stock_code=row["stock_code"],
            fetch_date=_to_yyyymmdd(row["fetch_date"]) or str(row["fetch_date"]),
            open_price=float(row["open_price"]) if row["open_price"] is not None else 0.0,
            highest_price=float(row["highest_price"]) if row["highest_price"] is not None else 0.0,
            lowest_price=float(row["lowest_price"]) if row["lowest_price"] is not None else 0.0,
            close_price=float(row["close_price"]),
        ))
        count += 1
    session.commit()
    return count


def migrate_target_settings(src: sqlite3.Connection, session: Session) -> int:
    """Cast legacy ``distinct_number INT`` → new ``str``."""
    count = 0
    for row in src.execute("SELECT * FROM Target_Setting"):
        session.merge(TargetSetting(
            distinct_number=_str(row["distinct_number"]),
            target_year=str(row["target_year"]),
            setting_value=_str(row["setting_value"]),
            is_done=row["is_done"],
        ))
        count += 1
    session.commit()
    return count


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def _source_table_names(src: sqlite3.Connection) -> set[str]:
    cur = src.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return {row["name"] for row in cur}


def _source_count(src: sqlite3.Connection, table: str) -> int:
    cur = src.execute(f"SELECT COUNT(*) AS n FROM {table}")
    return int(cur.fetchone()["n"])


def run_migration(src: sqlite3.Connection, engine, *, wipe: bool = True) -> dict[str, int]:
    """Run every migrator in FK-safe order; return per-legacy-table inserted counts.

    Raises ``MigrationCountMismatch`` if any migrator's inserted count
    differs from the legacy source count.
    """
    if wipe:
        _reset_target(engine)

    src_tables = _source_table_names(src)
    for skipped in SKIP_TABLES & src_tables:
        logger.warning("Skipping legacy table: %s", skipped)

    counts: dict[str, int] = {}
    with Session(engine) as session:
        maps = _load_lookup_maps(src)

        # FK-safe order. The mapping value is the migrator callable; some
        # migrators need the lookup maps and are wrapped in lambdas.
        migrators: list[tuple[str, Any]] = [
            ("Code_Data", migrate_codes),
            ("Account", lambda s, sess: migrate_accounts(s, sess, maps=maps)),
            ("Credit_Card", migrate_credit_cards),
            ("Budget", migrate_budgets),
            ("Alarm", migrate_alarms),
            ("Other_Asset", migrate_other_assets),
            ("Loan", lambda s, sess: migrate_loans(s, sess, maps=maps)),
            ("Loan_Journal", migrate_loan_journals),
            ("Loan_Balance", migrate_loan_balances),
            ("Stock_Journal", migrate_stock_journals),
            ("Stock_Detail", lambda s, sess: migrate_stock_details(s, sess, maps=maps)),
            ("Stock_Net_Value_History", migrate_stock_net_value_history),
            ("Insurance", lambda s, sess: migrate_insurance(s, sess, maps=maps)),
            ("Insurance_Journal", migrate_insurance_journals),
            ("Insurance_Net_Value_History", migrate_insurance_net_value_history),
            ("Estate", migrate_estate),
            ("Estate_Journal", migrate_estate_journals),
            ("Estate_Net_Value_History", migrate_estate_net_value_history),
            ("Journal", migrate_journals),
            ("Account_Balance", migrate_account_balances),
            ("Credit_Card_Balance", migrate_credit_card_balances),
            ("FX_Rate", migrate_fx_rates),
            ("Stock_Price_History", migrate_stock_price_history),
            ("Target_Setting", migrate_target_settings),
        ]

        for legacy_table, migrator in migrators:
            if legacy_table not in src_tables:
                logger.warning("Legacy table missing, skipping: %s", legacy_table)
                counts[legacy_table] = 0
                continue
            inserted = migrator(src, session)
            expected = _source_count(src, legacy_table)
            if inserted != expected:
                raise MigrationCountMismatch(
                    f"{legacy_table}: migrator inserted {inserted}, "
                    f"source has {expected}"
                )
            counts[legacy_table] = inserted
            logger.info("%s: %d rows migrated", legacy_table, inserted)

    return counts


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

DEFAULT_LEGACY_DB = Path("account-book-API/data/ledger.db")


def main(
    legacy_db: Path = DEFAULT_LEGACY_DB,
    target_db_url: str | None = None,
    wipe: bool = True,
) -> dict[str, int]:
    url = target_db_url or app_settings.database_url
    _assert_safe_target_url(url)
    engine = _build_engine(url)
    src = _open_legacy(legacy_db)
    try:
        return run_migration(src, engine, wipe=wipe)
    finally:
        src.close()
        engine.dispose()


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="migrate_from_legacy",
        description=(
            "BE-005 one-shot data migration: copies account-book-API/ledger.db "
            "into the networth-api SQLite database, applying field-removal "
            "rules and skipping Initial_Setting."
        ),
    )
    parser.add_argument(
        "--legacy-db",
        type=Path,
        default=DEFAULT_LEGACY_DB,
        help=(
            "Path to the legacy ledger.db (opened read-only). "
            f"Default: {DEFAULT_LEGACY_DB}"
        ),
    )
    parser.add_argument(
        "--target-db-url",
        default=None,
        help=(
            "Override the target SQLite URL. Defaults to "
            "app.config.settings.database_url. Must be a sqlite:/// URL "
            "and must not contain 'prod'."
        ),
    )
    parser.add_argument(
        "--no-wipe",
        dest="wipe",
        action="store_false",
        help="Skip drop_all + create_all on the target before migrating.",
    )
    parser.set_defaults(wipe=True)
    return parser


def _cli_entry(argv: Iterable[str] | None = None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = _build_arg_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    counts = main(
        legacy_db=args.legacy_db,
        target_db_url=args.target_db_url,
        wipe=args.wipe,
    )
    for table, n in counts.items():
        print(f"{table}: {n}")


if __name__ == "__main__":
    _cli_entry()
