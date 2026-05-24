/**
 * Display-only translations for SelectionGroup labels.
 *
 * BE returns English keys (account_type, table names) in `SelectionGroup.label`.
 * Templates render via `translateGroupLabel(label)` to show user-friendly
 * Chinese. Do NOT translate when storing values in journal payloads — the raw
 * key is the source of truth, only display layer translates.
 *
 * Source: account-book-view's commonData/accountData.js plus the financial
 * tables we surface as sub options.
 */
const GROUP_LABEL_TRANSLATIONS: Record<string, string> = {
  // Account types
  cash: '現金',
  normal: '一般帳戶',
  finance: '財務規劃帳戶',
  eWallet: '電子錢包',
  gift: '禮券',
  // Other financial entities
  Credit_Card: '信用卡',
  Loan: '貸款',
  Insurance: '保險',
  // Code types (main category groups)
  Floating: '浮動支出',
  Fixed: '固定支出',
  Income: '主動收入',
  Passive: '被動收入',
  Invest: '投資',
  Transfer: '轉帳',
}

export function translateGroupLabel(label: string): string {
  return GROUP_LABEL_TRANSLATIONS[label] ?? label
}
