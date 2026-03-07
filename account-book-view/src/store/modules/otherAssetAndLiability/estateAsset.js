import {
    addEstateAssetData,
    addEstateDetailData,
    deleteEstateAssetData,
    deleteEstateDetailData,
    getEstateAssetList,
    getEstateDetailList,
    updateEstateAssetData,
    updateEstateDetailData
} from '@/api/otherAssets/estate'

export default {
    state: {
        estateContentList: null,
        estateDetailList: null
    },
    mutations: {
        SET_ESTATE_ASSET_LIST: (state, datas) => {
            state.estateContentList = datas
        },
        ADD_ESTATE_ASSET_TO_LIST: (state, data) => {
            state.estateContentList.push(data)
        },
        UPDATE_ESTATE_ASSET_LIST: (state, data) => {
            state.estateContentList.map(item => {
                if (item.estate_id === data.estate_id) {
                    item = Object.assign(item, data)
                }
            })
        },
        SET_ESTATE_DETAIL_LIST: (state, datas) => {
            state.estateDetailList = datas
        },
        ADD_ESTATE_DETAIL_TO_LIST: (state, data) => {
            state.estateDetailList.push(data)
        },
        UPDATE_ESTATE_DETAIL_LIST: (state, data) => {
            state.estateDetailList.map(item => {
                if (item.distinct_number === data.distinct_number) {
                    item = Object.assign(item, data)
                }
            })
        }
    },
    actions: {
        GetEstateAssetList({ commit }, asset_id) {
            return new Promise((resolve, reject) => {
                getEstateAssetList(asset_id)
                    .then(response => {
                        commit('SET_ESTATE_ASSET_LIST', response.data)
                        resolve()
                    })
                    .catch(error => {
                        reject(error)
                    })
            })
        },
        AddEstateAssetData({ commit, state }, data) {
            return new Promise((resolve, reject) => {
                addEstateAssetData(data)
                    .then(response => {
                        if (state.estateContentList) {
                            commit('ADD_ESTATE_ASSET_TO_LIST', response.data)
                        }
                        resolve()
                    })
                    .catch(error => {
                        reject(error)
                    })
            })
        },
        UpdateEstateAssetData({ commit }, data) {
            return new Promise((resolve, reject) => {
                updateEstateAssetData(data)
                    .then(() => {
                        commit('UPDATE_ESTATE_ASSET_LIST', data)
                        resolve()
                    })
                    .catch(error => {
                        reject(error)
                    })
            })
        },
        DeleteEstateAssetData({ commit, state }, id) {
            return new Promise((resolve, reject) => {
                deleteEstateAssetData(id)
                    .then(() => {
                        commit(
                            'SET_ESTATE_ASSET_LIST',
                            state.estateContentList.filter(x => {
                                return x.estate_id !== id
                            })
                        )
                        resolve()
                    })
                    .catch(error => {
                        reject(error)
                    })
            })
        },
        GetEstateDetailList({ commit }, estate_id) {
            return new Promise((resolve, reject) => {
                getEstateDetailList(estate_id)
                    .then(response => {
                        commit('SET_ESTATE_DETAIL_LIST', response.data)
                        resolve()
                    })
                    .catch(error => {
                        reject(error)
                    })
            })
        },
        AddEstateDetailData({ commit, state }, data) {
            return new Promise((resolve, reject) => {
                addEstateDetailData(data)
                    .then(response => {
                        if (state.estateDetailList) {
                            commit('ADD_ESTATE_DETAIL_TO_LIST', response.data)
                        }
                        resolve()
                    })
                    .catch(error => {
                        reject(error)
                    })
            })
        },
        UpdateEstateDetailData({ commit }, data) {
            return new Promise((resolve, reject) => {
                updateEstateDetailData(data)
                    .then(() => {
                        commit('UPDATE_ESTATE_DETAIL_LIST', data)
                        resolve()
                    })
                    .catch(error => {
                        reject(error)
                    })
            })
        },
        DeleteEstateDetailData({ commit, state }, id) {
            return new Promise((resolve, reject) => {
                deleteEstateDetailData(id)
                    .then(() => {
                        commit(
                            'SET_ESTATE_DETAIL_LIST',
                            state.estateDetailList.filter(x => {
                                return x.distinct_number !== id
                            })
                        )
                        resolve()
                    })
                    .catch(error => {
                        reject(error)
                    })
            })
        }
    }
}
