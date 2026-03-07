import {
  addJournalData,
  addStockPrice,
  deleteJournalData,
  getAllSubCodeList,
  getExpenditureBudgetByVestingMonth,
  getExpenditureRatioByVestingMonth,
  getInvestRatioByVestingMonth,
  getJournalListByVestingMonth,
  getLiabilitiesByVestingMonth,
  getStockPriceList,
  setMonthlySummary,
  updateJournalData
} from '@/api/monthlyReport/cashFlow'

export default {
  state: {
    journalDataList: null
  },
  mutations: {
    SET_JOURNAL_DATA_LIST: (state, datas) => {
      state.journalDataList = datas
    },
    ADD_JOURNAL_DATA_TO_LIST: (state, data) => {
      state.journalDataList.push(data)
    },
    UPDATE_JOURNAL_DATA_LIST: (state, data) => {
      state.journalDataList.map(item => {
        if (item.distinct_number === data.distinct_number) {
          data.isEditMode = false
          item = Object.assign(item, data)
        }
      })
    }
  },
  actions: {
    GetJournalListByVestingMonth({ commit }, vestingMonth) {
      return new Promise((resolve, reject) => {
        getJournalListByVestingMonth(vestingMonth)
          .then(response => {
            commit('SET_JOURNAL_DATA_LIST', response.data.journalList)
            resolve(response.data.gainLoss)
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    DeleteJournalData({ commit, state }, id) {
      return new Promise((resolve, reject) => {
        deleteJournalData(id)
          .then(() => {
            commit(
              'SET_JOURNAL_DATA_LIST',
              state.journalDataList.filter(x => {
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
    AddJournalData({ commit, state }, data) {
      return new Promise((resolve, reject) => {
        addJournalData(data)
          .then(response => {
            if (state.journalDataList) {
              commit('ADD_JOURNAL_DATA_TO_LIST', response.data)
            }
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    UpdateJournalData({ commit }, data) {
      return new Promise((resolve, reject) => {
        updateJournalData(data)
          .then(() => {
            commit('UPDATE_JOURNAL_DATA_LIST', data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    SetMonthlySummary({ commit }, vestingMonth) {
      return new Promise((resolve, reject) => {
        setMonthlySummary(vestingMonth)
          .then(() => {
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    GetExpenditureRatioByVestingMonth({ commit }, vestingMonth) {
      return getExpenditureRatioByVestingMonth(vestingMonth)
    },
    GetInvestRatioByVestingMonth({ commit }, vestingMonth) {
      return getInvestRatioByVestingMonth(vestingMonth)
    },
    GetExpenditureBudgetByVestingMonth({ commit }, vestingMonth) {
      return getExpenditureBudgetByVestingMonth(vestingMonth)
    },
    GetLiabilitiesByVestingMonth({ commit }, vestingMonth) {
      return getLiabilitiesByVestingMonth(vestingMonth)
    },
    GetAllSubCodeList({ commit }) {
      return getAllSubCodeList()
    },
    GetStockPriceList({ commit }, vestingMonth) {
      return getStockPriceList(vestingMonth)
    },
    AddStockPrice({ commit }, data) {
      return new Promise((resolve, reject) => {
        addStockPrice(data)
          .then(() => {
            resolve(true)
          })
          .catch(error => {
            reject(error)
          })
      })
    }
  }
}
