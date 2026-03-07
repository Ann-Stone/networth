import router from './router'
import store from './store'
import NProgress from 'nprogress' // progress bar
import 'nprogress/nprogress.css' // progress bar style

NProgress.configure({ showSpinner: false }) // NProgress Configuration

const whiteList = ['/404', '/401'] // no need to check alive

router.beforeEach((to, from, next) => {
  NProgress.start() // start progress bar

  if (whiteList.indexOf(to.path) === -1) {
    // 確認 server 還活著
    store
      .dispatch('CheckServerAlive')
      .then(response => {
        if (response) {
          if (store.getters.permission_routers.length === 0) {
            store.dispatch('GenerateRoutes')
          }

          next()
        } else {
          next({ path: '/401', replace: true, query: { noGoBack: true } })
        }
      })
      .catch(() => {
        next({ path: '/404', replace: true, query: { noGoBack: true } })
      })
  }

  next()
})

router.afterEach(() => {
  NProgress.done() // finish progress bar
})
