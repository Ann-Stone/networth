import {
  addInsuranceAssetData,
  addInsuranceDetailData,
  deleteInsuranceAssetData,
  deleteInsuranceDetailData,
  getInsuranceAssetList,
  getInsuranceDetailList,
  updateInsuranceAssetData,
  updateInsuranceDetailData
} from '@/api/otherAssets/insurance'

export default {
  state: {
    insuranceContentList: null,
    insuranceDetailList: null
  },
  mutations: {
    SET_INSURANCE_ASSET_LIST: (state, datas) => {
      state.insuranceContentList = datas
    },
    ADD_INSURANCE_ASSET_TO_LIST: (state, data) => {
      state.insuranceContentList.push(data)
    },
    UPDATE_INSURANCE_ASSET_LIST: (state, data) => {
      state.insuranceContentList.map(item => {
        if (item.insurance_id === data.insurance_id) {
          item = Object.assign(item, data)
        }
      })
    },
    SET_INSURANCE_DETAIL_LIST: (state, datas) => {
      state.insuranceDetailList = datas
    },
    ADD_INSURANCE_DETAIL_TO_LIST: (state, data) => {
      state.insuranceDetailList.push(data)
    },
    UPDATE_INSURANCE_DETAIL_LIST: (state, data) => {
      state.insuranceDetailList.map(item => {
        if (item.distinct_number === data.distinct_number) {
          item = Object.assign(item, data)
        }
      })
    }
  },
  actions: {
    GetInsurenceAssetList({ commit }, asset_id) {
      return new Promise((resolve, reject) => {
        getInsuranceAssetList(asset_id)
          .then(response => {
            commit('SET_INSURANCE_ASSET_LIST', response.data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    AddInsuranceAssetData({ commit, state }, data) {
      return new Promise((resolve, reject) => {
        addInsuranceAssetData(data)
          .then(response => {
            if (state.insuranceContentList) {
              commit('ADD_INSURANCE_ASSET_TO_LIST', response.data)
            }
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    UpdateInsuranceAssetData({ commit }, data) {
      return new Promise((resolve, reject) => {
        updateInsuranceAssetData(data)
          .then(() => {
            commit('UPDATE_INSURANCE_ASSET_LIST', data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    DeleteInsuranceAssetData({ commit, state }, id) {
      return new Promise((resolve, reject) => {
        deleteInsuranceAssetData(id)
          .then(() => {
            commit(
              'SET_INSURANCE_ASSET_LIST',
              state.insuranceContentList.filter(x => {
                return x.insurance_id !== id
              })
            )
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    GetInsuranceDetailList({ commit }, insurance_id) {
      return new Promise((resolve, reject) => {
        getInsuranceDetailList(insurance_id)
          .then(response => {
            commit('SET_INSURANCE_DETAIL_LIST', response.data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    AddInsuranceDetailData({ commit, state }, data) {
      return new Promise((resolve, reject) => {
        addInsuranceDetailData(data)
          .then(response => {
            if (state.insuranceDetailList) {
              commit('ADD_INSURANCE_DETAIL_TO_LIST', response.data)
            }
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    UpdateInsuranceDetailData({ commit }, data) {
      return new Promise((resolve, reject) => {
        updateInsuranceDetailData(data)
          .then(() => {
            commit('UPDATE_INSURANCE_DETAIL_LIST', data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    DeleteInsuranceDetailData({ commit, state }, id) {
      return new Promise((resolve, reject) => {
        deleteInsuranceDetailData(id)
          .then(() => {
            commit(
              'SET_INSURANCE_DETAIL_LIST',
              state.insuranceDetailList.filter(x => {
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
