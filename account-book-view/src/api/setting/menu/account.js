import request from '@/utils/request'

export function getAccountList(conditions) {
  return request({
    url: '/account/query',
    method: 'get',
    params: conditions
  })
}

export function addAccountData(data) {
  return request({
    url: '/account',
    method: 'post',
    data: data
  })
}

export function updateAccountData(data) {
  return request({
    url: `/account/${data.id}`,
    method: 'put',
    data: data
  })
}

export function deleteAccountData(id) {
  return request({
    url: `/account/${id}`,
    method: 'delete'
  })
}

export function getAccountSelection() {
  return request({
    url: '/account/selection',
    method: 'get'
  })
}
