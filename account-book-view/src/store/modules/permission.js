import { constantRouterMap } from '@/router'

const permission = {
  state: {
    routers: []
  },
  mutations: {
    SET_ROUTERS: (state) => {
      state.routers = constantRouterMap
    }
  },
  actions: {
    GenerateRoutes({ commit }) {
      return new Promise(resolve => {
        commit('SET_ROUTERS')
        resolve()
      })
    }
  }
}

export default permission
