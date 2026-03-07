import {
  addCreditCardData,
  deleteCreditCardData,
  getCreditCardList,
  updateCreditCardData
} from '@/api/setting/menu/creditCard'

export default {
  state: {
    dataList: null
  },
  mutations: {
    SET_CREDIT_CARD_DATA_LIST: (state, datas) => {
      state.dataList = datas
    },
    ADD_CREDIT_CARD_DATA_TO_LIST: (state, data) => {
      state.dataList.push(data)
    },
    UPDATE_CREDIT_CARD_DATA_LIST: (state, data) => {
      state.dataList.map(item => {
        if (item.credit_card_id === data.credit_card_id) {
          item = Object.assign(item, data)
        }
      })
    }
  },
  actions: {
    GetCreditCardList({ commit }, conditions) {
      return new Promise((resolve, reject) => {
        getCreditCardList(conditions)
          .then(response => {
            commit('SET_CREDIT_CARD_DATA_LIST', response.data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    AddCreditCardData({ commit, state }, data) {
      return new Promise((resolve, reject) => {
        addCreditCardData(data)
          .then(response => {
            if (state.dataList) {
              commit('ADD_CREDIT_CARD_DATA_TO_LIST', response.data)
            }
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    UpdateCreditCardData({ commit }, data) {
      return new Promise((resolve, reject) => {
        updateCreditCardData(data)
          .then(() => {
            commit('UPDATE_CREDIT_CARD_DATA_LIST', data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    DeleteCreditCardData({ commit, state }, id) {
      return new Promise((resolve, reject) => {
        deleteCreditCardData(id)
          .then(() => {
            commit(
              'SET_CREDIT_CARD_DATA_LIST',
              state.dataList.filter(x => {
                return x.credit_card_id !== id
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
