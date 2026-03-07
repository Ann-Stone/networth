import moment from 'moment'

import {
  addAlarmData,
  deleteAlarmData,
  getAlarmList,
  getAllAlarmList,
  updateAlarmData
} from '@/api/setting/alarm'

export default {
  state: {
    dataList: null
  },
  mutations: {
    SET_ALARM_DATA_LIST: (state, datas) => {
      state.dataList = datas
    },
    ADD_ALARM_DATA_TO_LIST: (state, data) => {
      state.dataList.push(data)
    },
    UPDATE_ALARM_DATA_LIST: (state, data) => {
      state.dataList.map(item => {
        if (item.alarm_id === data.alarm_id) {
          if (data.due_date) {
            data.due_date = moment(data.due_date).format('YYYY-MM-DD')
          }
          item = Object.assign(item, data)
        }
      })
    }
  },
  actions: {
    GetAlarmList({ commit }, conditions) {
      return new Promise((resolve, reject) => {
        let result = null
        if (conditions) {
          result = getAlarmList(conditions)
        } else {
          result = getAllAlarmList()
        }

        result
          .then(response => {
            commit('SET_ALARM_DATA_LIST', response.data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    DeleteAlarmData({ commit, state }, id) {
      return new Promise((resolve, reject) => {
        deleteAlarmData(id)
          .then(() => {
            commit(
              'SET_ALARM_DATA_LIST',
              state.dataList.filter(x => {
                return x.alarm_id !== id
              })
            )
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    AddAlarmData({ commit, state }, data) {
      return new Promise((resolve, reject) => {
        addAlarmData(data)
          .then(response => {
            if (state.dataList) {
              commit('ADD_ALARM_DATA_TO_LIST', response.data)
            }
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    },
    UpdateAlarmData({ commit }, data) {
      return new Promise((resolve, reject) => {
        updateAlarmData(data)
          .then(() => {
            commit('UPDATE_ALARM_DATA_LIST', data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    }
  }
}
