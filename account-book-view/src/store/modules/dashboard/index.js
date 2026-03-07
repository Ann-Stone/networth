import {
    addTarget,
    deleteTarget,
    getAlarmList,
    getBudgetUsed,
    getSummary,
    getTargetList,
    getGiftedList,
    updateTarget
} from '@/api/dashboard'

export default {
    state: {
    },
    mutations: {
    },
    actions: {
        GetDashboardSummary({ commit }, conditions) {
            return getSummary(conditions)
        },
        GetBudgetUsed({ commit }, conditions) {
            return getBudgetUsed(conditions)
        },
        GetSummaryAlarmList({ commit }) {
            return getAlarmList()
        },
        GetGiftedList({ commit }, year) {
            return getGiftedList(year)
        },
        GetTargetList({ commit }) {
            return getTargetList()
        },
        AddTarget({ commit }, data) {
            return addTarget(data)
        },
        UpdateTarget({ commit }, data) {
            return updateTarget(data)
        },
        DeleteTarget({ commit }, id) {
            return deleteTarget(id)
        }
    }
}
