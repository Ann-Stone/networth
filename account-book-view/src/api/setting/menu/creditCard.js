import request from '@/utils/request'

export function getCreditCardList(conditions) {
  return request({
    url: '/credit-card/query',
    method: 'get',
    params: conditions
  })
}

export function addCreditCardData(data) {
  return request({
    url: '/credit-card',
    method: 'post',
    data: data
  })
}

export function updateCreditCardData(data) {
  return request({
    url: `/credit-card/${data.credit_card_id}`,
    method: 'put',
    data: data
  })
}

export function deleteCreditCardData(id) {
  return request({
    url: `/credit-card/${id}`,
    method: 'delete'
  })
}
