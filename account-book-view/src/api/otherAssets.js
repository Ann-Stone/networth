import request from '@/utils/request'

export function getOtherAssetItems() {
  return request({
    url: '/other-asset/items',
    method: 'get'
  })
}
