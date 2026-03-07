import request from '@/utils/request'

export function getSummary({ type, dateValue }) {
  return request({
    url: `/dashboard/summary/${type}/${dateValue}`,
    method: 'get'
  })
}

export function getBudgetUsed({ type, dateValue }) {
  return request({
    url: `/dashboard/budget/${type}/${dateValue}`,
    method: 'get'
  })
}

export function getAlarmList() {
  return request({
    url: '/dashboard/alarm',
    method: 'get'
  })
}

export function getGiftedList(year) {
  return request({
    url: `/dashboard/gift/${year}`,
    method: 'get'
  })
}

export function getTargetList() {
  return request({
    url: '/dashboard/target',
    method: 'get'
  })
}

export function addTarget(data) {
  return request({
    url: '/target',
    method: 'post',
    data: data
  })
}

export function updateTarget(data) {
  return request({
    url: `/target/${data.distinct_number}`,
    method: 'put',
    data: data
  })
}

export function deleteTarget(id) {
  return request({
    url: `/target/${id}`,
    method: 'delete'
  })
}
