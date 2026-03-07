// import Cookies from 'js-cookie'
import moment from 'moment'

// moment.tz.setDefault(Intl.DateTimeFormat().resolvedOptions().timeZone)
moment.suppressDeprecationWarnings = true

export function formatDateTimeSlash(input, format = 'YYYY-MM-DD') {
  // moment.locale(Cookies.get('Accept-Language'))
  if (input) {
    // console.log(moment.utc('2020-04-17 05:20:37').fromNow())
    if (moment(input)._pf.iso) {
      return moment(`${input} UTC`).format(format)
    } else return moment(input).format(format)
  }
  return ''
}
