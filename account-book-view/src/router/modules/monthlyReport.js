/** When your routing table is too long, you can split it into small modules**/

export default {
  path: '/monthlyReport',
  component: () => import('@/views/layout/Layout'),
  redirect: 'noredirect',
  name: 'MonthlyReport',
  meta: {
    title: '現金流明細',
    icon: 'chart'
  },
  children: [
    {
      path: 'cashFlow',
      component: () => import('@/views/monthlyReport/CashFlow/index'),
      name: 'CashFlow',
      meta: { title: '現金流明細' }
    }
  ]
}
