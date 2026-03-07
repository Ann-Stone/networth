import axios from 'axios'
import { Message, Notification } from 'element-ui'

// create an axios instance
const service = axios.create({
  baseURL: process.env.BASE_API, // api 的 base_url
  timeout: 5000 // request timeout
})

// request interceptor
service.interceptors.request.use(
  config => config,
  error => {
    // Do something with request error
    console.log(error) // for debug
    Promise.reject(error)
  }
)

// response interceptor
service.interceptors.response.use(
  response => {
    const respBody = response.data
    // -- Server 回传成功
    if (respBody.status === 1) {
      return respBody
    } else {
      Notification({
        message: respBody.msg, // + ' ' + respBody.error,
        type: 'error',
        duration: 5 * 1000
      })
      return new Promise((resolve, reject) => {
        reject(respBody.msg)
      })
    }
    // 回傳下載檔案
    // if (response.headers['content-type'] && response.headers['content-type'].includes('text/csv')) {
    //   new ExportFile(respBody)
    //   return
    // }
  },
  error => {
    console.log('err' + error) // for debug
    Message({
      message: error.message,
      type: 'error',
      duration: 5 * 1000
    })
    return Promise.reject(error)
  }
)

export default service
