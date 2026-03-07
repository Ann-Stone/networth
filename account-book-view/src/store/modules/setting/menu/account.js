import {
  addAccountData,
  deleteAccountData,
  getAccountList,
  getAccountSelection,
  updateAccountData
} from '@/api/setting/menu/account'

export default {
  state: {
    dataList: null,
    accountSelectList: []
  },
  mutations: {
    SET_ACCOUNT_DATA_LIST: (state, datas) => {
      state.dataList = datas
    },
    ADD_ACCOUNT_DATA_TO_LIST: (state, data) => {
      state.dataList.push(data)
    },
    UPDATE_ACCOUNT_DATA_LIST: (state, data) => {
      state.dataList.map(item => {
        if (item.account_id === data.account_id) {
          item = Object.assign(item, data)
        }
      })
    },
    SET_ACCOUNT_SELECT_LIST: (state, datas) => {
      state.accountSelectList = datas
    }
  },
  actions: {
    GetAccountList({ commit }, conditions) {
      return new Promise((resolve, reject) => {
        getAccountList(conditions)
          .then(response => {
            commit('SET_ACCOUNT_DATA_LIST', response.data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    DeleteAccountData({ commit, state }, id) {
      return new Promise((resolve, reject) => {
        deleteAccountData(id)
          .then(() => {
            commit(
              'SET_ACCOUNT_DATA_LIST',
              state.dataList.filter(x => {
                return x.account_id !== id
              })
            )
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    AddAccountData({ commit, state }, data) {
      return new Promise((resolve, reject) => {
        addAccountData(data)
          .then(response => {
            if (state.dataList) {
              commit('ADD_ACCOUNT_DATA_TO_LIST', response.data)
            }
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    UpdateAccountData({ commit }, data) {
      return new Promise((resolve, reject) => {
        updateAccountData(data)
          .then(() => {
            commit('UPDATE_ACCOUNT_DATA_LIST', data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    GetAccountSelection({ commit }) {
      return new Promise((resolve, reject) => {
        getAccountSelection()
          .then(response => {
            commit('SET_ACCOUNT_SELECT_LIST', response.data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    }
  }
}
