import {
  addStockAssetData,
  addStockDetailData,
  deleteStockAssetData,
  deleteStockDetailData,
  getStockAssetList,
  getStockDetailList,
  updateStockAssetData,
  updateStockDetailData
} from '@/api/otherAssets/stock'

export default {
  state: {
    stockContentList: null,
    stockDetailList: null
  },
  mutations: {
    SET_STOCK_ASSET_LIST: (state, datas) => {
      state.stockContentList = datas
    },
    ADD_STOCK_ASSET_TO_LIST: (state, data) => {
      state.stockContentList.push(data)
    },
    UPDATE_STOCK_ASSET_LIST: (state, data) => {
      state.stockContentList.map(item => {
        if (item.stock_id === data.stock_id) {
          item = Object.assign(item, data)
        }
      })
    },
    SET_STOCK_DETAIL_LIST: (state, datas) => {
      state.stockDetailList = datas
    },
    ADD_STOCK_DETAIL_TO_LIST: (state, data) => {
      state.stockDetailList.push(data)
    },
    UPDATE_STOCK_DETAIL_LIST: (state, data) => {
      state.stockDetailList.map(item => {
        if (item.distinct_number === data.distinct_number) {
          item = Object.assign(item, data)
        }
      })
    }
  },
  actions: {
    GetStockAssetList({ commit }, asset_id) {
      return new Promise((resolve, reject) => {
        getStockAssetList(asset_id)
          .then(response => {
            commit('SET_STOCK_ASSET_LIST', response.data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    AddStockAssetData({ commit, state }, data) {
      return new Promise((resolve, reject) => {
        addStockAssetData(data)
          .then(response => {
            if (state.stockContentList) {
              commit('ADD_STOCK_ASSET_TO_LIST', response.data)
            }
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    UpdateStockAssetData({ commit }, data) {
      return new Promise((resolve, reject) => {
        updateStockAssetData(data)
          .then(() => {
            commit('UPDATE_STOCK_ASSET_LIST', data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    DeleteStockAssetData({ commit, state }, id) {
      return new Promise((resolve, reject) => {
        deleteStockAssetData(id)
          .then(() => {
            commit(
              'SET_STOCK_ASSET_LIST',
              state.stockContentList.filter(x => {
                return x.stock_id !== id
              })
            )
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    GetStockDetailList({ commit }, stock_id) {
      return new Promise((resolve, reject) => {
        getStockDetailList(stock_id)
          .then(response => {
            commit('SET_STOCK_DETAIL_LIST', response.data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    AddStockDetailData({ commit, state }, data) {
      return new Promise((resolve, reject) => {
        addStockDetailData(data)
          .then(response => {
            if (state.stockDetailList) {
              commit('ADD_STOCK_DETAIL_TO_LIST', response.data)
            }
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    UpdateStockDetailData({ commit }, data) {
      return new Promise((resolve, reject) => {
        updateStockDetailData(data)
          .then(() => {
            commit('UPDATE_STOCK_DETAIL_LIST', data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    DeleteStockDetailData({ commit, state }, id) {
      return new Promise((resolve, reject) => {
        deleteStockDetailData(id)
          .then(() => {
            commit(
              'SET_STOCK_DETAIL_LIST',
              state.stockDetailList.filter(x => {
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
