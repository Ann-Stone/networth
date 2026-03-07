import {
  addOtherAssetsData,
  deleteOtherAssetsData,
  getOtherAssetsList,
  updateOtherAssetsData
} from '@/api/setting/menu/otherAssets'

export default {
  state: {
    dataList: null
  },
  mutations: {
    SET_OTHER_ASSETS_DATA_LIST: (state, datas) => {
      state.dataList = datas
    },
    ADD_OTHER_ASSETS_DATA_TO_LIST: (state, data) => {
      state.dataList.push(data)
    },
    UPDATE_OTHER_ASSETS_DATA_LIST: (state, data) => {
      state.dataList.map(item => {
        if (item.asset_id === data.asset_id) {
          item = Object.assign(item, data)
        }
      })
    }
  },
  actions: {
    GetOtherAssetsList({ commit }) {
      return new Promise((resolve, reject) => {
        getOtherAssetsList()
          .then(response => {
            commit('SET_OTHER_ASSETS_DATA_LIST', response.data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    AddOtherAssetData({ commit, state }, data) {
      return new Promise((resolve, reject) => {
        addOtherAssetsData(data)
          .then(response => {
            if (state.dataList) {
              commit('ADD_OTHER_ASSETS_DATA_TO_LIST', response.data)
            }
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    UpdateOtherAssetData({ commit }, data) {
      return new Promise((resolve, reject) => {
        updateOtherAssetsData(data)
          .then(() => {
            commit('UPDATE_OTHER_ASSETS_DATA_LIST', data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    DeleteOtherAssetData({ commit, state }, id) {
      return new Promise((resolve, reject) => {
        deleteOtherAssetsData(id)
          .then(() => {
            commit(
              'SET_OTHER_ASSETS_DATA_LIST',
              state.dataList.filter(x => {
                return x.asset_id !== id
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
