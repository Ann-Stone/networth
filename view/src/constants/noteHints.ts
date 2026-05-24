/**
 * Per-category placeholder hints for the journal `note` field.
 *
 * Matching:
 *  - For financial behaviors, set `main` to the behavior key (e.g., 'Transfer').
 *  - For codes, set `main` (and optionally `sub`) to the *display name*. Names
 *    survive ID changes from re-imports better than code_ids, and the user
 *    sees them when editing the form.
 *
 * Resolution order:
 *   1. exact (main, sub) match
 *   2. main-only match (applies to any sub under this main)
 *   3. fallback to '(可選)'
 */
export interface NoteHint {
  main: string
  sub?: string
  placeholder: string
}

export const NOTE_HINTS: NoteHint[] = [
  // ─── Financial behaviors ─────────────────────────────────────────────────
  { main: 'Transfer', placeholder: '匯率：1 USD = ? TWD（跨幣別時必填）' },
  { main: 'CreditCardRepayment', placeholder: '(可選) 對賬期間' },
  { main: 'LoanRepayment', placeholder: '(可選) 期數' },
  { main: 'Premiums', placeholder: '(可選) 保單號或保項' },

  // ─── 借出 / 借入（需先在「選單設定」建立對應子類別） ───────────────────
  { main: '人情往來', sub: '借出', placeholder: '對方姓名 + 事由（之後查餘額靠這欄）' },
  { main: '人情往來', sub: '借入', placeholder: '對方姓名 + 事由' },
  { main: '借貸收入', sub: '借款收入', placeholder: '對方姓名（要對得起當初借出的那筆）' },

  // ─── 人情往來其他子分類 ───────────────────────────────────────────────
  { main: '人情往來', sub: '婚宴', placeholder: '(可選) 對方姓名 + 關係' },
  { main: '人情往來', sub: '送禮', placeholder: '(可選) 對方姓名 + 場合' },
  { main: '人情往來', sub: '請客', placeholder: '(可選) 對象 + 場合' },
  { main: '人情往來', placeholder: '(可選) 對方姓名' },

  // ─── 投資與孳息 ───────────────────────────────────────────────────────
  { main: '孳息收入', sub: '股息', placeholder: '股票代號 + 股數，例如 TSLA 10' },
  { main: '孳息收入', sub: '銀行利息', placeholder: '(可選) 銀行或產品' },
  { main: '孳息收入', sub: '儲蓄險配息', placeholder: '(可選) 保單名' },
  { main: '投資', sub: '資本利得', placeholder: '標的代號 + 損益' },
  { main: '投資', sub: '期貨', placeholder: '標的 + 倉位' },
  { main: '投資', placeholder: '(可選) 標的代號' },

  // ─── 信用卡紅利 ───────────────────────────────────────────────────────
  { main: '信用卡紅利', placeholder: '(可選) 活動名或回饋來源' },

  // ─── 房租 ─────────────────────────────────────────────────────────────
  { main: '借貸收入', sub: '房租收入', placeholder: '房客姓名 + 月份' },
]

export function getNotePlaceholder(main?: string | null, sub?: string | null): string {
  if (!main) return '(可選)'
  if (sub) {
    const exact = NOTE_HINTS.find((h) => h.main === main && h.sub === sub)
    if (exact) return exact.placeholder
  }
  const mainOnly = NOTE_HINTS.find((h) => h.main === main && !h.sub)
  if (mainOnly) return mainOnly.placeholder
  return '(可選)'
}
