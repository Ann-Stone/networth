import {
  addInitialData,
  deleteInitialData,
  getInitialList,
  updateInitialData
} from '@/api/setting/initial'

export default {
  state: {
    dataList: null
  },
  mutations: {
    SET_INITIAL_DATA_LIST: (state, datas) => {
      state.dataList = datas
    },
    ADD_INITIAL_DATA_TO_LIST: (state, data) => {
      state.dataList.push(data)
    }
  },
  actions: {
    GetInitialList({ commit }, conditions) {
      return new Promise((resolve, reject) => {
        getInitialList(conditions)
          .then(response => {
            commit('SET_INITIAL_DATA_LIST', response.data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    DeleteInitialData({ commit, state }, data) {
      return new Promise((resolve, reject) => {
        deleteInitialData(data)
          .then(() => {
            commit(
              'SET_INITIAL_DATA_LIST',
              state.dataList.filter(x => {
                return !(
                  x.code_id === data.code_id &&
                  x.initial_type === data.initial_type
                )
              })
            )
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    AddInitialData({ commit, state }, data) {
      return new Promise((resolve, reject) => {
        addInitialData(data)
          .then(response => {
            if (state.dataList) {
              commit('ADD_INITIAL_DATA_TO_LIST', response.data)
            }
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    UpdateInitialData({ commit }, datas) {
      return new Promise((resolve, reject) => {
        updateInitialData(datas)
          .then(() => {
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    }
  }
}
