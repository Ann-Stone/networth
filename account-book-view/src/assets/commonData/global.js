export const yesNo = [
  { key: 'Y', value: '是' },
  { key: 'N', value: '否' }
]

export const assetType = [
  { key: 'Account', value: '銀行帳戶' },
  { key: 'CreditCard', value: '信用卡' },
  { key: 'Money', value: '現金' },
  { key: 'Loan', value: '貸款' }
]

export const otherAssetType = [
  {
    key: 'Stock',
    value: '股票',
    index: 1,
    table: 'Stock_Detail',
    type: 'Asset'
  },
  {
    key: 'Insurance',
    value: '保險',
    index: 2,
    table: 'Insurance_Journal',
    type: 'Asset'
  },
  {
    key: 'Estate',
    value: '房地產',
    index: 3,
    table: 'Estate_Journal',
    type: 'Asset'
  }
]

export const financialBehavior = [
  // {
  //   key: 'Invest',
  //   value: '投資',
  //   index: 1,
  //   table: 'Asset'
  // },
  {
    key: 'Transfer',
    value: '轉帳',
    index: 2,
    table: 'Account'
  },
  // {
  //   key: 'Deposit',
  //   value: '存款',
  //   index: 3,
  //   table: 'Account'
  // },
  {
    key: 'CreditCardRepayment',
    value: '繳信用卡款',
    index: 4,
    table: 'CreditCard'
  },
  {
    key: 'LoanRepayment',
    value: '繳貸款',
    index: 5,
    table: 'Loan'
  },
  {
    key: 'Premiums',
    value: '繳保費',
    index: 6,
    table: 'Insurance'
  }
  // {
  //   key: 'AddValue',
  //   value: '儲值',
  //   index: 7,
  //   table: 'Account'
  // }
  // {
  //   key: 'Refund',
  //   value: '退款',
  //   index: 8,
  //   table: 'Account'
  // }
]
