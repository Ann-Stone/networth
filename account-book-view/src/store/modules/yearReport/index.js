import {
    getAssetList,
    getBalanceList,
    getSpendingList
} from '@/api/yearReport/balance'

export default {
    state: {
    },
    mutations: {
    },
    actions: {
        GetBalanceList({ commit }) {
            return getBalanceList()
        },
        GetSpendingList({ commit }, conditions) {
            return getSpendingList(conditions)
        },
        GetAssetList({ commit }) {
            return getAssetList()
        }
    }
}
