import request from '@/utils/request'

export function getOtherAssetsList() {
  return request({
    url: '/other-asset/query',
    method: 'get'
  })
}

export function addOtherAssetsData(data) {
  return request({
    url: '/other-asset',
    method: 'post',
    data: data
  })
}

export function updateOtherAssetsData(data) {
  return request({
    url: `/other-asset/${data.asset_id}`,
    method: 'put',
    data: data
  })
}

export function deleteOtherAssetsData(id) {
  return request({
    url: `/other-asset/${id}`,
    method: 'delete'
  })
}
