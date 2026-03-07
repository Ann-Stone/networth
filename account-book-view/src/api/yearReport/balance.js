import request from '@/utils/request'

export function getBalanceList() {
  return request({
    url: '/report/balance',
    method: 'get'
  })
}

export function getSpendingList({ type, dateValue }) {
  return request({
    url: `/report/expenditure/${type}/${dateValue}`,
    method: 'get'
  })
}

export function getAssetList() {
  return request({
    url: '/report/asset',
    method: 'get'
  })
}
