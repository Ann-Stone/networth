import {
  getOtherAssetItems
} from '@/api/otherAssets'

export default {
  state: {
    itemList: []
  },
  mutations: {
    SET_OTHER_ASSET_ITEM_LIST: (state, datas) => {
      state.itemList = datas
    }
  },
  actions: {
    GetOtherAssetItems({ commit }) {
      return new Promise((resolve, reject) => {
        getOtherAssetItems()
          .then(response => {
            // response.data.push({
            //   asset_id: null,
            //   asset_name: "負債",
            //   asset_type: "Liability"
            // })
            commit('SET_OTHER_ASSET_ITEM_LIST', response.data)
            resolve()
          })
          .catch(error => {
            reject(error)
          })
      })
    }
  }
}
