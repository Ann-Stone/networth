import {
  addLiabilityData,
  addLoanDetailData,
  deleteLiabilityData,
  deleteLoanDetailData,
  getLiabilityById,
  getLiabilityList,
  getLoanDetailList,
  getLoanSelection,
  updateLiabilityData,
  updateLoanDetailData
} from '@/api/otherAssets/liability'

export default {
  state: {
    liabilityContentList: null,
    liabilityDetailList: null,
    loanSelectList: []
  },
  mutations: {
    SET_LOAN_LIST: (state, datas) => {
      state.liabilityContentList = datas
    },
    ADD_LOAN_TO_LIST: (state, data) => {
      state.liabilityContentList.push(data)
    },
    UPDATE_LOAN_LIST: (state, data) => {
      state.liabilityContentList.map(item => {
        if (item.loan_id === data.loan_id) {
          item = Object.assign(item, data)
        }
      })
    },
    SET_LOAN_DETAIL_LIST: (state, datas) => {
      state.liabilityDetailList = datas
    },
    ADD_LOAN_DETAIL_TO_LIST: (state, data) => {
      state.liabilityDetailList.push(data)
    },
    UPDATE_LOAN_DETAIL_LIST: (state, data) => {
      state.liabilityDetailList.map(item => {
        if (item.distinct_number === data.distinct_number) {
          item = Object.assign(item, data)
        }
      })
    },
    SET_LOAN_SELECT_LIST: (state, datas) => {
      state.loanSelectList = datas
    }
  },
  actions: {
    GetLiabilityList({ commit }) {
      return new Promise((resolve, reject) => {
        getLiabilityList()
          .then(response => {
            commit('SET_LOAN_LIST', response.data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    GetLiabilityById({ commit }, loan_id) {
      return new Promise((resolve, reject) => {
        getLiabilityById(loan_id)
          .then(response => {
            resolve(response)
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    AddLiabilityData({ commit, state }, data) {
      return new Promise((resolve, reject) => {
        addLiabilityData(data)
          .then(response => {
            if (state.liabilityContentList) {
              commit('ADD_LOAN_TO_LIST', response.data)
            }
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    UpdateLiabilityData({ commit }, data) {
      return new Promise((resolve, reject) => {
        updateLiabilityData(data)
          .then(() => {
            commit('UPDATE_LOAN_LIST', data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    DeleteLiabilityData({ commit, state }, id) {
      return new Promise((resolve, reject) => {
        deleteLiabilityData(id)
          .then(() => {
            commit(
              'SET_LOAN_LIST',
              state.liabilityContentList.filter(x => {
                return x.liability_id !== id
              })
            )
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    GetLoanDetailList({ commit }, loan_id) {
      return new Promise((resolve, reject) => {
        getLoanDetailList(loan_id)
          .then(response => {
            commit('SET_LOAN_DETAIL_LIST', response.data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    AddLoanDetailData({ commit, state }, data) {
      return new Promise((resolve, reject) => {
        addLoanDetailData(data)
          .then(response => {
            if (state.liabilityDetailList) {
              commit('ADD_LOAN_DETAIL_TO_LIST', response.data)
            }
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    UpdateLoanDetailData({ commit }, data) {
      return new Promise((resolve, reject) => {
        updateLoanDetailData(data)
          .then(() => {
            commit('UPDATE_LOAN_DETAIL_LIST', data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    DeleteLoanDetailData({ commit, state }, id) {
      return new Promise((resolve, reject) => {
        deleteLoanDetailData(id)
          .then(() => {
            commit(
              'SET_LOAN_DETAIL_LIST',
              state.liabilityDetailList.filter(x => {
                return x.distinct_number !== id
              })
            )
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    GetLoanSelection({ commit }) {
      return new Promise((resolve, reject) => {
        getLoanSelection()
          .then(response => {
            commit('SET_LOAN_SELECT_LIST', response.data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    }
  }
}
