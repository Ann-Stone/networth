import request from '@/utils/request'

export function getBudgetList(thisYear) {
  return request({
    url: `/budget/${thisYear}`,
    method: 'get'
  })
}

export function getBudgetRange() {
  return request({
    url: '/budget/year-range',
    method: 'get'
  })
}

export function updateBudgetData(datas) {
  return request({
    url: '/budget',
    method: 'put',
    data: datas
  })
}

export function bulkInsertBudget(next_year) {
  return request({
    url: `/budget/${next_year}`,
    method: 'post'
  })
}
