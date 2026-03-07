import store from '@/store'

import { accountType } from '@/assets/commonData/accountData'
import { codeType } from '@/assets/commonData/codeData'
import { feedbackWay } from '@/assets/commonData/creditCardData'
import { fxCode } from '@/assets/commonData/fxData'
import { assetType, otherAssetType, yesNo } from '@/assets/commonData/global'
import { loanType, loanExecuteType } from '@/assets/commonData/liability'
import {
  insuranceExcuteType,
  insurancePayType,
  stockExcuteType,
  estateStatus,
  estateExcuteType,
  estateType
} from '@/assets/commonData/otherAssets'

export function getMappingName(type, inputCode) {
  let target = null

  switch (type) {
    case 'account':
      target = store.state.setting.menu.account.accountSelectList
      break
    case 'account_type':
      target = accountType
      break
    case 'asset_type':
      target = otherAssetType
      break
    case 'code_type':
      target = codeType
      break
    case 'estate_excute_type':
      target = estateExcuteType
      break
    case 'estate_status':
      target = estateStatus
      break
    case 'estate_type':
      target = estateType
      break
    case 'excute_type':
      target = stockExcuteType
      break
    case 'feedback_way':
      target = feedbackWay
      break
    case 'fx_code':
      target = fxCode
      break
    case 'initial_type':
      target = assetType
      break
    case 'insurance_excute_type':
      target = insuranceExcuteType
      break
    case 'pay_type':
      target = insurancePayType
      break
    case 'loan_type':
      target = loanType
      break
    case 'loan_excute_type':
      target = loanExecuteType
      break
    case 'yes_no':
      target = yesNo
      break

    default:
      return inputCode
  }

  const data = target.find(x => x.key === inputCode)

  if (data) return data.value

  return inputCode
}
