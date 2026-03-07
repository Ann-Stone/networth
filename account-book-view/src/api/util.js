import request from '@/utils/request'

export function getWalletSelectionGroups() {
  return request({
    url: '/util/wallet-selection-group',
    method: 'get'
  })
}

export function getCreditCardSelectionGroups() {
  return request({
    url: '/util/credit-card-selection-group',
    method: 'get'
  })
}

export function getLoanSelectionGroups() {
  return request({
    url: '/util/loan-selection-group',
    method: 'get'
  })
}

export function getInsuranceSelectionGroups() {
  return request({
    url: '/util/insurance-selection-group',
    method: 'get'
  })
}

export function getCodeSelectionGroups() {
  return request({
    url: '/util/code-selection-group',
    method: 'get'
  })
}

export async function getSubCodeSelectionGroups(parent_id) {
  return await request({
    url: `/util/code-selection-group/${parent_id}`,
    method: 'get'
  })
}
