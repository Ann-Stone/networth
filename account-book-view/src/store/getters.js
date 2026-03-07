const getters = {
  errorLogs: state => state.errorLog.logs,
  permission_routers: state => state.permission.routers,
  sidebar: state => state.app.sidebar
}
export default getters
