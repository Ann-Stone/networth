import {
  addLoanData,
  deleteLoanData,
  getLoanList,
  updateLoanData
} from '@/api/setting/menu/loan'

export default {
  state: {
    dataList: null
  },
  mutations: {
    SET_LOAN_DATA_LIST: (state, datas) => {
      state.dataList = datas
    },
    ADD_LOAN_DATA_TO_LIST: (state, data) => {
      state.dataList.push(data)
    },
    UPDATE_LOAN_DATA_LIST: (state, data) => {
      state.dataList.map(item => {
        if (item.loan_id === data.loan_id) {
          item = Object.assign(item, data)
        }
      })
    }
  },
  actions: {
    GetLoanList({ commit }) {
      return new Promise((resolve, reject) => {
        getLoanList()
          .then(response => {
            commit('SET_LOAN_DATA_LIST', response.data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    AddLoanData({ commit, state }, data) {
      return new Promise((resolve, reject) => {
        addLoanData(data)
          .then(response => {
            if (state.dataList) {
              commit('ADD_LOAN_DATA_TO_LIST', response.data)
            }
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    UpdateLoanData({ commit }, data) {
      return new Promise((resolve, reject) => {
        updateLoanData(data)
          .then(() => {
            commit('UPDATE_LOAN_DATA_LIST', data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    DeleteLoanData({ commit, state }, id) {
      return new Promise((resolve, reject) => {
        deleteLoanData(id)
          .then(() => {
            commit(
              'SET_LOAN_DATA_LIST',
              state.dataList.filter(x => {
                return x.loan_id !== id
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
