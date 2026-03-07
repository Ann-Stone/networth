import request from '@/utils/request'

export function getAllAlarmList() {
  return request({
    url: '/alarm',
    method: 'get'
  })
}

export function getAlarmList(conditions) {
  return request({
    url: '/alarm/query',
    method: 'get',
    params: conditions
  })
}

export function deleteAlarmData(id) {
  return request({
    url: `/alarm/${id}`,
    method: 'delete'
  })
}

export function addAlarmData(data) {
  return request({
    url: '/alarm',
    method: 'post',
    data: data
  })
}

export function updateAlarmData(data) {
  return request({
    url: `/alarm/${data.alarm_id}`,
    method: 'put',
    data: data
  })
}
