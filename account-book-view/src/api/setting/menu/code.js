import request from '@/utils/request'

export function getMainCodeList(conditions) {
  return request({
    url: '/code/query',
    method: 'get',
    params: conditions
  })
}

export function addMainCodeData(data) {
  return request({
    url: '/code',
    method: 'post',
    data: data
  })
}

export function updateMainCodeData(data) {
  return request({
    url: `/code/${data.code_id}`,
    method: 'put',
    data: data
  })
}

export function getSubCodeList(parentId) {
  return request({
    url: `/sub-code/query/${parentId}`,
    method: 'get'
  })
}

export function addSubCodeData(data) {
  return request({
    url: '/sub-code',
    method: 'post',
    data: data
  })
}

export function updateSubCodeData(data) {
  return request({
    url: `/sub-code/${data.code_id}`,
    method: 'put',
    data: data
  })
}

export function deleteCodeData(id) {
  return request({
    url: `/code/${id}`,
    method: 'delete'
  })
}
