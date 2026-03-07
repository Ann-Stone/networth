import request from '@/utils/request'

export function checkServerAlive() {
  return request({
    url: '/global/server-alive',
    method: 'get'
  })
}

export function checkData({ type, data = { period: '' } }) {
  return request({
    url: `/global/check/${type}`,
    method: 'post',
    data
  })
}
