import {
  bulkInsertBudget,
  getBudgetList,
  getBudgetRange,
  updateBudgetData
} from '@/api/setting/budget'

export default {
  state: {
    yearRange: {
      max: 0,
      min: 0
    },
    dataList: {
      floatingList: null,
      stableList: null
    }
  },
  mutations: {
    SET_YEAR_RANGE: (state, data) => {
      state.yearRange = data
    },
    SET_BUDGET_DATA_LIST: (state, datas) => {
      state.dataList.floatingList = datas.filter(
        x => x.code_type === 'Floating'
      )
      state.dataList.stableList = datas.filter(x => x.code_type === 'Fixed')
    }
  },
  actions: {
    GetBudgetRange({ commit }) {
      return new Promise((resolve, reject) => {
        getBudgetRange()
          .then(response => {
            commit('SET_YEAR_RANGE', response.data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    GetBudgetList({ commit }, thisYear) {
      return new Promise((resolve, reject) => {
        getBudgetList(thisYear)
          .then(response => {
            commit('SET_BUDGET_DATA_LIST', response.data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    UpdateBudgetData({ commit }, datas) {
      return new Promise((resolve, reject) => {
        updateBudgetData(datas)
          .then(() => {
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    BulkInsertBudget({ dispatch }, next_year) {
      return new Promise((resolve, reject) => {
        bulkInsertBudget(next_year)
          .then(() => {
            dispatch('GetBudgetRange')
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    }
  }
}
