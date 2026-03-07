import request from '@/utils/request'

export function getInitialList(conditions) {
  return request({
    url: '/initial/query',
    method: 'get',
    params: conditions
  })
}

export function addInitialData(data) {
  return request({
    url: '/initial',
    method: 'post',
    data: data
  })
}

export function updateInitialData(datas) {
  return request({
    url: '/initial',
    method: 'put',
    data: datas
  })
}

export function deleteInitialData(data) {
  return request({
    url: '/initial',
    method: 'delete',
    data: data
  })
}
