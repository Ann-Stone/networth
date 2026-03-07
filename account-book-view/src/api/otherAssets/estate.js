import request from '@/utils/request'

export function getEstateAssetList(asset_id) {
    return request({
        url: `/other-asset/estate/${asset_id}`,
        method: 'get'
    })
}

export function addEstateAssetData(data) {
    return request({
        url: '/other-asset/estate',
        method: 'post',
        data: data
    })
}

export function updateEstateAssetData(data) {
    return request({
        url: `/other-asset/estate/${data.estate_id}`,
        method: 'put',
        data: data
    })
}

export function deleteEstateAssetData(id) {
    return request({
        url: `/other-asset/estate/${id}`,
        method: 'delete'
    })
}

export function getEstateDetailList(estate_id) {
    return request({
        url: `/other-asset/estate/detail/${estate_id}`,
        method: 'get'
    })
}

export function addEstateDetailData(data) {
    return request({
        url: '/other-asset/estate/detail',
        method: 'post',
        data: data
    })
}

export function updateEstateDetailData(data) {
    return request({
        url: `/other-asset/estate/detail/${data.distinct_number}`,
        method: 'put',
        data: data
    })
}

export function deleteEstateDetailData(id) {
    return request({
        url: `/other-asset/estate/detail/${id}`,
        method: 'delete'
    })
}
