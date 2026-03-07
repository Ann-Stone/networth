import request from '@/utils/request'

export function getStockAssetList(asset_id) {
    return request({
        url: `/other-asset/stock/${asset_id}`,
        method: 'get'
    })
}

export function addStockAssetData(data) {
    return request({
        url: '/other-asset/stock',
        method: 'post',
        data: data
    })
}

export function updateStockAssetData(data) {
    return request({
        url: `/other-asset/stock/${data.stock_id}`,
        method: 'put',
        data: data
    })
}

export function deleteStockAssetData(id) {
    return request({
        url: `/other-asset/stock/${id}`,
        method: 'delete'
    })
}

export function getStockDetailList(stock_id) {
    return request({
        url: `/other-asset/stock/detail/${stock_id}`,
        method: 'get'
    })
}

export function addStockDetailData(data) {
    return request({
        url: '/other-asset/stock/detail',
        method: 'post',
        data: data
    })
}

export function updateStockDetailData(data) {
    return request({
        url: `/other-asset/stock/detail/${data.distinct_number}`,
        method: 'put',
        data: data
    })
}

export function deleteStockDetailData(id) {
    return request({
        url: `/other-asset/stock/detail/${id}`,
        method: 'delete'
    })
}
