import request from '@/utils/request'

export function getInsuranceAssetList(asset_id) {
    return request({
        url: `/other-asset/insurance/${asset_id}`,
        method: 'get'
    })
}

export function addInsuranceAssetData(data) {
    return request({
        url: '/other-asset/insurance',
        method: 'post',
        data: data
    })
}

export function updateInsuranceAssetData(data) {
    return request({
        url: `/other-asset/insurance/${data.insurance_id}`,
        method: 'put',
        data: data
    })
}

export function deleteInsuranceAssetData(id) {
    return request({
        url: `/other-asset/insurance/${id}`,
        method: 'delete'
    })
}

export function getInsuranceDetailList(insurance_id) {
    return request({
        url: `/other-asset/insurance/detail/${insurance_id}`,
        method: 'get'
    })
}

export function addInsuranceDetailData(data) {
    return request({
        url: '/other-asset/insurance/detail',
        method: 'post',
        data: data
    })
}

export function updateInsuranceDetailData(data) {
    return request({
        url: `/other-asset/insurance/detail/${data.distinct_number}`,
        method: 'put',
        data: data
    })
}

export function deleteInsuranceDetailData(id) {
    return request({
        url: `/other-asset/insurance/detail/${id}`,
        method: 'delete'
    })
}
