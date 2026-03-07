import request from '@/utils/request'

export function getJournalListByVestingMonth(vestingMonth) {
  return request({
    url: `/journal/${vestingMonth}`,
    method: 'get'
  })
}

export function deleteJournalData(id) {
  return request({
    url: `/journal/${id}`,
    method: 'delete'
  })
}

export function addJournalData(data) {
  return request({
    url: '/journal',
    method: 'post',
    data: data
  })
}

export function updateJournalData(data) {
  return request({
    url: `/journal/${data.distinct_number}`,
    method: 'put',
    data: data
  })
}

export function setMonthlySummary(vestingMonth) {
  return request({
    url: `/balance/${vestingMonth}`,
    method: 'put'
  })
}

export function getExpenditureRatioByVestingMonth(vestingMonth) {
  return request({
    url: `/journal/expenditure-ratio/${vestingMonth}`,
    method: 'get'
  })
}

export function getInvestRatioByVestingMonth(vestingMonth) {
  return request({
    url: `/journal/invest-ratio/${vestingMonth}`,
    method: 'get'
  })
}

export function getExpenditureBudgetByVestingMonth(vestingMonth) {
  return request({
    url: `/journal/expenditure-budget/${vestingMonth}`,
    method: 'get'
  })
}

export function getLiabilitiesByVestingMonth(vestingMonth) {
  return request({
    url: `/journal/liability/${vestingMonth}`,
    method: 'get'
  })
}

export async function getAllSubCodeList() {
  return await request({
    url: '/code/all-sub-code',
    method: 'get'
  })
}

export async function getStockPriceList(vestingMonth) {
  return await request({
    url: `/stock/price/${vestingMonth}`,
    method: 'get'
  })
}

export function addStockPrice(data) {
  return request({
    url: '/stock/price',
    method: 'post',
    data: data
  })
}
