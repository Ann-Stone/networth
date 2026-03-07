import request from '@/utils/request'

export function getLiabilityList() {
  return request({
    url: '/liability/loan',
    method: 'get'
  })
}

export function getLiabilityById(loan_id) {
  return request({
    url: `/liability/loan/${loan_id}`,
    method: 'get'
  })
}

export function addLiabilityData(data) {
  return request({
    url: '/liability/loan',
    method: 'post',
    data: data
  })
}

export function updateLiabilityData(data) {
  return request({
    url: `/liability/loan/${data.loan_id}`,
    method: 'put',
    data: data
  })
}

export function deleteLiabilityData(id) {
  return request({
    url: `/liability/loan/${id}`,
    method: 'delete'
  })
}

export function getLoanSelection() {
  return request({
    url: '/liability/loan/selection',
    method: 'get'
  })
}

export function getLoanDetailList(loan_id) {
  return request({
    url: `/liability/loan/detail/${loan_id}`,
    method: 'get'
  })
}

export function addLoanDetailData(data) {
  return request({
    url: '/liability/loan/detail',
    method: 'post',
    data: data
  })
}

export function updateLoanDetailData(data) {
  return request({
    url: `/liability/loan/detail/${data.distinct_number}`,
    method: 'put',
    data: data
  })
}

export function deleteLoanDetailData(id) {
  return request({
    url: `/liability/loan/detail/${id}`,
    method: 'delete'
  })
}
