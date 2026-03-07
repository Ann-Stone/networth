import request from '@/utils/request'

export function getLoanList() {
  return request({
    url: '/loan/query',
    method: 'get'
  })
}

export function addLoanData(data) {
  return request({
    url: '/loan',
    method: 'post',
    data: data
  })
}

export function updateLoanData(data) {
  return request({
    url: `/loan/${data.loan_id}`,
    method: 'put',
    data: data
  })
}

export function deleteLoanData(id) {
  return request({
    url: `/loan/${id}`,
    method: 'delete'
  })
}
