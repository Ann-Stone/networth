/** When your routing table is too long, you can split it into small modules**/

export default {
  path: '/otherAssets',
  component: () => import('@/views/layout/Layout'),
  redirect: 'noredirect',
  name: 'OtherAssets',
  meta: {
    title: '其他資產/負債',
    icon: 'tab'
  },
  children: [
    {
      path: '',
      component: () => import('@/views/otherAssetAndLiabilities/index'),
      name: 'OtherAssetsDetail',
      meta: { title: '其他資產/負債', icon: 'tab' }
    }
  ]
}
