# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal accounting book API built with Flask. This is the backend service for the account-book-view frontend (https://github.com/stone0215/account-book-view).

## Commands

```bash
# Install dependencies
pip install -r requirements.txt          # Windows
pip install --user -r requirements.txt   # macOS

# Run the application
python app.py
# Server runs on port 9528 (configured in config.py)
```

## Known Dependency Issues

If encountering errors, use `sqlalchemy==1.4.39` and ensure werkzeug version matches Flask version.

## Architecture

### Directory Structure
- `app.py` - Flask application entry point
- `config.py` - Configuration (database path, port, invoice API settings)
- `router/` - API route handlers organized by domain
- `app/dao/model/` - SQLAlchemy models organized by domain
- `api/response_format.py` - Standard JSON response wrapper (status, data, msg)
- `data/` - SQLite database files and schema

### Route Organization
Routes are organized by functional domain:
- `setting/` - Account, Budget, Code, CreditCard, Alarm, Initial settings
- `monthlyReport/` - Cash flow and journal entries
- `otherAssetAndLiabilities/` - Estate, Insurance, Stock, Loan, Other assets
- `yearReport/` - Annual reports
- `dashboardRouter.py`, `globalRouter.py` - Dashboard and global queries

### Database
- SQLite database stored at `data/ledger.db`
- Schema defined in `data/create_db.sql`
- Initial data loaded from `data/private_data.sql` (or `data/init_data.sql`)
- Key tables: Account, Journal, Code_Data, Credit_Card, Stock_Journal, Insurance, Estate, Loan

### Data Model Pattern
Each model file in `app/dao/model/` follows a consistent pattern:
- Inherits from `db.Model` via `DaoBase`
- Contains `queryByKey`, `queryByConditions`, `add`, `update`, `delete` methods
- Includes `output` method for JSON serialization

### API Response Format
All endpoints return JSON with structure:
```json
{"status": 1, "data": ..., "msg": "success"}  // success
{"status": 0, "error": ..., "msg": "fail"}    // failure
```

### Asset Types Tracked
- Bank accounts (Account table)
- Credit cards (Credit_Card table)
- Stocks (Stock_Journal, Stock_Detail tables)
- Insurance policies (Insurance, Insurance_Journal tables)
- Real estate (Estate, Estate_Journal tables)
- Loans (Loan, Loan_Journal tables)
- Monthly balance snapshots (*_Balance, *_Net_Value_History tables)
