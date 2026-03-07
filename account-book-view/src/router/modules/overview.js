/** When your routing table is too long, you can split it into small modules**/

export default {
  path: '/overview',
  component: () => import('@/views/layout/Layout'),
  redirect: 'noredirect',
  name: 'Overview',
  meta: {
    title: '財務狀況一覽',
    icon: 'clipboard'
  },
  children: [
    {
      path: 'balanceSheet',
      component: () => import('@/views/yearReport/BalanceSheet/index'),
      name: 'BalanceSheet',
      meta: { title: '資產負債表' }
    },
    {
      path: 'spendings',
      component: () => import('@/views/yearReport/Spending/index'),
      name: 'Spendings',
      meta: { title: '收支一覽' }
    },
    {
      path: 'assets',
      component: () => import('@/views//yearReport/Asset/index'),
      name: 'AssetOverview',
      meta: { title: '資產一覽' }
    }
  ]
}
